
import numpy as np
from ray import Ray
from physical_object import *
from renderer import *
import timeit
from utilities import *

VECTOR = np.array([[.3],[.22],[.262]])

class Camera:

    def __init__(self):
        """
        Setup the cameras 4 borders, the origin, and transformation matrix
        """
        self._origin = np.array([0,0,0])
        self.set_viewport_borders()
        self._transform = IDENTITY
        self.reset_movement()

    def set_viewport_borders(self):
        """
        Generate the 4 boundary vectors of the frustum. Change them into xyz coords
        """
        self._d1 = VECTOR.flatten()
        self._d2 = np.dot(INVERT_Y, VECTOR).flatten()
        self._d3 = np.dot(INVERT_X, self._d2).flatten()
        self._d4 = np.dot(INVERT_X, VECTOR).flatten()
        
    def update_transform(self, translate: np.ndarray, yaw_pitch_roll: np.ndarray):
        """
        Given a a translation and rotation, find the new compound transformation matrix.
        :param translate: The amount the object has moved/translated
        :param yaw_pitch_roll: the amount the object has rotated about its axes
        """
        self._transform = apply_transform(translate, self._origin, yaw_pitch_roll, self._transform)

    def get_translate_viewport(self, x=0, y=0, z=0):
        """
        Changes individual position changes into a 1x3 array
        """
        return np.array([x, y, z])

    def get_rotations(self, yaw=0, pitch=0, roll=0):
        """
        Changes individual rotations into a 1x3 array
        """
        return np.array([yaw, pitch, roll])

    def new_transform(self):
        """
        Updates the current transformation matrix and resets accumulated translations and rotations. Call this before rendering.
        """
        t = self.get_translate_viewport(self._x, self._y, self._z)
        r = self.get_rotations(self._yaw, self._pitch, self._roll)
        self.update_transform(t, r)
        self.reset_movement()

    def get_transform(self):
        """
        Get the transformation matrix
        """
        return self._transform

    def transform_point(self, point: np.ndarray):
        """
        Changes a point or vector from local coordinates into its true xyz coordinate.
        """
        return world_coordinates(point, self._transform)
        
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
        self._x += x
        self._y += y
        self._z += z

    def add_rotation(self, yaw=0, pitch=0, roll=0):
        self._yaw += np.radians(yaw)
        self._pitch += np.radians(pitch)
        self._roll += np.radians(roll)
        
    def update_viewport(self):
        self.new_transform()
        # Maybe get the true vector positions

    def print_data(self):
        print(self._pitch,self._roll,self._yaw)
        print(self._d1,self._d2,self._d3,self._d4)

    def generate_rays(self,width,height):
        """
        Generate a ray for every pixel of the screen and return a list containing all rays. All rays generated will get that pixel location as their direction, and origin is the cameras origin
        :param width: The width of the screen in pixels
        :param height: The height of the screen in pixels
        :return: an hxw matrix containing each ray passing through that pixel
        """
        v1 = self._d1
        v2 = self._d2
        v3 = self._d3
        v4 = self._d4
        
        # Each point on the screen is a linear combination of the top and side edges. We will treat the bottom left as the origin
        top_line = np.subtract(v1 - v4)
        side_line = np.subtract(v4 - v3)
        rays = np.empty((width,height),dtype=object)

        # Generate a ray sequential from the bottom left to the top right
        for x in range(width):
            # Get the coefficient for our X basis axis
            step_x = x / width
            change_x = step_x * top_line
            for y in range(height):
                # Get the coefficient for our Y basis
                step_y = y/height
                change_y = step_y * side_line
                total_change = np.add(change_y, change_x)

                # the final position is the x and y change added to the origin
                ray_direction = np.add(v3, total_change)

                # Get the world coordinates for the ray, as they are currently in local coordinates to the viewport.
                ray_direction = self.transform_point(ray_direction)
                origin = self.transform_point(self._origin)
                new_ray = Ray(origin, ray_direction)
                rays[x][y] =new_ray
                
        return rays

