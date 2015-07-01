
#include "perlin.hpp"

#include <boost/python.hpp>

#include <cstdlib>
#include <algorithm>

BOOST_PYTHON_MODULE( planet )
{
	using namespace boost::python;
	class_< Perlin >( "Perlin" )
		.def( "noise", &Perlin::noise )
		;

	class_< Brownian >( "Brownian" )
		.def( "add_component", &Brownian::add_component )
		.def( "noise", &Brownian::noise )
		;
}

Perlin::Perlin() {
	// Initialize random with numbers 0-255
	for( unsigned short i = 0; i < 256; ++i )
		random.push_back( (unsigned char)i );

	// Shuffle everything up
	const size_t shuffles = 1024;
	for( size_t i = 0; i < shuffles; ++i ) {
		size_t i1 = ( rand() >> 10 ) & 255;
		size_t i2 = ( rand() >> 10 ) & 255;
		std::swap( random[i1], random[i2] );
	}

	// Double the random array so we can index into it up to 512
	for( unsigned short i = 0; i < 256; ++i )
		random.push_back( random[i] );
}

float Perlin::grad( unsigned char index, float x, float y, float z ) {
	unsigned char h = random[index] & 15;
	float u = h < 8? x: y;
	float v = h < 4? y: (h == 12 || h == 14)? x: z;
	return (h & 1? u: -u) + (h & 2? v: -v);
}

static inline float lerp( float t, float a, float b ) {
	return a + t * (b - a);
}

static inline float fade( float t ) {
	return t * t * t * (t * (t * 6 - 15) + 10);
}

float Perlin::noise( float x, float y, float z ) {
	unsigned char X = int(x) & 255, Y = int(y) & 255, Z = int(z) & 255;
	x = x - floor(x);	y = y - floor(y);	z = z - floor(z);

	float u = fade(x), v = fade(y), w = fade(z);

	unsigned char A = random[X] + Y, 	B = random[X+1] + Y;
	unsigned char AA = random[A] + Z,	AB = random[A+1] + Z;
	unsigned char BA = random[B] + Z,	BB = random[B+1] + Z;

	return lerp( w,
		lerp( v, 
			lerp( u, grad(AA, x, y, z), grad(BA, x-1, y, z) ),
			lerp( u, grad(AB, x, y-1, z), grad(BB, x-1, y-1, z) ) ),
		lerp( v,
			lerp( u, grad(AA+1, x, y, z-1), grad(BA+1, x-1, y, z-1) ),
			lerp( u, grad(AB+1, x, y-1, z-1), grad(BB+1, x-1, y-1, z-1) )
		) );
}

void Brownian::add_component( float a, float f ) {
	perlins.push_back( Perlin() );
	ampls.push_back( a );
	freqs.push_back( f );
}

float Brownian::noise( float x, float y, float z ) {
	float noise = 0.f;
	for( size_t i = 0; i < perlins.size(); ++i ) {
		float a = ampls[i], f = freqs[i];
		noise += a * perlins[i].noise( x*f, y*f, z*f );
	}
	return noise;
}


