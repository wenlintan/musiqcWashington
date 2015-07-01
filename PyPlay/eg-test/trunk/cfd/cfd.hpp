
#include <cstring>
#include <boost/preprocessor.hpp>

template< typename T, unsigned dim >
struct Vector {
	T data[ dim ];
};

template< typename T >
struct Vector< T, 2 > {
	union { T data[ 2 ]; struct{ T x, y; }; };

	Vector< T, 2 >( )
	{}

	Vector< T, 2 >( T x_, T y_ ): x( x_ ), y( y_ )
	{}

};

template< unsigned outer_dim, unsigned dim >
struct DimensionCalculator {
	static size_t calculate( 
			const Vector<size_t, dim>& dims, const Vector<size_t, dim>& vals ) {
		typedef DimensionCalculator< outer_dim - 1, dim > recurse;
		return recurse::calculate( dims, vals ) +
			dims.data[ outer_dim-1 ] * vals.data[ outer_dim-1 ];
	}
};

template< unsigned dim >
struct DimensionCalculator< 1, dim > {
	static size_t calculate( 
			const Vector<size_t, dim>& dims, const Vector<size_t, dim>& vals ) {
		return dims.data[0] * vals.data[0];
	}
};

template< unsigned dim >
size_t calculate_dim(
		const Vector<size_t, dim>& dims, const Vector<size_t, dim>& vals ) {
	return DimensionCalculator< dim, dim >::calculate( dims, vals );
}

template< typename T, unsigned dim >
class UniformGrid {
	T* data;
	Vector< size_t, dim > dimensions;

public:
	UniformGrid( const Vector<size_t, dim> dims ): 
		dimensions( dims ), 
		data( new T[ calculate_dim< dim >( dims, dims ) ] ) 
	{
		std::memset( data,  0, calculate_dim< dim >( dims, dims ) );
	}

	~UniformGrid() {
		delete [] data;
	}

	T& get( Vector< size_t, dim > values ) {
		return data[ calculate_dim< dim >( dimensions, values ) ];
	}

	const T& get( Vector< size_t, dim > values ) const 	{ 
		return data[ calculate_dim< dim >( dimensions, values ) ];
	}
};

class Vorton {
	float vorticity;
};

class SimData {
	float p;
	Vector<float, 2> u, v;
};

class Simulation {
	size_t						grid_dimension;
	UniformGrid< Vector<float, 2>, 2 >	data, storage;

public:
	Simulation( size_t grid_dim ): grid_dimension( grid_dim ),
		data( Vector<size_t, 2>( grid_dim, grid_dim ) ),
		storage( Vector<size_t, 2>( grid_dim, grid_dim ) )
	{}

	void step( float dt );
	void apply_boundary( const Boundary& b );

	Vector<float, 3> 
};

