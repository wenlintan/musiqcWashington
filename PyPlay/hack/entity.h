
#ifndef ENTITY__H
#define ENTITY__H

#include "status.h"
#include "trigger.h"

class EntityPosition {
public:
	virtual EntityPosition& move( Direction dir ) = 0;

	virtual void write( ostream& o ) const = 0;
	virtual bool operator ==( const EntityPosition& other ) const = 0;
	friend ostream& operator <<( ostream& o, const EntityPosition& other );
};
ostream& operator <<( ostream& o, const EntityPosition& other );

class Entity {
public:
	virtual shared_ptr< EntityPosition >& position()				{ return pos; }

private:
	Status		status;
	shared_ptr< EntityPosition >	pos;
	
};

#endif
