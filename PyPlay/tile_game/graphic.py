import image, player

import pygame
from pygame.locals import *

class Graphics:
    images = {}
    tiles = {}
    nicks = {}

    def __init__(self):
        self.width = 640.0 /32.0
        self.height = 480.0 /32.0
        
        self.screen = pygame.display.set_mode( (640, 480), 0, 24)
        self.screen.fill((0,0,0))

        self.player = player.Player([1.0, 1.0])

    def load_image(self, char, name):
        if not char in self.images.keys():
            try:
                self.images[char] = pygame.image.load(name)
            except pygame.error, message:
                print "Error loading image:", name
                raise SystemExit, message


    def create_tile(self, char, imagename, pos, level, options):
        if not imagename in self.images.keys():
            self.load_image(imagename, imagename)
            
        if not char in self.tiles.keys():
            pic = self.images[imagename]
            self.tiles[char] = image.Tile( pic, pos, level, options)

            if 'N' in options:
                nick = options [ options.find('N') +1 ]
                self.nicks[nick.strip()] = char
                print nick, char

    

    def create_world(self, data):
        self.x = len(data[0])
        self.y = len(data)

        for y in range(self.y):
            for x in range(self.x):
                try:
                    data[y][x] = data[y][x].strip()
                    print data[y][x]
                    data[y][x] = self.nicks[data[y][x]]
                except KeyError:
                    pass

        self.world = data

    def draw(self):
        self.screen.fill((0,0,0))

        self.player.move()
        startx = self.player.pos[0]  - self.width / 2.0
        starty = self.player.pos[1] - self.height / 2.0

        fracx = -startx + int(startx)
        fracy = -starty + int(starty)

        startx = int(startx)
        starty = int(starty)
        
        drawrect = pygame.Rect(fracx * 32.0, fracy * 32.0, 32.0, 32.0)

        for y in range(starty, starty+self.height):
            for x in range(startx, startx+self.width):
                if y > -1 and x > -1 and y < self.y and x < self.x:
                    tile = self.tiles[self.world[y][x]]
                    self.screen.blit(tile.image, drawrect, tile.rect)

                drawrect.move_ip(32.0, 0)

            drawrect.left = fracx * 32.0
            drawrect.move_ip(0, 32.0)

        player_rect = pygame.Rect(640.0 / 2.0 - 8.0,480.0 / 2.0 - 8.0,16,16)
        self.player.draw(self.screen, player_rect)
        
        pygame.display.flip()
        
    
