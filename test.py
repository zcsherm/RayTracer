from renderer import *
from camera import *
from physical_object import *
from space import *
from ray import *
import timeit

def v(x, y, z):
    return Vertex(np.array([x, y, z]))

renderer = Renderer(50,50)
space= Space(400,400,400)
renderer.add_space(space)
camera = Camera()
renderer.add_camera(camera)
v1 = v(-1, 0, 5)
v2 = v(0, 1.72, 5)
v3 = v(1, 0, 5)
s1 = Surface(v1,v2,v3)
s1.set_color('green')
print(s1.color())
s1 = Solid(s1)
renderer.add_object(s1)


v1 =v(-20, 0, 15)
v2 =v(0, 1.72, 15)
v3 = v(1, 0, 15)
s1 = Surface(v1,v2,v3)
s1.set_color('black')
s1 = Solid(s1)
renderer.add_object(s1)
"""
v1 = v(5, 0, 1)
v2 = v(5, 1.72, 0)
v3 = v(5, 0, -1)
s1 = Surface(v1,v2,v3)
s1.set_color('yellow')
s1 = Solid(s1)
renderer.add_object(s1)
v1 = v(-1, 0, -50)
v2 = v(0, 1.72, -50)
v3 = v(1, 0, -50)
s1 = Surface(v1,v2,v3)
s1.set_color('orange')
s1 = Solid(s1)
renderer.add_object(s1)
v1 = v(12,12,33)
v2 = v(25,25,33)
v3 = v(12,25,33)
s1 = Surface(v1,v2,v3)
s1.set_color('red')
s1 = Solid(s1)
renderer.add_object(s1)
"""
renderer.create_window()