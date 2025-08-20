# Creates a class for a basic solid in space


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
        """
        Returns the local coordinates of the vertex. Aliases get_coordinates
        """
        return self._coordinates

    def get_coordinates(self):
        """
        Returns the local coordinates of the vertex.
        """
        return self._coordinates

    def get_color(self):
        """
        Returns the RGB value of the vertex
        """
        return self._color

    def set_color(self, color):
        """
        Sets the color of the vertex.
        """
        # If a named color was passed, get the tuple associated with that name
        if isinstance(color, str):
            try:
                self._color = COLOR_MAP[color]
            except KeyError:
                # If the color wasn't found, assign pink to the vertex
                self._color = COLOR_MAP["pink"]

        # Otherwise set the passed tuple as the color
        else:
            self._color = color

    def set_coordinates(self, point: np.ndarray):
        """
        Updates the local coordinates for the vertex
        """
        self._x_coordinate = point[0]
        self._y_coordinate = point[1]
        self._z_coordinate = point[2]
        self._coordinates = point
        
    def get_color_from_barycentric_value(self, u):
        """
        Returns the adjusted color from this vertex given the relative distance from this point on a plane (u, v, or w from barycentric equations). Converts each value to int
        """
        return tuple(map(lambda x: int(x*u), self._color))

class Surface:
    """
    Represents the surface bounded by 3 vertices. A triangular polygon. Support for higher order polygons coming soon.
    """
    def __init__(self, vertex_0: Vertex, vertex_1: Vertex, vertex_2: Vertex, color=None):
        """
        Given 3 vertices, initialize the polygon. Winding order is clockwise to produce a normal facing the origin.
        The coordinates are local with respect to the origin. Must be translated to global coordinates when rendering
        :param vertex_0: the first vertex object
        :param vertex_1: the second vertex object
        :param vertex_2: the third vertex object
        :param color: a tuple representing the color of the polygon. Setting this will override getting vertex colors
        """
        
        self._vertices = np.array([vertex_0, vertex_1, vertex_2])
        self._v0 = vertex_0.get_coordinates()
        self._v1 = vertex_1.get_coordinates()
        self._v2 = vertex_2.get_coordinates()
        
        
        # Generate the edges of the polygon
        self._AB = self.make_line_segment(vertex_0, vertex_1)
        self._BC = self.make_line_segment(vertex_1, vertex_2)
        self._CA = self.make_line_segment(vertex_2, vertex_0)

        # Center, normal, and constant can change on rotation and translation
        self._center = self.get_center()
        self._solid = None
        self.calc_normal()
        self._local_normal = self._normal.flatten()    # Stores the normal vector when the surface is not rotated or translated
        self._area = np.linalg.norm(self._normal) / 2 # Unless deformation or vertex manipulation is added, this should be constant
        self.set_color(color)
    
    def make_line_segment(self, start_vertex, end_vertex):
        """
        Returns an ndarray representing the line segment from start_vertex to end_vertex
        :return: An ndarray of [x, y, z].
        """
        return start_vertex.get_vertex() - end_vertex.get_vertex()

    def get_center(self):
        """
        Calculates the local center of the surface with respect to its vertices.
        """
        coordinate_sum = np.array([0,0,0],dtype='float64')
        for vertex in self._vertices:
            coordinate_sum += vertex.get_coordinates()
        center = np.divide(coordinate_sum, len(self._vertices))
        return center

    def center(self):
        """
        Return the center of the surface
        """
        return self._center

    def set_vertices_color(self, color):
        """
        Sets all the vertices of this surface to a passed color. Deprecated.
        """
        for vertex in self._vertices:
            vertex.set_color(color)
    
    def set_color(self, color):
        """
        Sets the color of the solid. If a string is passed, it's mapped to its respective named color.
        """
        # If a named color was passed, get the tuple associated with that name
        if isinstance(color, str):
            try:
                self._color = COLOR_MAP[color]
            except KeyError:
                # If the color wasn't found, assign pink to the vertex
                self._color = COLOR_MAP["pink"]

        # Otherwise set the passed tuple as the color
        else:
            self._color = color
            
    def color(self):
        """
        Return the surfaces color
        """
        return self._color

    def set_id(self, id):
        """
        Set the id of the surface
        """
        self._id = id
    
    def id(self):
        """
        Get the id of the surface
        """
        return self._id

    def calc_normal(self):
        """
        Calculates the normal of the surface. Transforms it into world coordinates.
        """
        # I'm thinking that the normal doesn't need to be recalced, since it's based on local coordinates. Instead, Transform it
        normal_vector = np.cross(self._BC, self._CA)
        if self._solid is not None:
            # Find a better way to do this. Passing the entire object as an attribute seems like a poor use of memory
            normal_vector = self._solid.transform_vertex(self.get_normal())
        self._normal = normal_vector.T

    def get_normal(self):
        """
        Returns the current world normal as a 1x3 array
        """
        return self._normal.flatten()

    def get_transformed_normal(self):
        """
        Transforms the local normal by the solids transformation matrix
        """
        return self._solid.transform_vertex(self._local_normal)
        
    def get_new_normal(self):
        """
        Recalculate the world coordinates normal
        """
        self.calc_normal()
        return self.get_normal()

    def normal(self):
        """
        Alias for get_normal
        """
        return self.get_normal()

    def get_equation(self):
        """
        Gets the plane equation that the polygon resides on
        """
        self._equation = f"{self._normal[0]}X + {self._normal[1]}Y + {self._normal[2]}Z = {self._d}"

    def get_plane_constant(self):
        """
        Get the plane constant for the plane equation. Also referred to as d or D in the literature.
        """
        v = self._v0
        # Transform the source vertex to get its world position
        if self._solid is not None:
            v = self._solid.transform_vertex(v)
        constant = np.dot(v, self._normal)
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
        # recalculate the plane constant and normal to reflect current transformations
        self.calc_normal()
        self.get_plane_constant()
        
        # Check for orthogonal normal and direction, as the ray will not intersect
        if -.2 < np.dot(ray.direction(), self._normal) < .2:
            return -1
            
        t = (self._d - np.dot(ray.origin().flatten(), self._normal.flatten())) / np.dot(ray.direction().flatten(),self._normal.flatten())

        # For batch processing, t seems to be returns as a nested array of the form [[t]]. Individual calculations fetch it as a scalar. Investigation required
        if isinstance(t, float):
            return t
        return t[0][0]
        

    def get_intersection_point(self, ray: Ray, t = None):
        """
        Gets the point of intersection between a plane and a ray
        """
        if t is None:
            t = self.find_t(ray)
        if t<0:
            return False
        intersection = ray.get_point(t)
        return intersection
    
    def check_point_in_surface(self, u, v, w):
        """
        Checks that the barycentric coefficients add up to 1 and are each bounded by [0,1]
        """
        if .99 < u + v + w < 1.01 and (0,0,0) <= (u, v, w) <= (1, 1, 1):
            return True
        return False
        
    def get_barycentric_coefficients(self, point):
        """
        Returns the 3 barycentric coordinates associated with a given point on the surfaces plane.
        """
        u = self.get_u(point)
        v = self.get_v(point)
        w = self.get_w(point)
        return u, v, w

    def check_if_ray_intersects_surface(self, ray: Ray, t = None):
        """
        Check if a ray intersects with the surface. Returns the color of that intersection point or False if it doesn't
        :param ray: The Ray object to be checked
        :param t: The t value (length) to the surface. If not passed, it will be calculated
        """
        # Get whether the ray intercepts the plane of the surface
        plane_intercept = self.get_intersection_point(ray, t)
        if plane_intercept is False:
            return False

        # Find the barycentric coefficients and determine if the intercept is inside the surface
        u, v, w = self.get_barycentric_coefficients(plane_intercept)
        if self.check_point_in_surface(u, v, w):
            if self._color is not None:
                color = self._color
            else:
                color = self.get_color_at_point(u, v, w)
            return color
        else:
            return False

    def get_color_at_point(self, u, v, w):
        """
        Given the 3 barycentric coefficients, determine the average color of the intersection (based on vertex color data)
        """
        c1 = np.array(self._vertices[0].get_color_from_barycentric_value(u))
        c2 = np.array(self._vertices[0].get_color_from_barycentric_value(v))
        c3 = np.array(self._vertices[0].get_color_from_barycentric_value(w))
        color = c1 + c2 + c3
        return tuple(color)
        
    def get_u(self, point: np.ndarray):
        """
        Gets the first Barycentric coordinate.
        """
        # Use the cross product to find the area of Triangle PA, AB, BP and return that as a ratio of the triangles area
        radial = self._vertices[0].get_coordinates() - point
        normal = np.linalg.norm(np.cross(radial, self._AB))
        return normal / (2 * self._area)

    def get_v(self, point):
        """
        Gets the second Barycentric coordinate.
        """
        # Use the cross product to find the area of Triangle PB, BC, CP and return that as a ratio of the triangles area
        radial = self._vertices[1].get_coordinates() - point
        normal = np.linalg.norm(np.cross(radial, self._BC))
        return normal / (2 * self._area)

    def get_w(self, point):
        """
        Gets the third Barycentric coordinate.
        """
        # Use the cross product to find the area of Triangle PC, CA, AP and return that as a ratio of the triangles area
        radial = self._vertices[2].get_coordinates() - point
        normal = np.linalg.norm(np.cross(radial, self._CA))
        return normal / (2 * self._area)

    def assign_solid(self, id):
        self._solid = id
        
