
#pragma once

#include "entity.hpp"

void wrap_system();

class System: boost::noncopyable {
public:
	typedef boost::shared_ptr<System> pointer_type;

	virtual void begin() {}
	virtual void update( Entity::pointer_type entity ) {}
	virtual void end() {}
};

