
import serial
ser = serial.Serial(2, 19200)  # open first serial port
print ser.portstr       # check which port was really used

from pygame.locals import *
import pygame
pygame.init()

screen = pygame.display.set_mode( (800,600), 0, 32 )
ball_pos = [400,300]
ball = Rect( ball_pos, (8, 8) )
ball_color = ( 238, 154, 73 )

data = ""
running = True
accs_x = [ 0 ] * 5; accs_y = [ 0 ] * 5

while running:
    
    #poll input
    l = ser.readline()
    if len( l ):
        try:
            blocks = l.split( ':' )
            vals = [ int( b.strip()[:3] ) for b in blocks[ 1: ] ]
            x, y, accx, accy, accz = vals

            accs_x.append( accx-128 )
            accs_x = accs_x[1:]

            accs_y.append( accy-128 )
            accs_y = accs_y[1:]
            
        except ValueError:
            print "Bad data"

    new_accx = sum( accs_x ) / 5.
    new_accy = sum( accs_y ) / 5.

    print new_accx, new_accy
    ball_pos = [400+new_accx*5,300+new_accy*5]
    ball = Rect( ball_pos, (8, 8) )
    
    event = pygame.event.poll()
    while event.type != pygame.NOEVENT:
        
        if event.type == pygame.QUIT:
            running = False
            
        event = pygame.event.poll()
    
    #draw representation
    screen.fill( (0,0,0) )
        
    pygame.draw.rect( screen, ball_color, ball )
    pygame.display.flip()




while( 1 ):
    for i in range( 10 ):
        s = ser.read( 1 )
        print ord(s),
    print
        
##s = ser.read( 1000 )
##for i in range( 100 ):
##    for j in range( 10 ):
##        print ord( s[i*10+j] ),
##
##    print

ser.close()
