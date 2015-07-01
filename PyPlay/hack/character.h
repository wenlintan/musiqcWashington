#ifndef CHARACTER__H
#define CHARACTER__H

#pragma once

#include "entity.h"
#include "inventory.h"
#include "trigger.h"

void export_character();
class Character: public Entity {
public:
	Character()
	{ }

	Trigger		on_move;
	Trigger		on_weapon_hit, on_spell_hit; 
	Trigger		on_do_damage, on_take_damage;
private:
	Inventory	inventory;
};

#endif