
import pdb
pdb.set_trace()

from random import random, shuffle

from simulation import *

from car import *
from collision import *
from tilemap import *

from tile_shader import tile_vertex, tile_fragment


def create_tilemap( tsize ):
	worldmap = Entity()
	base_attrs = MeshAttributeType.VERTEX | MeshAttributeType.TEX_COORD0 |\
		MeshAttributeType.COLOR
	base_mesh = QuadMesh( [0.]*3, [tsize]*2, MeshAttributeType( base_attrs ) )
	xoff, yoff = [ tsize, 0, 0 ], [ 0, tsize, 0 ]
	mesh = BatchMesh( base_mesh, xoff, yoff, 30, 30 )
	worldmap.add_component( mesh )

	tilemap = Tilemap( 30, 30, 16. / 272, 16. / 192 )
	tileset = Texture( 0, TextureData( "assets/tiles.bmp" ) )
	worldmap.add_component( tileset )
	worldmap.add_component( tilemap )

	tile_program = Program( tile_vertex, tile_fragment, "" )
	tile_program.flags = 0xFF
	tile_program.set_frag_location( "out_color", 0 )
	tile_program.set_camera_transform( "modelviewprojection" )
	tile_program.set_variable( "vertex", 
		ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
	tile_program.set_variable( "tcoord0", 
		ProgramVariable.mesh_attribute( MeshAttributeType.TEX_COORD0 ) )
	tile_program.set_variable( "color",
		ProgramVariable.mesh_attribute( MeshAttributeType.COLOR ) )
	tile_program.set_variable( "tileset", ProgramVariable.int1( 0 ) )

	worldmap.add_component( tile_program )
	worldmap.add_component( MeshRenderer( 0xFF ) )
	return worldmap

def create_character( position ):
	player = Entity()
	player.add_component( Transform( position, [0., 0., 0.] ) )
	player.add_component( Health( 100 ) )
	
	collmesh = CollisionMesh()
	collmesh.add_geometry( CollAABB( [-8., -8., 0.], [16., 16., 0.] ) )
	player.add_component( collmesh )

	player_texture = Texture( 0, TextureData( "assets/player.bmp" ) )
	player.add_component( player_texture )

	player_attrs = MeshAttributeType.VERTEX | MeshAttributeType.TEX_COORD0
	player_mesh = QuadMesh( [-8., -8., 0.], [16.]*2, 
		MeshAttributeType(player_attrs) )
	player.add_component( player_mesh )

	player_program = Program( tile_vertex, tile_fragment, "" )
	player_program.flags = 0xFF
	player_program.set_frag_location( "out_color", 0 )
	player_program.set_camera_transform( "modelviewprojection" )
	player_program.set_variable( "vertex", 
		ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
	player_program.set_variable( "tcoord0", 
		ProgramVariable.mesh_attribute( MeshAttributeType.TEX_COORD0 ) )
	player_program.set_variable( "tileset", 
		ProgramVariable.int1( 0 ) )

	player.add_component( player_program )
	player.add_component( MeshRenderer( 0xFF ) )
	return player

def create_car( position ):
	car = Entity()
	car.add_component( Transform( position, [0., 0., 0.] ) )
	car.add_component( Car() )
	car.add_component( Physics( 1500., 1500.*16*16, restitution = 0.2 ) )
	
	collmesh = CollisionMesh()
	collmesh.add_geometry( CollAABB( [-8., -16., 0.], [16., 32., 0.] ) )
	car.add_component( collmesh )

	car_texture = Texture( 0, TextureData( "assets/car.bmp" ) )
	car.add_component( car_texture )

	car_attrs = MeshAttributeType.VERTEX | MeshAttributeType.TEX_COORD0
	car_mesh = QuadMesh( [-8., -16., 0.], [16., 32.], 
		MeshAttributeType(car_attrs) )
	car.add_component( car_mesh )

	car_program = Program( tile_vertex, tile_fragment, "" )
	car_program.flags = 0xFF
	car_program.set_frag_location( "out_color", 0 )
	car_program.set_camera_transform( "modelviewprojection" )
	car_program.set_variable( "vertex", 
		ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
	car_program.set_variable( "tcoord0", 
		ProgramVariable.mesh_attribute( MeshAttributeType.TEX_COORD0 ) )
	car_program.set_variable( "tileset", 
		ProgramVariable.int1( 0 ) )

	car.add_component( car_program )
	car.add_component( MeshRenderer( 0xFF ) )
	return car

def create_pickup( position, item ):
	pickup = Entity()
	pickup.add_component( Transform( position, [0.]*3 ) )
	pickup.add_component( Pickup( 3, item, 10 ) )
	pickup.add_component( Trigger() )

	collmesh = CollisionMesh()
	collmesh.add_geometry( CollAABB( [-5., -5., 0.], [10., 10., 0.] ) )
	pickup.add_component( collmesh )

	attrs = MeshAttributeType.VERTEX | MeshAttributeType.TEX_COORD0
	mesh = QuadMesh( [-5., -5., 0.], [10., 10.], MeshAttributeType(attrs) )
	pickup.add_component( mesh )

	texture = Texture( 0, TextureData( "assets/pistol.bmp" ) )
	pickup.add_component( texture )

	program = Program( tile_vertex, tile_fragment, "" )
	program.flags = 0xFF
	program.set_frag_location( "out_color", 0 )
	program.set_camera_transform( "modelviewprojection" )
	program.set_variable( "vertex", 
		ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
	program.set_variable( "tcoord0", 
		ProgramVariable.mesh_attribute( MeshAttributeType.TEX_COORD0 ) )
	program.set_variable( "tileset", 
		ProgramVariable.int1( 0 ) )

	pickup.add_component( program )
	pickup.add_component( MeshRenderer( 0xFF ) )
	return pickup

def create_bullet( position, rotation, damage = 1 ):
	bullet = Entity()
	bullet.add_component( Bullet( damage ) )
	bullet.add_component( Transform( position, rotation ) )
	bullet.add_component( Physics( 0.01, 0. ) )
	bullet.get_component( ComponentType.Physics ).coll_type = Physics.Trigger
	bullet.add_component( Trigger() )

	collmesh = CollisionMesh()
	collmesh.add_geometry( CollAABB( [-2., -2., 0.], [4., 4., 0.] ) )
	bullet.add_component( collmesh )

	attrs = MeshAttributeType.VERTEX | MeshAttributeType.TEX_COORD0
	mesh = QuadMesh( [-2., -2., 0.], [4., 4.], MeshAttributeType(attrs) )
	bullet.add_component( mesh )

	texture = Texture( 0, TextureData( "assets/bullet.bmp" ) )
	bullet.add_component( texture )

	program = Program( tile_vertex, tile_fragment, "" )
	program.flags = 0xFF
	program.set_frag_location( "out_color", 0 )
	program.set_camera_transform( "modelviewprojection" )
	program.set_variable( "vertex", 
		ProgramVariable.mesh_attribute( MeshAttributeType.VERTEX ) )
	program.set_variable( "tcoord0", 
		ProgramVariable.mesh_attribute( MeshAttributeType.TEX_COORD0 ) )
	program.set_variable( "tileset", 
		ProgramVariable.int1( 0 ) )

	bullet.add_component( program )
	bullet.add_component( MeshRenderer( 0xFF ) )
	return bullet

class Bullet( Component ):
	def __init__( self, damage ):
		super( Bullet, self ).__init__( ComponentType.Bullet )
		self.damage = damage

class Health( Component ):
	def __init__( self, max_health ):
		super( Health, self ).__init__( ComponentType.Health )
		self.health = self.max_health = max_health

class BulletSystem( System ):
	def __init__( self, world ):
		super( BulletSystem, self ).__init__()
		self.world = world

	def update( self, ent ):
		if not ent.has_component( ComponentType.Bullet ):
			return
		bullet = ent.get_component( ComponentType.Bullet )
		trigger = ent.get_component( ComponentType.Trigger )
		if trigger.triggered:
			if trigger.entity.has_component( ComponentType.Health ):
				health = trigger.entity.get_component( ComponentType.Health )
				health.health -= bullet.damage
				self.world.remove_entity( ent )
			trigger.triggered = False

class Inventory( Component ):
	Uzi = 0
	def __init__( self ):
		super( Inventory, self ).__init__( ComponentType.Inventory )
		self.items = defaultdict( int )
		self.selected_item = None

	def give( self, item, quantity ):
		self.items[ item ] += quantity

	def select( self, item ):
		self.selected_item = item

class Pickup( Component ):
	def __init__( self, reset, item, quantity = 1 ):
		super( Pickup, self ).__init__( ComponentType.Pickup )
		self.reset_time = reset 
		self.item_type = item
		self.item_quantity = quantity

		self.empty = False
		self.empty_tile = 0.

class PickupSystem( System ):
	def __init__( self ):
		super( PickupSystem, self ).__init__()

	def update( self, ent ):
		if not ent.has_component( ComponentType.Pickup ):
			return

		pickup = ent.get_component( ComponentType.Pickup )
		trigger = ent.get_component( ComponentType.Trigger )

		if trigger.triggered and not pickup.empty:
			if trigger.entity.has_component( ComponentType.Inventory ):
				i = trigger.entity.get_component( ComponentType.Inventory )
				i.give( pickup.item_type, pickup.item_quantity )

				pickup.empty = True
				pickup.empty_time = time()
				ent.get_component( ComponentType.MeshRenderer ).flags = 0

		# Collision system doesn't reset this currently
		trigger.triggered = False

		if pickup.empty and time() - pickup.empty_time > pickup.reset_time:
			pickup.empty = False
			ent.get_component( ComponentType.MeshRenderer ).flags = 0xff

class TilemapEntitySystem( System ):
	def __init__( self, world ):
		super( TilemapEntitySystem, self ).__init__()
		self.npedestrians, self.pedestrians = 5, []
		self.free_pedestrians = []

		self.ncars, self.cars = 100, []
		self.free_cars = []

		self.tilemap = None
		self.players = []

		for i in range( self.npedestrians ):
			ent = create_character( [0.] * 3 )
			ent.add_component( Pedestrian() )
			world.add_entity( ent )

			self.pedestrians.append( ent )
			self._free_pedestrian( ent )

		return
		for i in range( self.ncars ):
			ent = Entity()
			ent.add_component( Car() )
			ent.add_component( Physics( 1500., 1500. ) )

			world.add_entity( ent )
			self.free_cars.append( ent )


	def _free_pedestrian( self, p ):
		self.pedestrians.remove( p )
		self.free_pedestrians.append( p )
		p.get_component( ComponentType.MeshRenderer ).flags = 0

	def _alloc_pedestrian( self ):
		p = self.free_pedestrians.pop()
		self.pedestrians.append( p )
		p.get_component( ComponentType.MeshRenderer ).flags = 0xff
		return p

	def update( self, ent ):
		if ent.has_component( ComponentType.Tilemap ):
			self.tilemap = ent
		if ent.has_component( ComponentType.Player ):
			self.players.append( ent )

	def end( self ):
		if tilemap is None:
			return

		for p in self.pedestrians:
			dists = [ (p.transform().position - 
				player.transform().position).length_sq() 
				for player in self.players ]

			if all( d > 150.**2 for d in dists ):
				self._free_pedestrian( p )

		for p in self.players:
			i = 0
			while len(self.pedestrians) < self.npedestrians and i < 10:
				i += 1
				r = random()*50 + 50
				theta = random()*2*pi

				pos = p.transform().position
				tx, ty = pos[0] + r*cos(theta), pos[1] + r*sin(theta)

				flags = tilemap.flags[int(tx/16)][int(ty/16)]
				if not flags & Tilemap.Pedestrian:
					continue
				
				p = self._alloc_pedestrian()
				p.transform().position = [tx, ty, 0.]

		self.tilemap = None
		self.players = []

class Pedestrian( Component ):
	def __init__( self ):
		super( Pedestrian, self ).__init__( ComponentType.Pedestrian )
		self.direction = None
		self.distance = 0.

class PedestrianSystem( System ):
	def __init__( self ):
		super( PedestrianSystem, self ).__init__()
		self.tilemap = None

	def update( self, ent ):
		if ent.has_component( ComponentType.Tilemap ):
			self.tilemap = ent.get_component( ComponentType.Tilemap )

		if self.tilemap is None:
			return
		if not ent.has_component( ComponentType.Pedestrian ):
			return

		ped = ent.get_component( ComponentType.Pedestrian )

		pos = ent.transform().position
		tx, ty = int(pos[0]/16), int(pos[1]/16)
		if ped.direction is None:
			dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
			shuffle( dirs )

			for d in dirs:
				if self.tilemap.flags[tx+d[0]][ty+d[1]] & Tilemap.Pedestrian:
					ped.direction = d

		else:
			ent.transform().position += [
				ped.direction[0] * 0.1, ped.direction[1] * 0.1, 0. ]
			ped.distance += 0.1

			if ped.distance > 16.:
				d = ped.direction
				if not self.tilemap.flags[tx+d[0]][ty+d[1]] &Tilemap.Pedestrian:
					ped.direction = None
				ped.distance = 0.

class Animation( Component ):
	def __init__( self ):
		super( Animation, self ).__init__( ComponentType.Animation )
		self.frames = []
		self.playing = False

class AnimationSystem( System ):
	def __init__( self ):
		super( AnimationSystem, self ).__init__()

	def update( self, ent ):
		pass

class StackEventSystem( EventSystem ):
	def __init__( self ):
		super( StackEventSystem, self ).__init__()
		self.handlers = []
		self.running = True

	def push( self, handler ):
		self.handlers.append( handler )

	def handle_quit( self ):
		self.running = False

	def handle_keyboard( self, code, down ):
		for h in self.handlers[::-1]:
			if h.handle_keyboard( code, down ):
				break

	def handle_mouse_move( self, x, y, dx, dy ):
		for h in self.handlers[::-1]:
			if h.handle_mouse_move( x, y, dx, dy ):
				break

	def handle_mouse_click( self, button, x, y, down ):
		for h in self.handlers[::-1]:
			if h.handle_mouse_click( button, x, y, down ):
				break

class FileEventHandler( RocketEventListener ):
	def __init__( self, tilechooser ):
		super( FileEventHandler, self ).__init__()
		self.tilechooser = tilechooser

	def process_event( self, event ):
		filename = event.get_string_parameter( b'filename', b'' )
		if not filename:	return

		self.tilechooser.set_string_attribute( 
			b'tileset', bytes(filename, 'ascii') )

class TilemapEventHandler( RocketEventListener ):
	def __init__( self, tilemap ):
		super( TilemapEventHandler, self ).__init__()

	def process_event( self, event ):
		filename = event.get_string_parameter( b'filename', b'' )
		action = event.get_string_parameter( b'action', b'' )
		print( action, filename )
		if action == 'load':
			tilemap.load( filename )
		elif action == 'save':
			tilemap.save( filename )
		
class TileEventHandler( RocketEventListener ):
	def __init__( self ):
		super( TileEventHandler, self ).__init__()

	def process_event( self, event ):
		pass

class GameEventSystem( System ):
	def __init__( self, world, tilechooser, tileoptions, tilemap ):
		super( GameEventSystem, self ).__init__()
		
		#TODO This crashes program on shutdown
		self.world = world

		self.tilechooser = tilechooser
		self.tileoptions = tileoptions
		self.tilemap = tilemap

		self.keys = defaultdict( bool )
		self.mousedown = False

		self.rotate = 0.
		self.translate = 0.

		self.rotate_speed = 1. / 20.
		self.translate_speed = 1. / 1.

	def handle_keyboard( self, code, down ):
		if code == Scancode.KI_A:
			self.rotate = down * -1.0
		elif code == Scancode.KI_D:
			self.rotate = down * 1.0
		elif code == Scancode.KI_W:
			self.translate = down * 1.0
		elif code == Scancode.KI_S:
			self.translate = down * -1.0
		self.keys[ code ] = down

	def _set_tile( self, x, y ):
		settile = self.tileoptions.get_element_by_id( b'settile' )
		settile =  settile.has_attribute( b'checked' )

		collide = self.tileoptions.get_element_by_id( b'collidable' )
		collide = collide.has_attribute( b'checked' )

		pedestrian = self.tileoptions.get_element_by_id( b'pedestrian' )
		pedestrian = pedestrian.has_attribute( b'checked' )

		if settile:
			tx = self.tilechooser.get_int_attribute( b'tile_x', 0 )
			ty = self.tilechooser.get_int_attribute( b'tile_y', 0 )
			self.tilemap.tiles[ int(x/16) ][ int(y/16) ] = (tx, ty)

		flags = self.tilemap.flags[ int(x/16) ][ int(y/16) ]
		if collide:		flags |= Tilemap.Collidable
		else:			flags &= ~Tilemap.Collidable

		if pedestrian:	flags |= Tilemap.Pedestrian
		else:			flags &= ~Tilemap.Pedestrian

		self.tilemap.flags[ int(x/16) ][ int(y/16) ]  = flags

	def handle_mouse_move( self, x, y, dx, dy ):
		if self.mousedown:
			self._set_tile( x, y )
		return False

	def handle_mouse_click( self, button, x, y, down ):
		self.mousedown = down
		self._set_tile( x, y )
		return True

	def update( self, entity ):
		if not entity.has_component( ComponentType.Player ):
			return

		car = entity.get_component( ComponentType.Car )
		car.acceleration = max( 0., self.translate )
		car.braking = -min( 0., self.translate )
		car.steering_angle = self.rotate * 0.05

		transform = entity.transform()
		if self.keys[ Scancode.KI_Q ]:
			pos = transform.position + transform.up() * 20. + \
				transform.forward() * 0.1
			bullet = create_bullet( pos, transform.rotation )
			physics = bullet.get_component( ComponentType.Physics )
			physics.velocity = transform.up() * 30.
			self.world.add_entity( bullet )
			self.keys[ Scancode.KI_Q ] = False

		#transform = entity.transform()
		#transform.rotate( [0., 0., self.rotate * self.rotate_speed] )
		#transform.translate_relative( 
			#[0., self.translate * self.translate_speed, 0. ] )

class UIUpdateSystem( System ):
	def __init__( self, ui ):
		super( UIUpdateSystem, self ).__init__()

		self.ui = ui
		self.weapon_img = ui.get_element_by_id( b'weapon_icon' )
		self.weapon_name = ui.get_element_by_id( b'weapon_name' )
		self.weapon_ammo = ui.get_element_by_id( b'weapon_ammo' )

	def update( self, ent ):
		if not ent.has_component( ComponentType.Player ):
			return

		inventory = ent.get_component( ComponentType.Inventory )
		item = inventory.selected_item

		if True or item is None:
			self.weapon_img.set_string_attribute( b'src', b'pistol.bmp' )
		
if __name__ == "__main__":
	from event import PyEventSystem
	from random import random

	world = World()
	screen_system = ScreenSystem( 800, 600 )
	world.add_system( screen_system )

	ui_system = RocketSystem()
	ui_system.load_font( "assets/Anonymous_Pro.ttf" )
	world.add_system( ui_system )

	world.add_system( MeshRendererSystem() )
	world.add_system( TilemapSystem() )
	world.add_system( TilemapEntitySystem( world ) )
	world.add_system( PedestrianSystem() )
	world.add_system( PickupSystem() )

	bullet_system = BulletSystem( world )
	world.add_system( bullet_system )

	world.add_system( CollisionSystem2D() )

	camera = Entity()
	camera.add_component( Transform( [0., 0., 0.], [0., 0., 0.] ) )
	camera.add_component( Camera( 0, 800, 600, 0, -1, 1 ) )
	camera.add_component( Component( ComponentType.MouseControlled ) )
	world.add_entity( camera )

	player = create_car( [80., 80., 0.] )
	player.add_component( Component( ComponentType.Player ) )
	player.add_component( Inventory() )
	world.add_entity( player )

	pickup = create_pickup( [88., 88., 0.], Inventory.Uzi )
	world.add_entity( pickup )

	#bullet = create_bullet( [150., 150., 0.], [0.]*3 )
	#world.add_entity( bullet )

	worldmap = create_tilemap( 16 )
	tilemap = worldmap.get_component( ComponentType.Tilemap )
	world.add_entity( worldmap )

	menu = Entity()
	tile_menu = RocketDocument( "assets/tiles.rml" )
	file_menu = RocketDocument( "assets/file.rml" )
	game_ui = RocketDocument( "assets/ui.rml" )

	world.add_system( UIUpdateSystem( game_ui ) )

	tilehandler = TileEventHandler()
	tilechooser = tile_menu.get_element_by_id( "tiles" )
	tileoptions = tile_menu.get_element_by_id( "tile_options" )
	tilechooser.add_event_listener( b"click", tilehandler, False )

	filehandler = FileEventHandler( tilechooser )
	tile_menu.get_element_by_id( "load_file" ).add_event_listener(
		b'submit', filehandler, False )

	tilemaphandler = TilemapEventHandler( tilemap )
	file_menu.get_element_by_id( "file_manager" ).add_event_listener(
		b"submit", tilemaphandler, False )

	menu.add_component( tile_menu )
	menu.add_component( file_menu )
	world.add_entity( menu )

	event_system = GameEventSystem( world, tilechooser, tileoptions, tilemap )
	world.add_system( event_system )

	input_system = StackEventSystem()
	input_system.push( event_system )
	input_system.push( ui_system )
	world.add_system( input_system )

	world.add_system( CarSystem() )

	while input_system.running:
		world.update()

	#TODO needed to avoid circular reference
	event_system.world = None
	bullet_system.world = None
	

