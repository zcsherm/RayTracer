# Creates a physical space that objects reside in.
import numpy as np

import physical_object
import random
import string
class Space:
    """
    The physical space that objects reside in. Contains a list of all objects in its domain, the xyz coordinates of
    those objects and has x y z dimensions
    """

    def __init__(self,x,y,z):
        self._x_max = x
        self._x_min = -x
        self._y_max = y
        self._y_min = -y
        self._z_max = z
        self._z_min = -z
        self._objects = {}
        self._camera = None
        self.set_boundaries()

    def set_boundaries(self):
        # Get a vertex at each corner of space -> Change to a loop
        v1 = physical_object.Vertex(self._x_max,self._y_max,self._z_min)
        v2 = physical_object.Vertex(self._x_max,self._y_min,self._z_min)
        v3 = physical_object.Vertex(self._x_min,self._y_max,self._z_min)
        v4 = physical_object.Vertex(self._x_min,self._y_min,self._z_min)
        v5 = physical_object.Vertex(self._x_min,self._y_max,self._z_max)
        v6 = physical_object.Vertex(self._x_min,self._y_min,self._z_max)
        v7 = physical_object.Vertex(self._x_max,self._y_max,self._z_max)
        v8 = physical_object.Vertex(self._x_max,self._y_min,self._z_max)
        vertices = [v1,v2,v3,v4,v5,v6,v7,v8]
        # generate the polygons that make up the boundaries
        for p in range(8):
            q = p+1
            r = p+2
            if q>=8:
                q-=8
            if r>=8:
                r-=8
            new_surface = physical_object.Surface(vertices[p],vertices[q],vertices[r])
            new_surface.set_color('gray') # set the color to a greyish hue
            self.add_object(new_surface)

        # Now the 4 polygons that bound the top and bottom
        new_surface = physical_object.Surface(v1,v3,v5)
        new_surface.set_color('blue')
        self.add_object(new_surface)
        new_surface = physical_object.Surface(v7,v1,v5)
        new_surface.set_color('orange')
        self.add_object(new_surface)
        new_surface = physical_object.Surface(v2,v4,v6)
        new_surface.set_color('blue')
        self.add_object(new_surface)
        new_surface = physical_object.Surface(v2,v6,v8)
        new_surface.set_color('orange')
        self.add_object(new_surface)

    def add_object(self,object):
        id = generate_id()
        object.set_id(id)
        self._objects[object.id()]=object

    def add_viewpoint(self,camera):
        self._camera = camera

    def surfaces(self):
        return self._objects

    def surfaces_2(self):
        m = len(list(self._objects.keys()))
        colors = np.empty((m,3),dtype=np.uint8)
        vertices = np.empty((m,3))
        edge_one = np.empty((m,3))
        edge_two = np.empty((m,3))
        counter = 0
        for surface in list(self._objects.values()):
            colors[counter] = surface.color()
            vertices[counter] = surface._point_one
            edge_one[counter] = surface._side_one
            edge_two[counter] = surface._side_two
            counter += 1
        return vertices,edge_one,edge_two,colors

def generate_id(length=10):
    """
    Generate a 'unique' id for an object
    :param length: the length of the id
    :return: the id as a string
    """
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(characters, k=length))