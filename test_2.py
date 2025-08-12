from renderer import *
from camera import *
from physical_object import *
from space import *
from ray import *
import timeit

"""
Things to add:
    Rotation and translation of solids and surfaces
    Wire frame (return the object that each ray hits, render that ray black if it is a different surface than neighbor.
"""
renderer = Renderer(800,600)
space= Space(400,400,400)
renderer.add_space(space)
camera = Camera()
renderer.add_camera(camera)
v1 = Vertex(3,0,3)
v2 = Vertex(3,0,9)
v3 = Vertex(0,3,6)
v4 = Vertex(-3,0,3)
v5 = Vertex(-3,0,9)
s1 = Surface(v1,v2,v3)  # Center = (2,1,6)
s1.set_color('green')
v4 = Vertex(-3,0,3)
s2 = Surface(v1,v3,v4)  # Center = (0,1,4)
s2.set_color('red')
s3 = Surface(v3,v4,v5)  # center = (-2,1,6
s3.set_color('yellow')
s4 = Surface(v3,v5,v2)  # center = (0,1,8)
s4.set_color('orange')
solid = Solid('asd',s1,s2,s3,s4)
renderer.add_solid(solid)
renderer.create_window()