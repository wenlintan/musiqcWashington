
#include "entity.h"

ostream& operator <<( ostream& o, const EntityPosition& other ) {
	other.write( o );
	return o;
}
