
import pygame
from pygame.locals import *

from vector import *

import renderer
import event_handler
import world

pygame.init()
rend = renderer.renderer( vector2( 800, 600 ) )

hand = event_handler.handler()
scene = world.world( rend, hand )

while True:
    
    event = hand.process()
    if event and event.type == pygame.QUIT:
        break

    scene.update()

pygame.quit()
