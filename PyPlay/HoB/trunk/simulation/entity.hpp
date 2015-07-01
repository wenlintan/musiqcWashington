
#include <string>
#include <vector>
#include <memory>

#include "list.hpp"
#include "network.hpp"
#include "collision.hpp"

class Entity {
public:
	virtual ~Entity() 
	{}

	virtual CollGeometry&	collision_geometry() = 0;
	virtual void			resolve( Entity& other, Collision& coll ) = 0;

	virtual State&			state() = 0;

	typedef ListLink< Entity > Link_t;
	Link_t links;
};




