import unittest

import numpy as np

from physical_object import *

class MyTestCase(unittest.TestCase):
    def test_something(self):
        v1 = Vertex(np.array([-1,0,1]))
        v2 = Vertex(np.array([0,1,1]))
        v3 = Vertex(np.array([1,0,1]))
        r1 = Ray(np.array([0,0,0]),np.array([0,.5, 1]))
        s1 = Surface(v1,v2,v3)
        print(s1.normal())
        t = s1.find_t(r1)
        r = (s1.get_intersection_point(r1,t))
        print(t)
        print(r)
        bc = s1.get_barycentric_coefficients(r)
        print(bc)
        self.assertTrue(s1.check_if_ray_intersects_surface(r1))

if __name__ == '__main__':
    unittest.main()
