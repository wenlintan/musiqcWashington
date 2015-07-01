
import math

from pygame.locals import *
import pygame

import random
tile_width = 64
tile_height = 64
colors = [ (200,0,0), (0,200,0), (0,0,200) ]

class Snood:
    def __init__( self, color ):
        self.color = color

    def place( self, x, y ):
        self.x = x
        self.y = y

        self.rect = Rect( (x,y), (tile_width,tile_height) )

    def draw( self, screen ):
        pygame.draw.rect( screen, self.color, self.rect )

class Blank( Snood ):
    def __init__( self ):
        self.color = (0,0,0)

class Level:
    def __init__( self, height, x, length ):
        self.length = length
        self.offset = x
        
        self.height = height

        self.snoods = []
        for i in range( self.length ):
            b = Blank()
            b.place( i*tile_width + self.offset, self.height )
            self.snoods.append( b )

    def populate( self ):
        

        for i in range( self.length ):
            c = random.choice( colors )
            self.snoods[ i ] = Snood( c )
            self.snoods[ i ].place( i*tile_width + self.offset, self.height )

class Grid:
    def __init__( self, screen, height, width ):

        self.screen = screen
        self.levels = []
        
        for i in range( height ):
            offset = 0
            if i % 2 == 1:
                offset = tile_width / 2
                
            self.levels.append( Level( i*tile_height, offset, width ) )

        self.current_snood = self.create_snood ()
        self.queued_snood = self.create_snood ()

        scr_width, scr_height = screen.get_size()
        self.scr_width, self.scr_height = screen.get_size()
        
        self.queued_snood.place (scr_width - tile_width, scr_height - tile_height)
        self.current_snood.place ((scr_width - tile_width)/2, scr_height - tile_height)

        self.snood_velocity = 15.0
        self.snood_velx, self.snood_vely = 0.0, 0.0
        self.snood_posx, self.snood_posy = self.current_snood.x, self.current_snood.y
        
        self.snood_moving = False
        
    def create_snood( self ):
        c = random.choice( colors )
        s = Snood (c)
        return s
        
    def draw_snood( self, snood ):
        snood.draw( self.screen )

    def update( self, dt ):

        b1,b2,b3 = pygame.mouse.get_pressed()
        if not self.snood_moving and b1:
            posx, posy = pygame.mouse.get_pos()
            vx, vy = posx - self.scr_width/2, (posy - self.scr_height)

            l = math.sqrt( vx*vx + vy*vy )
            scale = self.snood_velocity / l

            self.snood_velx = vx * scale
            self.snood_vely = vy * scale
            self.snood_moving = True

        elif self.snood_moving:
            self.snood_posx += self.snood_velx*dt
            self.snood_posy += self.snood_vely*dt

            self.current_snood.place( int(self.snood_posx), int(self.snood_posy) )
        
        

    def draw( self ):
        for l in self.levels:
            for s in l.snoods:
                self.draw_snood( s )
                
        self.draw_snood (self.queued_snood)
        self.draw_snood (self.current_snood)

    def populate( self ):
        for l in self.levels:
            l.populate()
        

        
