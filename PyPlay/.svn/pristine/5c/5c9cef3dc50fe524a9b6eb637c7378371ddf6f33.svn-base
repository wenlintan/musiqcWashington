#ifndef STDAFX__H__PROJ
#define STDAFX__H__PROJ

#pragma once

#include <string>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <list>
#include <map>
#include <set>
#include <queue>
#include <algorithm>
#include <cctype>
#include <cstdlib>
using namespace std;

//yay boost!
#pragma warning(disable: 4267)
#include "boost/smart_ptr.hpp"
using boost::shared_ptr;
using boost::shared_array;
using boost::weak_ptr;

#include "boost/function.hpp"
#include "boost/bind.hpp"

#include "boost/noncopyable.hpp"
#include "boost/python.hpp"

#include "boost/program_options.hpp"
namespace options = boost::program_options;
#pragma warning(default: 4267)


//#pragma comment( lib, "libboost_program_options-vc90-mt-gd-1_37.lib" )
//#pragma comment( lib, "libboost_python-vc90-mt-gd-1_37.lib" )
//#pragma comment( lib, "libboost_signals-vc90-mt-gd-1_37.lib" )

typedef unsigned int uint;
typedef unsigned long ulong;
typedef unsigned short ushort;
typedef unsigned char uchar;

#include "math.h"

void export_stdafx();
enum Direction { EAST, WEST, NORTH, SOUTH, NORTH_EAST, NORTH_WEST, SOUTH_WEST, SOUTH_EAST, UP, DOWN, SELF, NUM_DIRECTIONS };
extern Vector2d DirectionOffsets[];

enum Color { BLACK, RED, GREEN, BLUE, MAGENTA, CYAN, YELLOW, GRAY, 
	BRIGHT_RED, BRIGHT_GREEN, BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_YELLOW, WHITE, NUM_COLORS };

void hack_srand();
int hack_rand();
float hack_norm_rand();

template< typename T >
T hack_range( T min, T max ) {
	return (T)((max-min+(T)1)*hack_norm_rand()) + min;
}

uint dn( uint n );
uint ndm( uint n, uint m );

#endif
