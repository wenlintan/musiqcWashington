import pygame
from pygame.locals import *

class Console:
    def __init__(self, screen, rect):
        self.buf = []
        self.drawn = []
        self.r = rect
        self.s = screen

        self.f = pygame.font.SysFont("Helvetica", 15)
        self.draw_change = 0
        self.line_change = 0
        

    def add_buffer(self, data):
        cur_size = 0
        if len(buf):
            cur_size = self.f.size( buf[ len(buf)-1 ] )
            
        while len(data):
            insert = ""
            try:
                newend = data.index("\n")
                if self.f.size(data[:newend])[0] > self.r.width:
                    raise ValueError

                insert = data[:newend]
                data = data[newend+1:]
            except ValueError:
                newend = min( [self.r.w / 12, len(data)] )

                while self.f.size(data[:newend])[0] < self.r.width and newend < len(data):
                    newend += 1

                while self.f.size(data[:newend])[0] > self.r.width:
                    newend -= 1

                print data[newend:]
                #skip to the beginning of this word
                oldnewend = newend
                while (not data[newend:newend+1].isspace()) and newend > 0:
                    newend -=1
                if newend == 0:
                    newend = oldnewend  #word is whole line

                insert = data[:newend]
                data = data[newend:]
                print data

            self.buf.append( insert )
            self.draw_change += self.f.size( insert )[1]
            self.line_change += 1

            self.drawn.append( self.f.render(insert, True, (255,0,0), (0,0,0)) )

    def draw(self):
        screen = self.s
        drawn = self.drawn
        
        lo = self.r.bottom
        ls = self.f.get_linesize()
        pos = len(drawn) -1

        while lo - ls > self.r.top and pos > 0:
            screen.blit(drawn[pos], (self.r.left, lo-ls))
            
            lo -= ls
            pos -= 1

        if len( drawn ):
            h_clip = min( [ls, lo - self.r.height] )
            r = Rect(0, ls - h_clip, drawn[pos].get_size()[0], h_clip)

            screen.blit(drawn[pos], (self.r.left, lo-h_clip), r)
            
            
            
        

class Command:
    def __init__(self, screen, rect):
        self.r = rect
        self.s = screen

        self.buf = ""

    def add_input(self, char):
        self.buf += char

    def draw(self):
        pass
