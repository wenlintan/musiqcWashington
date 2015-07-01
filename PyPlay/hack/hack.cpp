
#include "stdafx.h"

#include "scripts.h"
#include "renderer.h"
#include "controller.h"

int main( int argc, char** argv ) {

	hack_srand();

#if defined(WINDOWS) || defined(WIN32)
	shared_ptr<Renderer> r( new WindowsTextRenderer() );
	shared_ptr< InputController > in( new WindowsInputController() );
#elif defined(LINUX)
	shared_ptr<Renderer> r( new X11TextRenderer() );
	shared_ptr< InputController > in( new LinuxInputController() );
#endif

	MapRandomConstraints constraints;
	MapRandomResults results;

	Map m = Map::generate_random( constraints, results );
	shared_ptr< Character > pc( new Character() );
	PlayerController cont( pc, in );

	m.place( pc, results.player_location );
	MapVisibility v( m );

	ScriptController sc;
	sc.load_module( "scripts.test", pc );

	while( true ) {	
		cont.control( m );
		m.resolve();

		v.update( m, pc );
		r->render( v );
	}

	cin.get();
	return 0;
}

