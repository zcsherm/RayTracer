import numpy as np

class Ray:

    def __init__(self, origin: np.ndarray,direction: np.ndarray):
        """
        Create a new ray starting from an origin and traveling in a direction
        :origin: an numpy array of <x,y,z> representing the rays source
        :direction: a numpy array representing the direction the ray is travelling (not another point along the ray)
        """
        self._origin = origin
        self._direction = direction
        #self._equation = "<Ox, Oy, Oz> + t<Dx, Dy, Dz>" # Unsure which of these looks better when printed
        self._equation = f"{origin} + t{direction}"
        
    def direction(self):
        return self._direction

    def origin(self):
        return self._origin

    def get_point(self,t):
        """
        Returns a point that is t distance along the ray
        :param t: The length to travel along direction from the origin
        """
        new_point = self._origin + t * self._direction
        return new_point
