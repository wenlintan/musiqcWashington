#ifndef ACTION__H
#define ACTION__H

#pragma once
#include "stdafx.h"

// The actions declare data storage structures designed to be used to communicate actions between various components
//  as such several structures are declared but not defined and must be treated as undefined types

class Map;
#define DECLARE_MAP_VISITOR		virtual void apply( shared_ptr<Action> act, Map& m )	

class Entity;
class Character;
class Item;

void export_action();
struct Action {
	enum ActionType { MOVE, ATTACK };
	Action( const shared_ptr<Entity>& ent, ActionType t ): actor( ent ), type( t ), triggered( false )
	{ }

	void trigger()			{ triggered = true; }

	DECLARE_MAP_VISITOR = 0;
	ActionType				type;
	bool					triggered;
	shared_ptr<Entity>		actor;
};

struct MoveAction: public Action {
	MoveAction( const shared_ptr<Entity>& actor, Direction dir ): Action( actor, MOVE ), direction( dir )
	{ }

	DECLARE_MAP_VISITOR;
	Direction	direction;
};

struct AttackAction: public Action {
	AttackAction( const shared_ptr<Entity>& actor, const shared_ptr<Entity>& o ): Action( actor, ATTACK ), other( o )
	{ }

	DECLARE_MAP_VISITOR;
	shared_ptr<Entity> other;
};

#endif
