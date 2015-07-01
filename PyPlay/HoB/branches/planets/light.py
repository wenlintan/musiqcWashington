
from flags import *
from light_shader import *

from simulation import Component, Entity, System, Transform
from simulation import Camera, TextureData, TextureDataPrecision
from simulation import Framebuffer, Renderbuffer, RenderbufferType
from simulation import Program, MeshAttributeType, ProgramVariable

class Light( Component ):
	"Represents a light in the world."

	Directional = 0
	def __init__( self, light_type, shadows = True ):
		super( Light, self ).__init__( ComponentType.Light )
		self.light_type = light_type

		self.shadows = shadows
		if shadows:
			self.shadow_maps = []
			self.shadow_textures = []

	@staticmethod
	def directional( dir ):
		l = Light( Light.Directional )
		l.dir = dir
		return l

class LightShaderData( Component ):
	"Attaches light data to shader variables."

	def __init__( self, shadow_texture, program, shadow_transform  ):
		"""Binds shadow_texture to the shadow fbo of the best light 
		to use on this entity. Binds variable named <shadow_transform>
		to the 4x4 transformation of the shadow fbo in program."""
		super( LightShaderData, self ).__init__( 
			ComponentType.LightShaderData )
		self.texture = shadow_texture
		self.program = program
		self.shadow = shadow_transform


class LightSystem( System ):
	"Processes lights and light shader data."
	def __init__( self, world ):
		super( LightSystem, self ).__init__()
		self.world = world
		self.camera = None

		# TODO: will not work for multiple lights/shadowmaps
		self.texture = TextureData( 
			800, 600, 1, 2, TextureDataPrecision.Depth32 )
		self.transform = Transform()

	def update( self, ent ):
		if ent.has_component( ComponentType.LightShaderData ):
			lsd = ent.get_component( ComponentType.LightShaderData )
			lsd.texture.texture = self.texture

			t = ProgramVariable.mat4( self.transform )
			lsd.program.set_variable( lsd.shadow, t )

		if ent.has_component( ComponentType.Camera ):
			self.camera = ent

		if not ent.has_component( ComponentType.Light ):
			return

		light = ent.get_component( ComponentType.Light )
		if light.shadows:
			if not light.shadow_maps:
				ent = Entity()
				cam = Camera( -2.0, 2.0, -2.0, 2.0, -2.0, 2.0 )
				cam.flags = ShadowRenderFlag
				cam.priority = 0

				fb = Framebuffer( 800, 600 )
				fb.attach_renderbuffer( Renderbuffer( 
					RenderbufferType.Depth, self.texture ) )

				ent.add_component( cam )
				ent.add_component( fb )
				ent.add_component( Transform() )

				program = Program( light_vertex, light_fragment, "" )
				program.flags = ShadowRenderFlag
				program.set_camera_transform( "modelviewprojection" )
				program.set_variable( "vertex", 
					ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
				ent.add_component( program )

				light.shadow_maps.append( ent )
				light.shadow_textures.append( self.texture )
				self.world.add_entity( ent )
			
			if self.camera is None:
				return 

			cam = self.camera.camera()
			camtrans = self.camera.transform()
			for sm in light.shadow_maps:
				lightcam = sm.camera()
				trans = sm.transform()
				#trans.load_identity()

				avez = (cam.nearz + cam.farz) / 2.0
				#base = cam.pos + camtrans.look() * avez
				#lightcam.pos = [0.0, 0.0, 0.0] #base
				#lightcam.rot = [-1.5, 0.0, 0.0]
				trans.position = [0.0, 0.0, 0.0] #base
				trans.rotation = [-1.5, 0.0, 0.0]
				
				#trans.lookat( light.dir, [0.0, 1.0, 0.0] )
				#trans.translate( -base )
				self.transform = lightcam.build_matrix() * \
					sm.transform().build_matrix( False )

