
from math import cos, sin

from flags import *
from light import *
from ship import build_ship
from event import *

from planet_shader import planet_vertex, planet_fragment
from sky_shader import sky_vertex, sky_fragment

from simulation import World, System, Component, ComponentType, Entity, Vector3f
from simulation import ScreenSystem, MeshRendererSystem, EventSystem

from simulation import AABBMesh, Mesh, MeshRenderer, Transform, Camera
from simulation import Program, ProgramVariable, MeshAttributeType
from simulation import Texture, TextureData, TextureDataPrecision

from simulation import VertexArray, SphericalROAM, SphericalROAMSystem,	Brownian

# Create world and attach necessary systems
world = World()
screen_system = ScreenSystem( 800, 600 )
#screen_system.has_shaders = False
world.add_system( screen_system )

world.add_system( MeshRendererSystem() )
world.add_system( SphericalROAMSystem() )
if screen_system.has_shaders:
	world.add_system( LightSystem( world ) )

event_system = PyEventSystem()
world.add_system( event_system )
world.add_system( FollowSystem() )

camera = Entity()
camera.add_component( Transform( [0., 0., -1.2], [-3.14, 0., 0.] ) )
cam = Camera( 70., 800. / 600., 0.001, 10. )
cam.priority = 100
cam.flags = FinalRenderFlag
camera.add_component( cam );
#camera.add_component( Component( ComponentType.MouseControlled ) )
world.add_entity( camera )

if screen_system.has_shaders:
	sun = Entity()
	sun.add_component( Light.directional( [1.0, 0.0, 0.0] ) )
	world.add_entity( sun )

mts_biome = Brownian()
mts_biome.add_component( 2., 3. )

mts = Brownian()
mts.add_component( 1., 100. )
mts.add_component( 0.8, 110. )
mts.add_component( 0.8, 130. )
mts.add_component( 0.6, 200. )
mts.add_component( 0.6, 250. )
mts.add_component( 0.02, 5000. )

hills = Brownian()
hills.add_component( 0.05, 500. )

def noisefn( x, y, z ):
	h = mts_biome.noise(x, y, z)**3 * ( 0.3 +
		mts.noise(x, y, z)**2 )
	#h += hills.noise(x, y, z)
	h *= 0.003
	return h

mesh = Entity()
mesh.add_component( VertexArray( 60000, 205000 ) )
mesh.add_component( SphericalROAM( noisefn ) )
mesh.add_component( MeshRenderer( FinalRenderFlag | ShadowRenderFlag ) )
if screen_system.has_shaders:
	mesh.add_component( Texture( 0, TextureData("terrain/dirt.bmp") ) )
	mesh.add_component( Texture( 1, TextureData("terrain/grass.bmp") ) )
	mesh.add_component( Texture( 2, TextureData("terrain/rock.bmp") ) )
	mesh.add_component( Texture( 3, TextureData("terrain/snow.bmp") ) )

	planet_program = Program( planet_vertex, planet_fragment, "" )
	planet_program.flags = FinalRenderFlag
	planet_program.set_frag_location( "color", 0 )
	planet_program.set_camera_transform( "modelviewprojection" )
	planet_program.set_variable( "vertex", 
		ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
	planet_program.set_variable( "normal", 
		ProgramVariable.mesh_attribute( MeshAttributeType.NORMAL ) )
	planet_program.set_variable( "dirt", ProgramVariable.int1( 0 ) )
	planet_program.set_variable( "grass", ProgramVariable.int1( 1 ) )
	planet_program.set_variable( "rock", ProgramVariable.int1( 2 ) )
	planet_program.set_variable( "snow", ProgramVariable.int1( 3 ) )
	planet_program.set_variable( "shadow", ProgramVariable.int1( 4 ) )

	tex = Texture( 4, None )
	tex.flags = FinalRenderFlag
	light_data = LightShaderData( tex, planet_program, "shadow_transform" )
	mesh.add_component( tex )
	mesh.add_component( light_data )

	mesh.add_component( planet_program )
world.add_entity( mesh )
	
if screen_system.has_shaders:
	sky = Entity()
	sky.add_component( AABBMesh( [-1.5, -1.5, -1.5], [3., 3., 3.] ) )
	sky.add_component( MeshRenderer( FinalRenderFlag ) )
	sky_program = Program( sky_vertex, sky_fragment, "" )
	sky_program.set_frag_location( "color_out", 0 )
	sky_program.set_camera_transform( "modelviewprojection" )
	sky_program.set_variable( "vertex",
		ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
	sky.add_component( sky_program )
	world.add_entity( sky )

ship = build_ship( [ 0.0, 0.0, -1.2 ], "atst.dae", screen_system.has_shaders )
ship.add_component( Component( ComponentType.MouseControlled ) )
world.add_entity( ship )
camera.add_component( FollowComponent( ship, 0.002 ) )

t = 0.0
while event_system.running:
	if screen_system.has_shaders:
		camera_var = ProgramVariable.float3( camera.transform().position )
		sun_var = ProgramVariable.float3( [cos(t), 0, sin(t)] )
		sky_program.set_variable( "camera", camera_var )
		sky_program.set_variable( "sun", sun_var )
		planet_program.set_variable( "camera", camera_var )
		planet_program.set_variable( "sun", sun_var )
	#t += 0.01
	if t > 6.22:	t -= 6.22

	world.update()

