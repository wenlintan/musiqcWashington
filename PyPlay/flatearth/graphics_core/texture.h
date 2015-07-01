#ifndef BITMAP__H
#define BITMAP__H

#include "stdafx.h"
#include "resource.h"

#include <cstdio>
#include <sstream>

class Renderer;

class Color: public State
{
public:
	Color(): State(Resource::FLAT_COLOR), Alpha(255)
	{}

	Color( const Vector3ub& color ): State(Resource::FLAT_COLOR), RawColor(color), Alpha(255)
	{}

	Color( const Vector3ub& color, uchar alpha ): State(Resource::FLAT_COLOR), RawColor(color), Alpha( alpha )
	{}

	Vector3ub	RawColor;
	uchar		Alpha;
};

//assistance from gamedev article by Mark Bernard
const short BITMAP_MAGIC_NUMBER=19778;

#pragma pack(push,bitmap_data,1)

typedef struct tagRGBQuad {
	char rgbBlue;
	char rgbGreen;
	char rgbRed;
	char rgbReserved;
} RGBQuad;

typedef struct tagBitmapFileHeader {
	unsigned short bfType;
	unsigned int bfSize;
	unsigned short bfReserved1;
	unsigned short bfReserved2;
	unsigned int bfOffBits;
} BitmapFileHeader;

typedef struct tagBitmapInfoHeader {
	unsigned int biSize;
	int biWidth;
	int biHeight;
	unsigned short biPlanes;
	unsigned short biBitCount;
	unsigned int biCompression;
	unsigned int biSizeImage;
	int biXPelsPerMeter;
	int biYPelsPerMeter;
	unsigned int biClrUsed;
	unsigned int biClrImportant;
} BitmapInfoHeader;

#pragma pack(pop,bitmap_data)

class Texture: public State
{
public:

	//loaded data should be converted to this masking
	const static uint RMASK = 0x0000ff;
	const static uint GMASK = 0x00ff00;
	const static uint BMASK = 0xff0000;
	const static uint AMASK = 0x000000;

	string			Name;

    unsigned char*	PixelData;
    long			Width;
	long			Height;
    ushort			Bpp;
	uint			PixelDataSize;

	Texture(): State(Resource::TEXTURE), PixelData(NULL), Width(0), Height(0), Bpp(0), PixelDataSize(0)
	{}

	Texture( const string& file ): State(Resource::TEXTURE), PixelData(NULL), Width(0), Height(0), Bpp(0), PixelDataSize(0)
	{
		if( !initialize( file ) )
			throw g5Exception("Texture", "Could not load texture data", true);
	}

	Texture::~Texture()
	{
		shutdown();
	}

	virtual bool initialize( const string& file );
	virtual bool save( const string& file );
	virtual void shutdown();

	void reverse_data();
	bool is_valid()					{ return PixelData != NULL; }

private:
	BitmapFileHeader	_FileHeader;
	BitmapInfoHeader	_InfoHeader;

};

class DataTexture: public Texture {
public:

	enum DataType { FLOAT };
	enum Precision { COLOR, FLOAT16, FLOAT32 };

	template< typename ValueType >
	DataTexture( DataType type, Precision prec, const vector<ValueType>& data, uint ncomponents, uint width ): 
			Type( type ), Data( data ), Prec( prec ), Size( data.size() ), NComponents( ncomponents ), Width( width )
	{ SpecType = DATA_TEXTURE; }

	DataType		Type;
	Precision		Prec;
	boost::any		Data;
	size_t			Size;

	uint			NComponents, Width;
};

class MultiTexture: public State {
public:

	MultiTexture( ushort num, const shared_ptr<Texture>& tex, const vector<Vector2f>& coords ):
			State( Resource::MULTI_TEXTURE ), TextureUnit( num ), Texture( tex ), Coordinates( coords )
	{}

	ushort				TextureUnit;
	shared_ptr<Texture> Texture;
	vector<Vector2f>	Coordinates;

};


#endif