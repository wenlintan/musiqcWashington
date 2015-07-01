#include "stdafx.h"

void export_stdafx() {
	using namespace boost::python;

	enum_< Direction >( "Direction" )
		.value("EAST", EAST)				.value("WEST", WEST)
		.value("NORTH", NORTH)				.value("SOUTH", SOUTH)
		.value("NORTH_EAST", NORTH_EAST)	.value("NORTH_WEST", NORTH_WEST)
		.value("SOUTH_WEST", SOUTH_WEST)	.value("SOUTH_EAST", SOUTH_EAST)
		.value("UP", UP)					.value("DOWN", DOWN)
		.value("SELF", SELF)				.value("NUM_DIRECTIONS", NUM_DIRECTIONS)
		.export_values()
	;

	enum_< Color >( "Color" )
		.value("BLACK", BLACK)				.value("RED", RED)
		.value("GREEN", GREEN)				.value("BLUE", BLUE)
		.value("MAGENTA", MAGENTA)			.value("CYAN", CYAN)
		.value("YELLOW", YELLOW)			.value("GRAY", GRAY) 
		.value("BRIGHT_RED", BRIGHT_RED)	.value("BRIGHT_GREEN", BRIGHT_GREEN)
		.value("BRIGHT_BLUE", BRIGHT_BLUE)	.value("BRIGHT_MAGENTA", BRIGHT_MAGENTA)
		.value("BRIGHT_CYAN", BRIGHT_CYAN)	.value("BRIGHT_YELLOW", BRIGHT_YELLOW)
		.value("WHITE", WHITE)				.value("NUM_COLORS", NUM_COLORS)
		.export_values()
	;


	def( "rand", hack_rand );
	def( "norm_rand", hack_norm_rand );

	def( "dn", dn );
	def( "ndm", ndm );
}

Vector2d DirectionOffsets[] = 
	{	Vector2d(1,0),  Vector2d(-1,0),  Vector2d(0,-1), Vector2d(0,1),
		Vector2d(1,-1), Vector2d(-1,-1), Vector2d(-1,1), Vector2d(1,1)
	};

void hack_srand() {
	srand( (size_t)time(NULL) );
}

int hack_rand() {
	return rand();
}

float hack_norm_rand() {
	return (float)rand()/((float)RAND_MAX + 1.0f);
}

uint dn( uint n ){
	return (uint)( n*hack_norm_rand() )+1;
}

uint ndm( uint n, uint m ){
	uint val = 0;
	for( size_t i = 0; i < n; ++i )
		val += dn( m );
	return val;
} 
