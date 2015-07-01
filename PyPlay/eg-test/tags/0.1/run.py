
import pdb
from renderer import *

class Entity:
    def __init__( self, position ):
            self.pos = position

class Order:
    pass

r = Renderer( 800, 600 )
tiles = [ Tile( x, y ) for x in range( 80 ) for y in range( 60 ) ]
batch = Batch( tiles )

src = """
#version 330
uniform mat4 modelview, projection;

in vec4 vertex;
in vec3 color;

out vec3 frag_color;

void main() {
    gl_Position = projection * modelview * vertex;
    frag_color = color; 
}

--Vertex/Fragment--
#version 330

in vec3 frag_color;
out vec4 out_color;

void main() {
    out_color = vec4( frag_color, 1.0 );
    //out_color = vec4( 1.0, 0.0, 0.0, 1.0 );
}
"""

compare_src = """
#version 330

void main() {
    
}

--Vertex/Fragment--
#version 330

void main() {
    
}
"""

##pdb.set_trace()
program = Program.create( src, "out_color" )
program.set_matrices_from_gl( "modelview", "projection" )
program.vars.vertex = Program.Vertex
program.vars.color = Program.Color
program.apply()

handle_key = {}
handle_event = {}
handle_event[ KEYDOWN ] = lambda ev: handle_key[ ev.key ]( ev.key, True )
handle_event[ KEYUP ] = lambda ev: handle_key[ ev.key ]( ev.key, False )

event = pygame.event.poll()
while event.type != QUIT:

    event = pygame.event.poll()
    while event.type not in ( NOEVENT, QUIT ):
        if event.type in handle_event:
            handle_event[ event.type ]( event )
        event = pygame.event.poll()

    r.begin_frame()
    batch.draw( program )
    r.end_frame()


