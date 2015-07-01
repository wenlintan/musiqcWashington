
#include "collision.h"

bool operator <( const Collision& one, const Collision& two ) {
	return one.t < two.t;
}