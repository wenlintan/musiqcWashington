#include "event.h"

void export_event()
{
	/*
	class_<Event>("event")
		.def_readwrite("keydown", &Event::KeyDown)
		.def_readwrite("mouseclick", &Event::MouseClick)
		.def_readwrite("mousemove", &Event::MouseMove)
		.def_readwrite("quit", &Event::Quit)
		.def("poll_event", &Event::pollEvent)
		.def("wait_event", &Event::waitEvent)
		.def("sleep", &Event::sleep)
		.def("get_delta_time", &Event::deltaTime)
		.def("get_raw_time", &Event::rawTime);

	
	enum_<SDLKey>("sdlkey")
		.value("K_RETURN", SDLK_RETURN)
		.value("K_RIGHT", SDLK_RIGHT)
		.value("K_UP", SDLK_UP)
		.value("K_LEFT", SDLK_LEFT)
		.value("K_DOWN", SDLK_DOWN)
		.value("K_LAST", SDLK_LAST)
		.export_values();
		*/
		

}

bool Event::pollEvent()
{
	SDL_Event e;
	if(!SDL_PollEvent(&e))
		return false;

	switch(e.type)
	{
	case SDL_KEYDOWN:
		if(KeyDown) KeyDown(e.key.keysym.unicode, (short)e.key.keysym.sym, true);
		break;
	case SDL_KEYUP:
		if(KeyDown) KeyDown(e.key.keysym.unicode, (short)e.key.keysym.sym, false);
		break;
	case SDL_MOUSEBUTTONDOWN:
		if(MouseClick) MouseClick( Vector2d(e.button.x, e.button.y), true, e.button.button == SDL_BUTTON_LEFT );
		break;
	case SDL_MOUSEBUTTONUP:
		if(MouseClick) MouseClick( Vector2d(e.button.x, e.button.y), false, e.button.button == SDL_BUTTON_LEFT );
		break;
	case SDL_MOUSEMOTION:
		if(MouseMove) MouseMove( Vector2d(e.motion.xrel, e.motion.yrel) );
		break;
	case SDL_QUIT:
		if(Quit) Quit();
		break;
	}

	return true;
}

void Event::waitEvent()
{
	SDL_WaitEvent(NULL);
	pollEvent();
}

void Event::sleep(uint ms)
{
	SDL_Delay(ms);
}

uint Event::deltaTime()
{
	uint n = SDL_GetTicks();

	if( n <= _OldTime )
		return 0;

	uint dt = n - _OldTime;
	_OldTime = n;
	return dt;
}

uint Event::rawTime()
{
	return SDL_GetTicks();
}