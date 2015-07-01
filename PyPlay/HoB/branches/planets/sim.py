
from simulation import *

from flags import *
from event import *

world = World()
screen_system = ScreenSystem( 800, 600 )
world.add_system( screen_system )

world.add_system( MeshRendererSystem() )
world.add_system( SphericalROAMSystem() )

event_system = PyEventSystem()
world.add_system( event_system )
world.add_system( FollowSystem() )

camera = Entity()
camera.add_component( Transform( [0., 0., -1.2], [-3.14, 0., 0.] ) )
cam = Camera( 70., 800. / 600., 0.001, 10. )
cam.flags = FinalRenderFlag
camera.add_component( cam );
camera.add_component( Component( ComponentType.MouseControlled ) )
world.add_entity( camera )

sky = Entity()
sky.add_component( AABBMesh( [-.5, -.5, -.5], [1., 1., 1.] ) )
sky.add_component( MeshRenderer( FinalRenderFlag ) )
world.add_entity( sky )

while event_system.running:
	world.update()
