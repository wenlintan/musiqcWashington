
#include "vector.hpp"

#include <string>
#include <boost/python.hpp>
using namespace boost::python;

template< typename T >
void wrap_subtype( const std::string& name ) {
	class_< Vector3< T > >( name.c_str() )
		.def( init<T, T, T>() )
		.def( "__getitem__", &Vector3<T>::index )

		.def( -self )
		.def( self += self )
		.def( self + self )
		.def( self -= self )
		.def( self - self )

		.def( self * float() )
		.def( self *= float() )

		.def( "length", &Vector3<T>::length )
		.def( "dot", &Vector3<T>::dot )
		;
}

void wrap_vector() {
	wrap_subtype< float >( "Vector3f" );	
}

