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
renderer = Renderer(50,25)
space= Space(400,400,400)
renderer.add_space(space)
camera = Camera()
renderer.add_camera(camera)
v1 = Vertex(np.array([3,0,3]), 'indigo')
v2 = Vertex(np.array([3,0,9]), 'green')
v3 = Vertex(np.array([0,3,6]), 'yellow')
v4 = Vertex(np.array([-3,0,3]), 'orange')
v5 = Vertex(np.array([-3,0,9]), 'blue')
s1 = Surface(v1,v2,v3)  # Center = (2,1,6)
v4 = Vertex(np.array([-3,0,3]),'pink')
s2 = Surface(v1,v3,v4)  # Center = (0,1,4)
s3 = Surface(v3,v4,v5)  # center = (-2,1,6
s4 = Surface(v3,v5,v2)  # center = (0,1,8)
solid = Solid(s1,s2,s3,s4)
renderer.add_object(solid)
renderer.create_window()