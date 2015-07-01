#ifndef INVENTORY__H
#define INVENTORY__H

#include "item.h"

class TextInventoryEntityPosition: public EntityPosition {
	TextInventoryEntityPosition( uchar sym ): symbol( sym )
	{ }

private:
	uchar	symbol;
};

class Inventory {
public:
	void get( shared_ptr<Item> i );
	void drop( shared_ptr<Item> i );

private:
	vector< shared_ptr<Item> >	items;
};

#endif
