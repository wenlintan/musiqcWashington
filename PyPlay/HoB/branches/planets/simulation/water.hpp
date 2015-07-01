
#include <vector>
#include <map>

#include "vector.hpp"

struct FFTComponent {
	Vector3f	wavevector;
	float		frequency, amplitude;

};

class Water {
	std::vector< FFTComponent >	components;

	size_t		width, height, resolution;
	float		fov, aspect;

public:
	typedef float vertex_t[3];
	typedef unsigned char color_t[4];
	typedef unsigned short index_t;

	vertex_t*		vertices;
	color_t*		colors;
	index_t*		indices;

	std::map< size_t, size_t >	batch_data;
	size_t update;

	Water( size_t resolution, size_t w, size_t h, float fov );
	void dynamic_update(vertex_t* vertices, color_t* colors, index_t* indices);
};

