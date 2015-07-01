#ifndef STDAFX__H
#define STDAFX__H

#include <string>
#include <sstream>
#include <iostream>
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
#include "boost/lexical_cast.hpp"
#include "boost/function.hpp"
#include "boost/bind.hpp"
#include "boost/any.hpp"
#include "boost/noncopyable.hpp"
#pragma warning(default: 4267)

using boost::shared_ptr;
using boost::shared_array;
using boost::weak_ptr;
using boost::lexical_cast;
using boost::function;
using boost::any;
using boost::any_cast;

//necessary internal headers
#include "log.h"
#include "math.h"

typedef unsigned int uint;
typedef unsigned long ulong;
typedef unsigned short ushort;
typedef unsigned char uchar;

class g5Exception: public std::exception
{
public:
	g5Exception():
				component("unknown"),
				error("unspecified"),
				recoverable(false)
	{}

	g5Exception(string component_, string error_, bool recoverable_):
				component(component_),
				error(error_),
				recoverable(recoverable_)
	{}

	string component, error;
	bool recoverable;

	string toString()
	{
		string display = recoverable ? "Warning: " : "Error: ";
		display += "module " + component;
		display += " failed -> " + error + "\n";
		return display;
	}
};

#endif