
#include "water.hpp"

Vector3f FFTComponent::sample( const Vector3f& pos, float& w ) {
	//http://hal.inria.fr/docs/00/44/40/80/PDF/article-1.pdf
	float lambda = wavevector.length();
	float w = ( lambda / resolution - Nmin ) / ( Nrange );
	w = std::max( std::min( w, 1.f ), 0.f );

	w = 3*w*w - 2*w*w*w;
	return wavevector * amplitude * sin( frequency*t - 
		wavevector.dot( pos ) );	
}

Water::Water( size_t res_, size_t width_, size_t height_, float fov_ ):
	resolution(res_), width(width_), height(height_), fov(fov_),
	aspect( float(width_) / height * fov_ )
{
	size_t nx = width / resolution + 1, ny = height / resolution + 1;
	vertices = new vertex_t[ nx * ny ];
	colors = new color_t[ nx * ny ];
	indices = new index_t[ 6 * (nx-1) * (ny-1) ];

	size_t nquads = 0;
	for( size_t x = 0; x < nx - 1; ++x )
		for( size_t y = 0; y < ny - 1; ++y ) {
			index_t off = x + y * nx;
			indices[ nquads*6 + 0 ] = off; 
			indices[ nquads*6 + 1 ] = off + 1; 
			indices[ nquads*6 + 2 ] = off + nx + 1; 
			indices[ nquads*6 + 3 ] = off; 
			indices[ nquads*6 + 4 ] = off + nx + 1; 
			indices[ nquads*6 + 5 ] = off + nx; 
			++nquads;
		}

}

void Water::dynamic_update( vertex_t* vertices, color_t* colors, 
	index_t* indices, const Vector3f& pos, const Vector3f& look ) {

	size_t nv = 0;
	float xmax = fov * aspect / 2.f, ymax = fov / 2.f;
	for( float x = -xmax; x < xmax; x += float(width)/resolution )
		for( float y = -ymax; y < ymax; y += float(height)/resolution ) {

			Vector3f dir = look + right * x + up * y;
			float a = dir.length_squared();
			float b = 2 * pos.dot( dir );
			float c = pos.length_squared() - 100.f;
			float t = ( -b + sqrt( b*b - 4*a*c ) ) / 2 / a;

			Vector3f pos = look + dir * t, offset;
			for( size_t i = 0; i < components.size(); ++i ) {
				offset += components[ i ].sample( pos );
			}

			vertices[ nv++ ] = pos + offset;
		}

}


