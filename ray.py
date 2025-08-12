import numpy as np

class Ray:

    def __init__(self,origin,direction):
        if not isinstance(origin, np.ndarray):
            origin = np.array(origin)
        if not isinstance(direction,np.ndarray):
            direction = np.array(direction)
        self._origin = origin
        self._direction = direction

    def direction(self):
        return self._direction

    def origin(self):
        return self._origin

    def get_point(self,t):
        #new_point = (self._direction[0]-self._origin[0],self._direction[1]-self._origin[1],self._direction[2]-self._origin[2])
        new_point = self._direction-self._origin
        h = []
        #new_point = (new_point[0]*t,new_point[1]*t,new_point[2]*t)
        new_point = new_point*t
        # I could be wrong on this, but I think this doesn't work. It only finds a point along the direction from origin?
        return new_point