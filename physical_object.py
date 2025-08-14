# Creates a class for a basic solid in space

import space
from ray import Ray
import numpy as np
from utilities import *

# Move to another file, constants
COLOR_MAP = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "gray": (128, 128, 128),
    "light_gray": (192, 192, 192),
    "dark_gray": (64, 64, 64),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "purple": (128, 0, 128),
    "brown": (165, 42, 42),
    "lime": (0, 255, 0),
    "teal": (0, 128, 128),
    "indigo": (75, 0, 130),
    "violet": (238, 130, 238)
}

class Vertex:
    """
    Represents a point in 3d space with color data for that vertex. Color data enables smooth shading
    """
    def __init__(self, point: np.ndarray, color=COLOR_MAP["black"]):
        """
        Create the vertex with coordinates of point, and vertex data of color
        :param point: an array of [x,y,z]
        :param color: the vertex color, (R, G, B)
        """
        self.set_coordinates(point)
        self.set_color(color)

    def get_vertex(self):
        return self._coordinates

    def get_coordinates(self):
        return self._coordinates
    #def get_world_coordinates(self,):
    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color

    def set_coordinates(self, point: np.ndarray):
        self._x_coordinate = point[0]
        self._y_coordinate = point[1]
        self._z_coordinate = point[2]
        self._coordinates = point
        
    def get_color_from_barycentric_value(self, u):
        """
        Returns the adjusted color from this vertex given the relative distance from this point on a plane (u, v, or w from barycentric equations)
        """
        return self._color * u

class Surface:
    """
    Represents the surface bounded by 3 vertices. A triangular polygon. Support for higher order polygons coming soon.
    """
    def __init__(self, vertex_0: np.ndarray, vertex_1: np.ndarray, vertex_2: np.ndarray, color=None):
        """
        Given 3 vertices, initialize the polygon. 
        :param vertex_0: an ndarray for the first vertex
        :param vertex_1: an ndarray for the second vertex
        :param vertex_2: an ndarray for the third vertex
        :param color: a tuple representing the color of the polygon. Overwrites the vertex data
        """
        self._vertices =np.array([vertex_0, vertex_1, vertex_2])
        self._v0 = vertex_0.get_coordinates()
        
        
        # Generate the edges of the polygon
        self._AB = self.make_line_segment(vertex_0, vertex_1)
        self._BC = self.make_line_segment(vertex_1, vertex_2)
        self._CA = self.make_line_segment(vertex_2, vertex_0)

        # Center, normal, and constant can change on rotation and translation
        self._center = self.get_center()
        self._normal = self.calc_normal()
        self._area = np.linalg.norm(self._normal) / 2 # Unless deformation or vertex manipulation is added, this should be constant
        self._solid = None
        
        # If a color was passed then override the color data of the vertices
        if color is not None:
            self.set_color(color)
        else:
            self._color = None

        # make an ID
        # Assign to a solid?
    
    def make_line_segment(start_vertex, end_vertex):
        return start_vertex.get_vertex() - end_vertex.get_vertex()

    def get_center(self):
        coordinate_sum = np.array([0,0,0])
        for vertex in self._vertices:
            coordinate_sum += vertex.get_coordinates()
        center = np.divide(coordinate_sum, len(self._vertices))
        return center

    def set_vertices_color(self, color):
        for vertex in self._vertices:
            vertex.set_color(color)
    
    def set_color(self, color):
        self._color = color
        self.set_vertices_color(color)
        
    def color(self):
        return self._color

    def set_id(self,id):
        self._id = id

    def id(self):
        return self._id

    def calc_normal(self):
        normal_vector = np.cross(self._CA, self._BC)
        self._normal = normal_vector

    def get_normal(self):
        return self._normal

    def get_new_normal(self):
        self.calc_normal
        return self.get_normal()

    def normal(self):
        """
        Alias for get_normal
        """
        return self.get_normal()

    def get_equation(self):
        self._equation = f"{self._normal[0]}X + {self._normal[1]}Y + {self._normal[2]}Z = {self._d}"

    def get_plane_constant(self):
        """
        Get the plane constant for the plane equation. Also referred to as d or D in the literature.
        """
        constant = np.dot(self._normal, self._v0)
        self._plane_constant = constant
        self._d = constant

    def backface_check(self, ray: Ray):
        """
        Determine if the surface is pointing the right direction to be seen. Not yet implemented. Perhaps have a toggle for each surface as to whether or not it can be seen from both sides?
        """
        if np.dot(ray.direction(), self._normal) < 0:
            return True
        return False
        
    def find_t(self, ray: Ray):
        """
        Get the distance along a ray to the intersection of the plane
        """
        # Check for orthogonal normal and direction, as the ray will not intersect
        if -.2 < np.dot(ray.direction(), self._normal) < .2:
            return -1
        t = (self._d - np.dot(self._normal, ray.origin())) / np.dot(self._normal, ray.direction())
        return t

    def get_intersection_point(self, ray: Ray):
        """
        Gets the point of intersection between a plane and a ray
        """
        t = self.find_t(ray)
        intersection = ray.get_point(t)
        return intersection
    
    def check_point_in_surface(self, u, v, w):
        if .99 < u + v + w < 1.01 and (0,0,0) <= (u, v, w) <= (1, 1, 1):
            return True
        return False
        
    def get_barycentric_coefficients(self, point):
        u = self.get_u(point)
        v = self.get_v(point)
        w = self.get_w(point)
        return u, v, w

    def check_if_ray_intersects_surface(self, ray: Ray):
        plane_intercept = self.get_intersection_point(ray)
        u, v, w = self.get_barycentric_coefficients(plane_intercept)
        if self.check_point_in_surface(u, v, w):
            return self.get_color_at_point(u, v, w)
        else:
            return False

    def get_color_at_point(self, u, v, w):
        c1 = np.array(self._vertices[0].get_color_from_barycentric_value(u))
        c2 = np.array(self._vertices[0].get_color_from_barycentric_value(v))
        c3 = np.array(self._vertices[0].get_color_from_barycentric_value(w))
        color = c1 + c2 + c3
        return tuple(color)
        
    def get_u(self, point: np.ndarray):
        # The sign of the cross product shouldn't matter, since we wind in the same order as the normal
        radial = self._vertices[0].get_coordinates() - point
        normal = np.dot(radial, self._AB)
        return normal / (2 * self._area)

    def get_v(self, point):
        radial = self._vertices[1].get_coordinates() - point
        normal = np.dot(radial, self._BC)
        return normal / (2 * self._area)

    def get_u(self, point):
        radial = self._vertices[2].get_coordinates() - point
        normal = np.dot(radial, self._CA)
        return normal / (2 * self._area)

    def assign_solid(self, id):
        self._solid = id
        
