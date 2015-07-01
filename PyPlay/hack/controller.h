#ifndef CONTROLLER__H
#define CONTROLLER__H

#pragma once

#include "input.h"
#include "character.h"
#include "map.h"

class Controller {
public:
	Controller( shared_ptr<Character>& ch ): character( ch )
	{ }

	virtual void control( Map& m ) = 0;

protected:
	shared_ptr<Character>		character;

};

class PlayerController: public Controller {
public:
	PlayerController( shared_ptr<Character>& ch, shared_ptr<InputController>& cont ): Controller( ch ), input( cont )
	{ }

	virtual void control( Map& m );

protected:
	shared_ptr<InputController>	input;
};

class AIController: public Controller {
	AIController( shared_ptr<Character>& ch ): Controller( ch )
	{ }

	virtual void control( Map& m );
};

class NetController: public Controller {
	NetController( shared_ptr<Character>& ch ): Controller( ch )
	{ }

	virtual void control( Map& m );
};

#endif
