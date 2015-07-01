import pygame

class Tile:
    def __init__(self, image, pos, level, options):
        self.image = image
        self.rect = pygame.Rect(pos[0], pos[1], 32, 32)
        
        self.pos = pos
        self.level = level

        if 's' in options:
            self.slope = options[ options.find('s') + 1 ]
        else:
            self.slope = 'O'
