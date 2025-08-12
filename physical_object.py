# Creates a class for a basic solid in space

import space
from ray import Ray
import numpy as np

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
    def __init__(self, point: np.ndarray, color=COLOR_MAP["black"]: tuple):
        """
        Create the vertex with coordinates of point, and vertex data of color
        :param point: an array of [x,y,z]
        :param color: the vertex color, (R, G, B)
        """
        self._x_coordinate = point[0]
        self._y_coordinate = point[1]
        self._z_coordinate = point[2]
        self._coordinates = point
        self._color = color

    def get_vertex(self):
        return self._coordinates

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color

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

        # Generate the edges of the polygon
        self._AB = self.make_line_segment(vertex_0, vertex_1)
        self._BC = self.make_line_segment(vertex_1, vertex_2)
        self._CA = self.make_line_segment(vertex_2, vertex_0)
        
        self._normal = self.calc_normal()

        # If a color was passed then override the color data of the vertices
        if color is not None:
            for vertex in self._vertices:
                vertex.set_color(color)


    def make_line_segment(start_vertex, end_vertex):
        return start_vertex.get_vertex() - end_vertex.get_vertex()

    def get_center(self):
        xyz_total=self._vertices[0].get_vertex()+self._vertices[1].get_vertex()+self._vertices[2].get_vertex()
        xyz_total = np.divide(xyz_total,3)
        return xyz_total

    def set_color(self,color):
        if COLOR_MAP[color]:
            color = np.array(COLOR_MAP[color],dtype=np.uint8)
        self._color=color

    def color(self):
        return self._color

    def set_id(self,id):
        self._id = id

    def id(self):
        return self._id

    def calc_normal(self):
        normal_vector = np.cross(self._CA, self._BC)
        return normal_vector

    def check_intersection(self,ray):
        #h = self.calc_h(ray)
        h = np.cross(ray.direction(), self._side_two)
        #a = self._side_one[0]*h[0]+self._side_one[1]*h[1]+self._side_one[2]*h[2]  # The determinant
        a = np.dot(self._side_one,h)
        if a == 0:
            return False
        o = ray.origin()
        vertex_0 = self._vertices[0].get_vertex()
        #s = (o[0]-vertex_0[0],o[1]-vertex_0[1],o[2]-vertex_0[2])
        s = o-vertex_0
        d = ray.direction()
        cp = np.cross(s, self._side_one)
        #u = self.calc_u(h,a,s)
        u = np.dot(s,h)/a
        if u > 1 or u < 0:
            return False
        #v = self.calc_v(d,a,s)
        v = np.dot(d,cp)/a
        if v > 1 or v < 0 or u+v > 1:
            return False
        #t = self.calc_t(a,s)
        t = np.dot(self._side_two, cp) / a
        point = ray.get_point(t)
        return t,point

    def calc_h(self,ray):
        """
        Gives the cross product of the direction and the second edge of the vertex
        :param ray:
        :return:
        """
        direction = ray.direction()
        #h = cross_product(direction,self._side_two)
        return np.cross(direction,self._side_two)

    def calc_u(self,h,a,s):
        """
        Calculates the U value for an intersection. must be between 0 and 1 inclusive, to intersect
        :param ray:
        :return:
        """
        #u = (s[0]*h[0]+s[1]*h[1]+s[2]*h[2])/a
        u = np.dot(s,h)/a
        return u

    def calc_v(self,d,a,s):
        """
        Calculates the v value for an intersection must be between 0 and 1, and u+v must be 0-1
        :param ray:
        :return:
        """
        #cp = cross_product(s,self._side_one)
        cp = np.cross(s,self._side_one)
        #v = (d[0]*cp[0]+d[1]*cp[1]+d[2]*cp[2])/a
        v = np.dot(d,cp)/a
        return v

    def calc_t(self,a,s):
        """
        Calculates t which is how far along the ray the object is.
        :param ray:
        :return:
        """
        #cp = cross_product(s,self._side_one)
        cp = np.cross(s,self._side_one)
        d = self._side_two
        #t = (d[0]*cp[0]+d[1]*cp[1]+d[2]*cp[2])/a
        t = np.dot(d,cp)/a
        return t

    def check_parallel(self,vector):
        #dot_product = self._normal[0]*vector[0] + self._normal[1]*vector[1] + self._normal[2]*vector[2]
        #if dot_product == 0:
        dot = np.dot(self._normal,vector)
        if -.1<dot and dot<.1:
            return True
        return False


class Solid:
    # represents a set of surfaces that make up an object
    def __init__(self,id,*args):
        self.set_id(id)
        self._origin = np.array([0,0,0])
        self._surfaces = []
        for arg in args:
            self.add_surface(arg)
        self.center_of_mass()

    def add_surface(self,surface):
        self._surfaces.append(surface)
        surface.assign_solid(self._id)

    def center_of_mass(self):
        center = self._origin
        for surface in self._surfaces:
            center= np.add(center,surface.get_center())
        center /= len(self._surfaces)
        self._origin = center
        print(f"This is my center {center}")

    def get_surfaces(self):
        return self._surfaces

    def set_id(self,id):
        self._id = id

    def id(self):
        return self._id

    def translate(self,x,y,z):
        move = np.array([x,y,z])
        self._origin += move

    def rotate(self,yaw,pitch,roll):
        pass

def cross_product(v1,v2):
    cp =            (v1[1] * v2[2] - v1[2] * v2[1],
                     v1[2] * v2[0] - v1[0] * v2[2],
                     v1[0] * v2[1] - v1[1] * v2[0])
    return cp

