
#include "graphics_core/stdafx.h"
#include "graphics_core/glrenderer.h"
#include "graphics_core/camera.h"
#include "graphics_core/event.h"

#include "airplane.h"

const short screen_width = 800, screen_height = 600;

//simple functions to implement user interface

extern "C" void _imp__fprintf( char*, ... ) {};

bool running = true;
ControlSurfaceSet controls;

void quit() {	running = false;	}

bool left_down = false, right_down = false;
void mouse_click( Vector2d pos, bool down, bool left ) {
	if( left )		left_down = down;
	else			right_down = down;
}

void mouse_move( Vector2d delta, shared_ptr<Camera> cam ) {
	if( left_down ) {
		controls.rudder += delta.x;
		controls.elevator += delta.y;
	}
	if( right_down ) {
	}
}

int main(int argc, char* argv[])
{
	try
	{
		logger = new Logger("edit.html");
	}
	catch( g5Exception& )
	{
		return -1;
	}
	
	try
	{
		shared_ptr<GLRenderer> gl( new GLRenderer() );
		gl->initialize( Vector2d( screen_width, screen_height ), false );

		shared_ptr<GLFont> font( new GLFont( "Images/Font1.bmp", gl ) );

		shared_ptr<Camera> cam( new Camera() );
		cam->set(	Vector2d(screen_width, screen_height), 
					Vector3f(0.0,0.0,0.0), Vector3f(0.0,0.0,-1.0), Vector3f(0.0,1.0,0.0), 
					70.0f, 0.01f, 10.0f );

		shared_ptr<Light> light( new Light() );				light->ID = 0;
		light->Enabled = true;	light->Point = true;		light->PointPosition = Vector3f( 0.0f, -0.2f, -0.2f );
		light->Diffuse = LightColor( 0.0, 1.0f, 0.0 );		light->Specular = LightColor( 1.0, 1.0, 1.0 );
		light->Ambient = LightColor( 1.0f, 1.0f, 1.0f );

		gl->apply_render_state( cam );
		gl->apply_render_state( light );
		
		Airplane p = Airplane::simple_model();
		AirplaneState s( p );
		AirplaneRenderer r( s );

		//set initial conditions
		s.position = Vector3f( 0.0f, 0.0f, 0.0f );
		s.velocity = Vector3f( 456.0f, 0.0f, 0.0f );

		shared_ptr<Event> ev( new Event() );
		ev->Quit = &quit;
		ev->MouseClick = &mouse_click;
		ev->MouseMove = boost::bind( &mouse_move, _1, cam );

		while( running ) {
			while( ev->pollEvent() );
			uint millis = ev->deltaTime();
			s.update( controls, 621, Vector3f(), millis / 1000.0f );

			r.setup_follow_camera( cam );
			gl->apply_render_state( cam );

			gl->start_frame();
			r.render( gl );
			gl->end_frame();
		}

	}
	catch( ... ) {
		LOG_ERR( "I am a big fat french idiot" );
	}

	return 0;
}
