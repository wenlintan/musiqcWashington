
#include "matrix.hpp"

#include <boost/python.hpp>
using namespace boost::python;

template< unsigned N, typename T >
void wrap_subtype( const std::string& name ) {
	typedef T (Matrix<N, T>::*index_type)(unsigned) const;
	index_type index = &Matrix<N, T>::index;

	class_< Matrix< N, T > >( name.c_str() )
		.def( "__getitem__", index )

		.def( self += self )
		.def( self + self )
		.def( self -= self )
		.def( self - self )

		.def( self * self )
		.def( self *= self )
		.def( self * Vector<N, T>() )

		.def( "identity", Matrix<N, T>::identity )
		.staticmethod( "identity" )
		;
}

void wrap_matrix() {
	wrap_subtype< 4, float >( "Matrix4f" );	
}

