#ifndef TRIGGER__H
#define TRIGGER__H

#pragma once
#include "stdafx.h"
#include "action.h"

void export_trigger();
class Trigger {
public:
	typedef shared_ptr<Action> arg_type;
	typedef boost::function<arg_type (arg_type)> cb_type;

	Trigger(): running( false )
	{ }

	void add_trigger( cb_type& fn, int priority = 0 ) {
		callbacks.push_back( make_pair(priority,fn) );
		std::sort( callbacks.begin(), callbacks.end(), boost::bind( &Trigger::callback_compare, this, _1, _2 ) );
	}

	arg_type invoke( arg_type val );

private:
	bool		running;

	bool callback_compare( const pair<int,cb_type>& one, const pair<int,cb_type>& two );
	vector< pair<int,cb_type> > callbacks;
};

#endif
