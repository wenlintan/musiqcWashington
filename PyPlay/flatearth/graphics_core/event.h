#ifndef EVENT__H
#define EVENT__H

#include "stdafx.h"
#include <sdl.h>

void export_event();
class Event
{
public:
	Event(): _OldTime( SDL_GetTicks() )		{ LOG_INFO("Event processing created"); }

	bool pollEvent();
	void waitEvent();

	void sleep(uint ms);
	uint deltaTime();
	uint rawTime();


	function< void( Vector2d, bool, bool ) >	MouseClick;
	function< void( Vector2d ) >				MouseMove;
	function< void( short, short, bool ) >		KeyDown;
	function< void() >							Quit;

private:
	uint _OldTime;

};







#endif