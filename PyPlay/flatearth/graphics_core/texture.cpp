#include "texture.h"

#pragma warning( disable: 4996 )
bool Texture::initialize( const string& file )
{
	Name = file;
	FILE* stream = fopen(file.c_str(), "rb");
	if(!stream)
	{
		LOG_ERR("Could not open texture file");
		return false;
	}

	fread(&_FileHeader, sizeof(BitmapFileHeader), 1, stream);
	if(_FileHeader.bfType != BITMAP_MAGIC_NUMBER)
	{
		LOG_ERR("Invalid texture file");
		fclose(stream);
		return false;
	}

	fread(&_InfoHeader, sizeof(BitmapInfoHeader), 1, stream);
	if(_InfoHeader.biBitCount != 24 && _InfoHeader.biBitCount != 32)
	{
		LOG_ERR("Unsupported bpp, cannot load bitmap");
		fclose(stream);
		return false;
	}
	LOG_INFO("Texture header files loaded and valid");

	//save the width, height and bits per pixel for external use
    Width = _InfoHeader.biWidth;
    Height = _InfoHeader.biHeight;
    Bpp = _InfoHeader.biBitCount;

	int size = (Width*Height*(unsigned int)(_InfoHeader.biBitCount/8.0));
	PixelDataSize = (unsigned int)size;

	unsigned char* tempPixelData = new unsigned char[size];
	if(!tempPixelData)
	{
		LOG_ERR("Could not allocate temporary pixel data");
		fclose(stream);
		return false;
	}

	fread(tempPixelData, sizeof(char), size, stream);
	fclose(stream);

	LOG_INFO("Pixel data loaded");

	//need to see if bitmap was padded to DWORD bounds
	int padWidth, byteWidth;
	padWidth = byteWidth = (long)((float)Width * (float)_InfoHeader.biBitCount/8.0);
	while(padWidth%4 != 0)
		++padWidth;


	int height = _InfoHeader.biHeight;
	PixelData=new unsigned char[size];
	if(!PixelData) 
	{
		LOG_ERR("Could not allocate pixel data");
		return false;
	}


	if(_InfoHeader.biBitCount == 32)
	{
		if(height>0) {
			int offset=padWidth-byteWidth;
			//count backwards so you start at the front of the image
			for(int i=0;i<size;i+=4) {
				//jump over the padding at the start of a new line
				if((i+1)%padWidth==0) {
					i+=offset;
				}
				//transfer the data
				*(PixelData+i+3)=*(tempPixelData+i);
				*(PixelData+i+2)=*(tempPixelData+i+1);
				*(PixelData+i+1)=*(tempPixelData+i+2);
				*(PixelData+i)=*(tempPixelData+i+3);
			}
		}

		//image parser for a forward image
		else {
			int offset=padWidth-byteWidth;
			int j=size-3;
			//count backwards so you start at the front of the image
			//here you can start from the back of the file or the front,
			//after the header  The only problem is that some programs
			//will pad not only the data, but also the file size to
			//be divisible by 4 bytes.
			for(int i=0;i<size;i+=4) {
				//jump over the padding at the start of a new line
				if((i+1)%padWidth==0) {
					i+=offset;
				}
				//transfer the data
				*(PixelData+i+3)=*(tempPixelData+i);
				*(PixelData+j+2)=*(tempPixelData+i+1);
				*(PixelData+j+1)=*(tempPixelData+i+2);
				*(PixelData+j)=*(tempPixelData+i+3);
				j-=4;
			}
		}

		delete [] tempPixelData;
	}
	else if (_InfoHeader.biBitCount == 24)
	{
		if(height>0) {
			int offset=padWidth-byteWidth;
			//count backwards so you start at the front of the image
			for(int i=0;i<size;i+=3) {
				//jump over the padding at the start of a new line
				if((i+1)%padWidth==0) {
					i+=offset;
				}
				//transfer the data
				*(PixelData+i+2)=*(tempPixelData+i);
				*(PixelData+i+1)=*(tempPixelData+i+1);
				*(PixelData+i)=*(tempPixelData+i+2);
			}
		}

		//image parser for a forward image
		else {
			int offset=padWidth-byteWidth;
			int j=size-3;
			//count backwards so you start at the front of the image
			//here you can start from the back of the file or the front,
			//after the header  The only problem is that some programs
			//will pad not only the data, but also the file size to
			//be divisible by 4 bytes.
			for(int i=0;i<size;i+=3) {
				//jump over the padding at the start of a new line
				if((i+1)%padWidth==0) {
					i+=offset;
				}
				//transfer the data
				*(PixelData+j+2)=*(tempPixelData+i);
				*(PixelData+j+1)=*(tempPixelData+i+1);
				*(PixelData+j)=*(tempPixelData+i+2);
				j-=3;
			}
		}

		delete [] tempPixelData;
	}

	stringstream buf;
	buf << "Texture loaded - " << file;
	LOG_SUCCESS(buf.str());
	return true;
}

void swap( unsigned char& one, unsigned char& two )
{
	char store = one;
	one = two;
	two = store;
}

void Texture::reverse_data()
{
	for(uint i=0; i<PixelDataSize; i+=3)
	{
		swap( PixelData[i+2], PixelData[PixelDataSize-(i+2)-1] );
		swap( PixelData[i+1], PixelData[PixelDataSize-(i+1)-1] );
		swap( PixelData[i+0], PixelData[PixelDataSize-(i+0)-1] );
	}
		
}

bool Texture::save( const string& file )
{ return true; }

void Texture::shutdown()
{
	delete [] PixelData;
	PixelData = NULL;
}