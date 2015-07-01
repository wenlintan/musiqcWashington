import pygame, math
from pygame.locals import *

class Player:
    speed = .07
    car_speed = .2
    
    def __init__(self, startpos):
        self.pos = startpos
        self.rot = 0.0
        self.image = []
        try:
            for i in range(1):
                self.image.append(pygame.image.load("player_" + str(i) + ".bmp"))
                self.image[i].set_colorkey((255,255,255))
        except pygame.error, message:
            print "Error laoding player image"
            raise SystemExit, message

    def move(self):
        bools = pygame.key.get_pressed()
        if bools[K_RIGHT]:
            self.rot += math.pi / 64.0
            if self.rot > 2.0* math.pi:
                self.rot = 0.0
                
        if bools[K_LEFT]:
            self.rot -= math.pi / 64.0
            if self.rot < 0.0:
                self.rot = 2.0* math.pi
                
        if bools[K_DOWN]:
            self.pos[0] -= math.cos(self.rot) * self.speed
            self.pos[1] -= math.sin(self.rot) * self.speed
        if bools[K_UP]:
            self.pos[0] += math.cos(self.rot) * self.speed
            self.pos[1] += math.sin(self.rot) * self.speed

    def draw(self, screen, rect):
        degrees = self.rot + math.pi / 2.0
        degrees = degrees * 180.0 / math.pi
        degrees = -degrees
        tempscreen = pygame.transform.rotate(self.image[0], degrees)
        screen.blit(tempscreen, rect)
        
