import pygame
from pygame.locals import *

import scene, math, random, shapes
from vector3 import *

class render:
    def __init__(self, scene):
        "Arguments: scene object containing geometry"
        self.scene = scene

        # define screen dimensions
        self.w = 800
        self.h = 600

        self.hw = self.w/2
        self.hh = self.h/2
        self.distort = float(self.w) / float(self.h)

        #define viewing angle
        self.fov = 70.0 * math.pi / 180.0
        self.tanfov = math.tan( self.fov / 2.0 )

        #base at origin looking down z axis for now
        self.pos = vector3()
        self.look = vector3(0.0, 0.0, -1.0)
        self.up = vector3(0.0, 1.0, 0.0)
        self.right = self.look.crossp( self.up )

        self.screen = pygame.display.set_mode( (self.w,self.h), 0, 24 )
        self.screen.fill( (0,0,0) )

    def test_one(self):
        p = vector3()
        d = vector3(0.0, 0.0, -1.0)
        self.scene.collide( shapes.ray(p, d) )
        return

    def render_ray(self, xfactor, yfactor):
        "Renders a single ray at the fraction of the screen specified"
        
        #generate ray for this pixel
        d = ( self.look + self.right * xfactor * self.tanfov +
              self.up * -yfactor * self.tanfov )
        r = shapes.ray(self.pos, d)

        intersect = self.scene.collide( r )

        #see if we managed to hit anything
        if not intersect:
            self.intersect_info = ()
            return vector3()

        color = intersect.surf.m.color( self.scene, intersect, self.pos )
        self.intersect_info = intersect.surf.m.info
        return color

    def render(self):
        "Draws and displays an image"
        i = 0

        screen = self.screen
        #pixels = [ (x,y) for y in range(self.h) for x in range(self.w) ]

        lastrow = [()] * self.w
        last = ()

        #define variables for half of change between pixels
        #used during supersampling
        hdeltax = 0.5 * self.distort / float(self.w/2)
        hdeltay = 0.5 / float(self.h/2)

        #create the deltas to be added for supersampling
        #remove the center one because we'll have already calculated that
        #color to determine that we should supersample
        deltas = [ (x*hdeltax*self.distort, y*hdeltay) for x in range(-1,2)
                                                       for y in range(-1,2) ]
        del deltas[4]

        #create some local variables just to avoid self lookups
        hw = self.w/2
        hh = self.h/2
        
        dxfactor = self.distort / float(hw)
        dyfactor = 1.0 / float(hh)

        render_ray = self.render_ray
        
        screen.lock()
        for y in range(self.h):
            for x in range(self.w):
                #calculate the x and y components of the ray through this pixel
                dx = (x - hw) * dxfactor
                dy = (y - hh) * dyfactor
                
                color = render_ray( dx, dy )

                #info contains surfaces and number of lights involved
                #if any of this info changes then we're at a boundary condition
                #and we'll run supersampling
                newinfo = self.intersect_info
                
                if ( ( newinfo != last and len(last) ) or
                     ( newinfo != lastrow[x] and len(lastrow[x]) ) ):
                    
                    # super sample to antialias this color change
                    # start accumulator with original color
                    accumulator = color
                    for d in deltas:
                        newdx = dx + d[0]
                        newdy = dy + d[1]
                        
                        accumulator += render_ray( newdx, newdy )

                    raw_color = (accumulator / 9.0).raw
                    screen.set_at( (x,y), raw_color )

                    # next we're going to recompute the color in the direction
                    # that doesn't match this one
                    if newinfo != last and len(last):
                        newx = x-1
                        newy = y
                    else:
                        newx = x
                        newy = y-1

                    #calculate the x and y components of the ray through this pixel
                    dx = (newx - hw) * dxfactor
                    dy = (newy - hh) * dyfactor

                    accumulator = raw_to_vec3( screen.get_at( (newx,newy) ) )
                    for d in deltas:
                        newdx = dx + d[0]
                        newdy = dy + d[1]
                        
                        accumulator += render_ray( newdx, newdy )

                    raw_color = (accumulator / 9.0).raw
                    screen.set_at( (newx,newy), raw_color )

                else:
                    raw_color = color.raw
                    screen.set_at( (x,y), raw_color )

                last = lastrow[ x ] = newinfo

                #wait a set number of loops and then let the system know
                #we aren't dead
                i = i+1
                if i%self.w == 0:
                    event = pygame.event.poll()
                    while event.type != pygame.NOEVENT:
                        if event.type == pygame.QUIT:
                            return False
                        event = pygame.event.poll()

                    screen.unlock()
                    pygame.display.flip()
                    screen.lock()

            #reset this for next row
            last = ()
            
        return True

    def anti_alias_dither(self):
        "Assumes image has already been drawn to self.screen, then anti-aliases"
        i = 0
        for y in range(1, self.h-1):
            for x in range(1, self.w-1):
                this = raw_to_vec3( self.screen.get_at( (x,y) ) )
                
                right = raw_to_vec3( self.screen.get_at( (x+1,y) ) )
                self.screen.set_at( (x+1,y), (this*0.44 + right*0.56).raw )

                down = raw_to_vec3( self.screen.get_at( (x,y+1) ) )
                self.screen.set_at( (x,y+1), (this*0.31 + down*0.69).raw )

                dl = raw_to_vec3( self.screen.get_at( (x-1,y+1) ) )
                self.screen.set_at( (x-1,y+1), (this*0.19 + dl*0.81).raw )

                dr = raw_to_vec3( self.screen.get_at( (x+1,y+1) ) )
                self.screen.set_at( (x+1,y+1), (this*0.06 + dr*0.94).raw )

                i = i+1
                if i%10 == 0:
                    event = pygame.event.poll()
                    while event.type != pygame.NOEVENT:
                        if event.type == pygame.QUIT:
                            return False
                        event = pygame.event.poll()
                        
                    pygame.display.flip()
        return True

            
            
            
        
            
