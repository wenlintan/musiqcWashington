import pygame, globals

class Object:
    width = 1
    color = (50, 200, 50)    #greenish, where's the rgb table when you need it

    draw_name = False
    font_render = None
    
    def __init__(self, points = None):
        self.points = points
        if points is None:
            self.points = []

    def add_point(self, point):
        self.points.append(point)

    def set_width(self, width):
        self.width = width

    def set_color(self, color):
        self.color = color
        self.font_render = None

    def set_name(self, name):
        self.name = str(name)
        self.font_render = None

    def draw_name(self, state):
        self.draw_name = state
    
    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.points, self.width)

        if self.draw_name and globals.font_available:
            if self.font_render is None:
                self.font_render = globals.font.render(self.name, 1, self.color)

            avex, avey = 0,0
            for i in range( len(self.points) ):
                avex += points[i][0]
                avey += points[i][1]

            avex /= len(self.points)
            avey /= len(self.points)

            width, height = globals.font.size(self.name)
            avex -= width / 2
            avey -= height / 2
            
            screen.blit(self.font_render, (avex, avey) )

        
        