class Solid:
    """
    Holds a set of surfaces that make up a rigid body. Allows translation and rotation of all vertices and surfaces uniformly about a point
    """
    def __init__(self,id,*args):
        """
        Instantiate a solid with a set id and a number of surfaces.
        :param id: The unique id of the solid
        :param args: All of the surfaces to initially assign to the solid
        """
        self.set_id(id)
        self._origin = np.array([0,0,0])

        # Set the translation and rotation transforms
        self._translation = np.array([0, 0, 0])
        self._rotation = IDENTITY

        # Assign all of the passed surfaces and get the center of mass        
        self._surfaces = np.array([])
        for arg in args:
            self.add_surface(arg)
        
    def add_surface(self,surface):
        """
        Adds a new surface to the solid and recalculates the center of mass.
        """
        np.append(self._surfaces, surface)
        surface.assign_solid(self._id)
        self.get_center_of_mass()
    
    def get_center_of_mass(self):
        """
        Calculates the center of mass of the solid. This point is the default axis of rotation.
        """
        #center = np.array([0, 0, 0])
        #np.sum(self._surfaces, axis=0) # I believe this will add the vectors appropriately
        #for surface in self._surfaces:
        #    center= np.add(center, surface.get_center())
        #center /= len(self._surfaces)
        center = np.mean(self._surfaces, axis=0) # should find the average point in the solid
        self._center = center
        print(f"This is my center {center}")

    def center_of_mass(self):
        return self._center
        
    def get_surfaces(self):
        return self._surfaces

    def set_id(self,id):
        self._id = id

    def id(self):
        return self._id

    def translate(self, x, y, z):
        movement = np.array([x, y, z])
        
    def translate_vector(self, movement: np.ndarray):
        np.add(self._translation, movement)
        
    def rotate(self, yaw, pitch, roll):
        pass

    def __getattr__(self, name):
        """
        Alias get methods as attributes of the object. Prevent reassignment of private attributes.
        """
        if name == "COM":
            return self.center_of_mass()
        if name == "com":
            return self.center_of_mass()
        if name == "surfaces":
            return self.get_surfaces()
        if name == "id":
            return self.id()
        if name == 'rotation':
            return self.get_rotation_matrix()
        if name == "translation":
            return self.get_translation_vector()
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

def cross_product(v1,v2):
    cp =            (v1[1] * v2[2] - v1[2] * v2[1],
                     v1[2] * v2[0] - v1[0] * v2[2],
                     v1[0] * v2[1] - v1[1] * v2[0])
    return cp

