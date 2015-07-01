
#include <vector>
#include <cstdlib>

void wrap_perlin();

class Perlin {
	std::vector< unsigned char > random;
	float grad( unsigned char index, float x, float y, float z );

public:
	Perlin();
	float noise( float x, float y, float z );
};

class Brownian {
	std::vector< Perlin > perlins;
	std::vector< float > ampls, freqs;

public:
	void add_component( float a, float f );
	float noise( float x, float y, float z );
};

