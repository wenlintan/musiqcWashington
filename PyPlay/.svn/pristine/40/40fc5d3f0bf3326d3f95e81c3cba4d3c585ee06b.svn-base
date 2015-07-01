import globals, object
import pygame, time
from Numeric import *

class SimplifiedPass:
    boundary = []
    
    def __init__(self, array):
        self.array = array
        self.build_array()
        self.build_objects()

    def build_array(self):
        self.simp_array = self.array
        
        for i in range(globals.num_reductions):
            for x in range( 1, len(self.simp_array) -1 ):
                for y in range(1, len(self.simp_array[0])-1 ):
                    c1 = self.simp_array[x][y-1]
                    c2 = self.simp_array[x-1][y]
                    c3 = self.simp_array[x+1][y]
                    c4 = self.simp_array[x][y+1]

                    r = c1[0] + c2[0] + c3[0] +c4[0]
                    g = c1[1] + c2[1] + c3[1] +c4[1]
                    b = c1[2] + c2[2] + c3[2] +c4[2]
                        
                    self.simp_array[x][y] = [ r/4.0, g/4.0, b/4.0 ]

        surf = pygame.surfarray.make_surface(self.simp_array)
        #pygame.image.save(surf, "still-blurry.bmp")

    def build_objects(self):
        print "getting objects"
        self.objects = []

        width, height = len(self.simp_array), len(self.simp_array[0])
        def valid(point):
            return  point[0] >= 0 and point[0] < width and   \
                    point[1] >= 0 and point[1] < height

        cur = [40,300]
        try:
            while globals.close_color_match(    self.simp_array[cur[0]][cur[1]],    \
                                                self.simp_array[cur[0]+1][cur[1]]     ):
                cur[0] += 1
        except IndexError:
            cur[0] -= 1     # hello wall

        start = cur = (cur[0], cur[1])
        start_list = [cur]
        open_list = []      # list of (dist, (x, y))
        open_objects = []
        closed_list= []
        locked_list = []
        temp_list = []

        distance_primed = False #have we moved away from the start far enough to trip the primer

        if globals.debug_simplified:
            img = pygame.surfarray.make_surface(self.simp_array)
            globals.screen.blit(img, img.get_rect())
            pygame.display.flip()
            
        while not len(start_list) == 0:
            cur = start_list.pop()
            open_list = [[0, cur]]      # list of (dist, (x, y))
            open_objects = [cur]

            del temp_list[:]
            del closed_list[:]
            del locked_list[:]
            print "new start ", cur
            
            while not len(open_list) == 0:
                data = open_list.pop(0)
                point = data[1]
                print data, self.simp_array[point[0]][point[1]]
                
                if not valid(point):
                    continue

                neighbors = [ (point[0], point[1]-1), (point[0]-1, point[1]),
                              (point[0]+1, point[1]), (point[0], point[1]+1) ]

                boundary = None
                for neighbor in neighbors:
                    if not neighbor in closed_list and not neighbor in locked_list and \
                       not neighbor in open_objects:
                        if not valid(neighbor) or \
                           not globals.close_color_match(   self.simp_array[neighbor[0]][neighbor[1]], \
                                                            self.simp_array[point[0]][point[1]] ):
                            if boundary is None or not valid(boundary):
                                boundary = neighbor
                                print "boundary: ", boundary, valid(boundary)
                        else:
                            temp_list.append([data[0]+1, neighbor])
                            print "open: ", neighbor
                        
                    
                if boundary is not None and not cur == point:
                    print point, cur

                    self.add_boundary_point(boundary)
                    locked_list.append(boundary)
                    locked_list.append(point)
                    cur = point

                    #check if we're done
                    if not distance_primed and abs(cur[0] - start[0]) + \
                       abs(cur[1] - start[1]) > globals.min_end_start_termination:
                        distance_primed = True
                    if distance_primed and abs(cur[0] - start[0]) + \
                       abs(cur[1]- start[1]) < globals.min_end_start_termination:
                        break   #my tank is fight!


                    if len(locked_list) > globals.locked_list_max_size:
                        locked_list = locked_list[-globals.locked_list_max_size:]   #take the end
                        
                    del closed_list[:]
                    del open_objects[:]     #we can't keep this because it doesn't have the same
                                            #indices as open_list, so we won't know what to delete

                    for x in open_list:
                        x[0] = abs(point[0] - x[1][0]) + abs(point[1] - x[1][1])
                    
                    for x in temp_list:
                        open_list.append([1, x[1]])
                        open_objects.append(x[1])
                    del temp_list[:]

                    open_list.sort()
                    for x in open_list:
                        if x[0] > globals.open_list_max_distance:
                            open_list = open_list[: open_list.index(x)]
                            break

                else:
                    print "close: ", point
                    closed_list.append(point)
                    
                    open_list.extend(temp_list)
                    for x in temp_list:
                        open_objects.append(x[1])

                    open_list.sort()
                    del temp_list[:]


                if boundary is not None and valid(boundary):
                        start_list.append(boundary)            #this is a place we can begin after this object
                
                if globals.debug_simplified:
                    surf = pygame.surfarray.make_surface(self.simp_array)
                    globals.screen.blit(surf, surf.get_rect())
                    
                    for x in open_list:
                        globals.screen.set_at(x[1], (50,200,50))
                    for x in closed_list:
                        globals.screen.set_at(x, (200,50,50))
                    for x in locked_list:
                        globals.screen.set_at(x, (200, 50, 200))
                    for x in self.boundary:
                        globals.screen.set_at(x, (50,50,200))
                    pygame.display.flip()

                pygame.event.pump()
                event = pygame.event.poll()
                while event.type != pygame.NOEVENT:
                    if event.type == pygame.QUIT:
                        return
                    event = pygame.event.poll()
                    
                #time.sleep(0.1)
            
            self.build_object()

    def add_boundary_point(self, point):
        self.boundary.append(point)

    def simplify_boundary(self):
        pass
    
    def build_object(self):
        self.simplify_boundary()
        
        bound = self.boundary
        del self.boundary[:]

        self.objects.append( object.Object(bound) )
        
    def get_objects(self):
        return self.objects

    def debug_draw_image(self, screen):
        surf = pygame.surfarray.make_surface(self.simp_array)
        screen.blit(surf, surf.get_rect())
        for obj in self.objects:
            for point in obj.points:
                screen.set_at(point, (250, 250, 250))
