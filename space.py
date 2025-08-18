# Creates a physical space that objects reside in.
import numpy as np

from physical_object import Vertex, Surface, Solid
import random
import string

from utilities import *

class Space:
    """
    The physical space that objects reside in. Contains a list of all objects in its domain, the xyz coordinates of
    those objects and has x y z dimensions
    """
    def __init__(self, x, y, z):
        self._bounds = np.array([x],[y],[z])
        self._objects = {}
        self._camera = None
        self._vertices = []
        self.set_boundaries

    def set_boundaries(self):
        # Get all 8 points in the corners of the space cube
        for x in (IDENTITY_3, INVERT_X):
            for y in (IDENTITY_3, INVERT_Y):
                for z in (IDENTITY_3, INVERT_Z):
                    point = np.dot(x, np.dot(y, np.dot(z, self._bounds))).flatten()
                    v = Vertex(point)
                    self._vertices.append(v)
        self.set_boundary_polygons()

    def set_boundary_polygons(self):
        """
        Create all boundary polygons that create the edge of space in the scene. All surfaces are made in winding order, normal should face origin.
        """
        # Positive X
        self.add_object(Surface(self._vertices[0], self._vertices[1], self.vertices[3],color=(128,128,128)))
        self.add_object(Surface(self._vertices[3], self._vertices[2], self.vertices[0],color=(128,128,128)))
        # Negative Z Boundary
        self.add_object(Surface(self._vertices[1], self._vertices[5], self.vertices[7],color=(128,128,128)))
        self.add_object(Surface(self._vertices[7], self._vertices[3], self.vertices[1],color=(128,128,128)))
        # Negative X Boundary
        self.add_object(Surface(self._vertices[5], self._vertices[4], self.vertices[6],color=(128,128,128)))
        self.add_object(Surface(self._vertices[6], self._vertices[7], self.vertices[5],color=(128,128,128)))
        # Positive Z Boundary
        self.add_object(Surface(self._vertices[4], self._vertices[0], self.vertices[2],color=(128,128,128)))
        self.add_object(Surface(self._vertices[2], self._vertices[6], self.vertices[4],color=(128,128,128)))
        # Positive Y Boundary
        self.add_object(Surface(self._vertices[5], self._vertices[1], self.vertices[0],color=(128,128,128)))
        self.add_object(Surface(self._vertices[0], self._vertices[4], self.vertices[5],color=(128,128,128)))
        # Negative Y Boundary
        self.add_object(Surface(self._vertices[6], self._vertices[2], self.vertices[3],color=(128,128,128)))
        self.add_object(Surface(self._vertices[3], self._vertices[7], self.vertices[6],color=(128,128,128)))
    
    def add_object(self,object):
        id = generate_id()
        object.set_id(id)
        self._objects[object.id()] = object

    def add_viewpoint(self,camera):
        self._camera = camera

    def object_list(self):
        return list(self._objects.keys())

    def object_list(self, id):
        return self._objects[id]
                
def generate_id(length=10):
    """
    Generate a 'unique' id for an object
    :param length: the length of the id
    :return: the id as a string
    """
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(characters, k=length))
