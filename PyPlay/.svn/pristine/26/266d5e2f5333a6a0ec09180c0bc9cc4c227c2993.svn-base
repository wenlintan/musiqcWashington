
from flags import *
from ship_shader import ship_vertex, ship_fragment

from simulation import Transform, Vector3f
from simulation import Mesh, MeshRenderer, MeshAttributeType
from simulation import Program, ProgramVariable
from simulation import Entity, Component, ComponentType, System

class Thruster( Component ):
	pass

class ShipCameraSystem( System ):
	def __init__( self, camera, ship ):
		pass

def build_ship( pos, filename, shaders=True ):
	ent = Entity()
	#ent.add_component( Thruster( Vector3f( 0., 0., 0. ) ) )
	#ent.add_component(

	test = Entity()
	test.add_component( Transform( pos, [ 0., 0., 0. ] ) )
	test.add_component( Mesh( filename, 0.00003 ) )
	test.add_component( MeshRenderer( FinalRenderFlag | ShadowRenderFlag ) )

	if shaders:
		ship_program = Program( ship_vertex, ship_fragment, "" )
		ship_program.flags = FinalRenderFlag
		ship_program.set_frag_location( "out_color", 0 )
		ship_program.set_camera_transform( "modelviewprojection" )
		ship_program.set_variable( "vertex", 
			ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
		ship_program.set_variable( "normal", 
			ProgramVariable.mesh_attribute( MeshAttributeType.NORMAL ) )
		test.add_component( ship_program )

	return test
