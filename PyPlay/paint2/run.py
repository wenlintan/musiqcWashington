
import pygame, sys
from pygame.locals import *

from vector import *
import constants

import renderer
import event_handler
import network
import world

server = False
for arg in sys.argv:
    
    if arg == '-s' or arg == '-server':
        server = True

try:
    if server:  net = network.server( constants.port )
    else:       net = network.client( "127.0.0.1", constants.port )
except AttributeError, e:
    print "ERROR: in connection, %s" % e
    sys.exit(-1)

pygame.init()
rend = renderer.renderer( vector3( constants.width, constants.height ) )
hand = event_handler.handler()
scene = world.world( rend, hand, net )

while True:
    
    event = hand.process()
    if event and event.type == pygame.QUIT:
        break
    scene.update()
    
pygame.quit()
