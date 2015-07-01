import pygame

from vector3 import *
import shapes, voxel, scene, render, material

#create some materials
red_mat = material.material( vector3(),                     #emissive
                             vector3(96.0, 66.0, 66.0),     #ambient
                             vector3(96.0, 66.0, 66.0),     #diffuse
                             vector3(),                     #specular
                             20.0,                          #shininess
                             0.0 )                          #reflectivity

grey_mat = material.material( vector3(),
                              vector3(96.0, 96.0, 96.0),
                              vector3(96.0, 96.0, 96.0),
                              vector3(),
                              20.0,
                              0.0 )

bluegrey_mat = material.material( vector3(),
                                  vector3(66.0, 66.0, 96.0),
                                  vector3(66.0, 66.0, 96.0),
                                  vector3(),
                                  20.0,
                                  0.0 )

orange_mat = material.material( vector3(),
                                vector3(238.0, 154.0, 73.0),
                                vector3(238.0, 154.0, 73.0),
                                vector3(255.0, 255.0, 255.0),
                                20.0,
                                0.0 )

purple_mat = material.material( vector3(),
                                vector3(222.0, 60.0, 222.0),
                                vector3(222.0, 60.0, 222.0),
                                vector3(222.0, 60.0, 222.0),
                                20.0,
                                0.0 )

refl_mat = material.material( vector3(),
                              vector3(0.0, 0.0, 0.0),
                              vector3(25.0, 25.0, 25.0),
                              vector3(150.0, 150.0, 150.0),
                              20.0,
                              0.4 )
                              

light_mat = material.material( vector3(255.0, 255.0, 255.0),
                               vector3(),
                               vector3(),
                               vector3(),
                               10.0,
                               0.0 )
                             
                             
                             

#create some geometry
p1 = shapes.plane( vector3(0.0, -5.0, 0.0),     #point in plane
                   vector3(0.0, 1.0, 0.0),      #plane normal
                   red_mat )                    #plane material

p2 = shapes.plane( vector3(0.0, 5.0, 0.0),
                   vector3(0.0, -1.0, 0.0),
                   red_mat )

p3 = shapes.plane( vector3(-5.0, 0.0, 0.0),
                   vector3(1.0, 0.0, 0.0),
                   grey_mat )

p4 = shapes.plane( vector3(5.0, 0.0, 0.0),
                   vector3(-1.0, 0.0, 0.0),
                   grey_mat )

p5 = shapes.plane( vector3(0.0, 0.0, -10.0),
                   vector3(0.0, 0.0, 1.0),
                   bluegrey_mat )

p6 = shapes.plane( vector3(0.0, 0.0, 10.0),
                   vector3(0.0, 0.0, -1.0),
                   bluegrey_mat )

s1 = shapes.sphere( vector3(-2.0, 2.0, -5.0),      #center point
                    1.0,                           #radius
                    orange_mat )                   #material

s2 = shapes.sphere( vector3(2.0, 2.0, -5.0),      #center point
                    1.0,                          #radius
                    orange_mat )                  #material

s3 = shapes.sphere( vector3(0.0, -1.0, -6.0),
                    1.5,
                    bluegrey_mat )

s4 = shapes.sphere( vector3(0.0, 2.0, -7.0),
                    2.0,
                    refl_mat )

v1 = voxel.voxel_tree( vector3(0.0, 2.0, -7.0),
                       vector3(256, 256, 128) )
v1.create_sphere( vector3(128, 128, 64), 32, bluegrey_mat )

#create some lights
material.material.ambient = vector3(70.0, 70.0, 70.0) / 255.0

l1 = material.point_light( vector3(2.0, -2.0, -3.0),        #location
                           20.0,                            #distance falloff term
                           vector3(150.0, 20.0, 20.0),      #diffuse component
                           vector3(255.0, 50.0, 50.0) )   #specular component

l2 = material.point_light( vector3(-2.0, -2.0, -3.0),
                           20.0,
                           vector3(20.0, 20.0, 150.0),
                           vector3(50.0, 50.0, 255.0) )

l3 = material.square_light( vector3(-0.25, 4.99, -3.75),
                            0.5,
                            -0.5,
                            20.0,
                            vector3(255.0, 255.0, 255.0),
                            vector3(255.0, 255.0, 255.0) )

pygame.init()
scene = scene.scene()
scene.shapes = [p1, p2, p3, p4, p5, p6, v1]
scene.lights = [l1]
scene.select_collides()

rend = render.render( scene )

start = pygame.time.get_ticks()
success = rend.render()
end = pygame.time.get_ticks()

seconds = (end-start) / 1000.0
minutes = int(seconds) / 60
seconds = seconds - (minutes*60.0)

print "Render took %d:%f (minutes:seconds)" % (minutes, seconds)

#if success:
#    success = rend.anti_alias_dither()

#if we succeeded in drawing the whole thing
#let it sit until we get user input
#otherwise we want to quit now
while success:
    
    pygame.time.wait(20)
    event = pygame.event.poll()
    while event.type != pygame.NOEVENT:
        if event.type == pygame.QUIT:
            success = False
        event = pygame.event.poll()
        
    pygame.display.flip()

pygame.quit()