class Solid:
    """
    Holds a set of surfaces that make up a rigid body. Allows translation and rotation of all vertices and surfaces uniformly about a point
    """
    def __init__(self, *args):
        """
        Instantiate a solid with a set id and a number of surfaces.
        :param id: The unique id of the solid
        :param args: All of the surfaces to initially assign to the solid
        """
        self.set_id(id)
        self._origin = np.array([0,0,0])
        self._transform = IDENTITY
        self.reset_movement()
        
        # Assign all of the passed surfaces and get the center of mass        
        self._surfaces = []
        for arg in args:
            self.add_surface(arg)

    def add_surface(self,surface):
        """
        Adds a new surface to the solid and recalculates the center of mass.
        """
        self._surfaces.append(surface)
        surface.assign_solid(self)
        self.get_center_of_mass()
    
    def get_center_of_mass(self):
        """
        Calculates the center of mass of the solid. This point is the default axis of rotation.
        """
        center = np.mean(self.get_surface_coords(), axis=0) # should find the average point in the solid
        self._center = center
        print(f"This is my center {center}")

    def center_of_mass(self):
        """
        Returns the local center coordinate for the object
        """
        return self._center
        
    def get_surfaces(self):
        """
        Return all surfaces contained in the object
        """
        return np.array(self._surfaces)

    def get_surface_coords(self):
        """
        Return all of the coordinates of the centers for the surfaces in the object
        """
        return np.array([s.center() for s in self._surfaces])

    def set_id(self,id):
        """
        Sets the unique ID of the solid
        """
        self._id = id

    def id(self):
        """
        Returns the unique ID of the solid
        """
        return self._id

    def get_transform(self):
        """
        Returns the 4x4 transformation matrix of the object
        """
        return self._transform

    def reset_movement(self):
        """
        Resets accumulated movement and rotation back to 0. Called after every new transform is used. Can track movement between frames
        """
        self._x = 0
        self._y = 0
        self._z = 0
        self._yaw = 0
        self._pitch = 0
        self._roll = 0
        
    def add_movement(self, x=0, y=0, z=0):
        """
        Adds an accumulation of movement along the 3 axes
        """
        self._x += x
        self._y += y
        self._z += z

    def add_rotation(self, yaw=0, pitch=0, roll=0):
        """
        Adds an accumulation of rotation about the 3 axes
        """
        self._yaw += yaw
        self._pitch += pitch
        self._roll += roll
    
    def translate(self, x=0, y=0, z=0):
        """
        Returns the accumulated movement as a 1x3 array
        """
        return np.array([x, y, z])

    def rotate(self, yaw=0, pitch=0, z=0):
        """
        Returns the accumulated rotation as a 1x3 array
        """
        return np.array([x, y, z])
        
    def new_transform(self):
        """
        Gets a new transformation matrix based on movement since last render. Resets accumulated sub frame movement to 0
        """
        t = self.translate(self._x, self._y, self._z)
        r = self.rotate(self._yaw, self._pitch, self._roll)
        self.update_transform(t, r, self._center) # I believe that the axis is appropriate here, doesn't need to be converted to world coordinates
        self.reset_movement()
        
    def update_transform(self, translate: np.ndarray, yaw_pitch_roll: np.ndarray, axis=None):
        """
        Performs transformation on the existing matrix and overwrites it.
        """
        self._transform = apply_transform(translate, axis, yaw_pitch_roll, self._transform)

    def transform_vertex(self, vertex_coords: np.ndarray):
        """
        Transforms a vertexes coordinates by the transformation matrix, gives the true position of the vertex in space.
        :param vertex_coords: a 1x3 vector containing the xyz of a vertex.
        :return: a 1x3 array containing the true xyz of a vertex.
        """
        return world_coordinates(vertex_coords, self._transform)

    def get_world_coords(self):
        """
        Gets the world coordinates of the center of mass.
        """
        return self.transform_vertex(self._center)
        
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
        if name == 'transform':
            return self.get_transform()
        if name == "xyz":
            return self.get_translation_vector()
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

def cross_product(v1,v2):
    cp =            (v1[1] * v2[2] - v1[2] * v2[1],
                     v1[2] * v2[0] - v1[0] * v2[2],
                     v1[0] * v2[1] - v1[1] * v2[0])
    return cp

