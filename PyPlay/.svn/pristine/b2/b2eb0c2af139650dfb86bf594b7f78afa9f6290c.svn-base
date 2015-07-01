#include "math.h"
#include "stdafx.h"


#define PyVector( size, type, export_name ) class_< Vector##size<type> >( export_name ) \
	.def_readwrite("x", &Vector##size<type>::x) \
	.def_readwrite("y", &Vector##size<type>::y) \
	.def(self == self) \
	.def(self += self) \
	.def(self -= self) \
	.def(self + self) \
	.def(self - self) \
	.def(self *= type()) \
	.def(self /= type()) \
	.def(self * type()) \
	.def(self / type()) \
	.def("zero", &Vector##size<type>::zero) \
	.def("dot_product", &Vector##size<type>::dot_product) \
	.def("length", &Vector##size<type>::length) \
	.def("length_sq", &Vector##size<type>::length_sq) \
	.def("normalize", &Vector##size<type>::normalize)

#define PyVInit2( type )	.def( init< type, type >() )
#define PyVInit3( type )	.def( init< type, type, type >() )
#define PyVZ3( type )		.def_readwrite("z", &Vector3<type>::z)

void export_math()
{
	/*
	PyVector( 2, float, "vector2f" )PyVInit2(float);
	PyVector( 2, long, "vector2i" )PyVInit2(long);
	PyVector( 2, short, "vector2d" )PyVInit2(short);
	PyVector( 2, char, "vector2b" )PyVInit2(char);

	PyVector( 3, float, "vector3f" )PyVInit3(float)PyVZ3(float);
	PyVector( 3, long, "vector3i" )PyVInit3(long)PyVZ3(long);
	PyVector( 3, short, "vector3d" )PyVInit3(short)PyVZ3(short);
	PyVector( 3, char, "vector3b" )PyVInit3(char)PyVZ3(char);	
	*/
}

#undef PyVector
#undef PyVInit2
#undef PyVInit3
#undef PyVZ3