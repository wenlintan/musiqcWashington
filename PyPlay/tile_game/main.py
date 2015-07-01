import filereader, pygame

pygame.init()
mainfile = filereader.File("world.txt")
graphics = mainfile.get_graphics()


if __name__ == "__main__":
    Run = True
    while Run:
        pygame.event.pump()
        event = pygame.event.poll()
        while event.type != pygame.NOEVENT:
            if event.type == pygame.QUIT:
                Run = False
            event = pygame.event.poll()
        
        graphics.draw()
