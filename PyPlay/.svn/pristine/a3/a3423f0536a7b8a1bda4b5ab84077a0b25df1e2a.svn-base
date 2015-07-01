import pygame
import imageparser, globals

pygame.init()

try:
    image = pygame.image.load("bent-nail.jpg")
    array = pygame.surfarray.array3d(image)
    rect = image.get_rect()
    
    screen = pygame.display.set_mode( (rect.width, rect.height), 0, 24)
    screen.fill((0,0,0))
    globals.screen = screen # use only for debugging
    
    parse = imageparser.ImageParser(array)
    

except pygame.error, message:
    print "Error loading image"
    raise SystemExit, message


if __name__ == "__main__":
    Run = True
    while Run:
        pygame.event.pump()
        event = pygame.event.poll()
        while event.type != pygame.NOEVENT:
            if event.type == pygame.QUIT:
                Run = False
            event = pygame.event.poll()
            
        screen.blit(image, pygame.Rect(0, 0, 0, 0) )

        parse.draw_objects(screen)
        pygame.display.flip()
        
