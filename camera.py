
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import ray
from physical_object import *
from renderer import *
import timeit
#VECTOR = [0.720,0.643,0.262]       # Old pov, way to big
VECTOR = [.3,.22,.262]
class Camera:

    def __init__(self):
        self._origin = np.array([0,0,0],dtype=np.float64)
        self._heading = np.array([0,0,1])
        self._d1 = np.array([VECTOR[0],VECTOR[1],VECTOR[2]])
        self._d2 = np.array([VECTOR[0],-VECTOR[1],VECTOR[2]])
        self._d3 = np.array([-VECTOR[0],-VECTOR[1],VECTOR[2]])
        self._d4 = np.array([-VECTOR[0],VECTOR[1],VECTOR[2]])
        self._pitch = 0 # along x axis, like looking up.
        self._yaw = 0 # along y axis, like turning head
        self._roll = 0 #along the z axis, uncommon


    def change_angle(self,pitch=0,yaw=0,roll=0):
        # Update the angling of the guy, roll values over
        self._pitch += pitch
        self._yaw += yaw
        self._roll += roll
        if self._pitch >=360:
            self._pitch -= 360
        if self._pitch < 0:
            self._pitch+=360
        if self._yaw >=360:
            self._yaw -= 360
        if self._yaw < 0:
            self._yaw+=360
        if self._roll >=360:
            self._roll -= 360
        if self._roll < 0:
            self._roll+=360
        self.update_viewport(pitch,yaw,roll)

    def move_origin(self,x=0,y=0,z=0):
        self._origin += np.array([x,y,z])
        # Need to call updating the screen, but calling the  viewport will cause unreliable behavior
        #self.update_viewport(self._pitch,self._yaw,self._roll)

    def update_viewport(self,pitch,yaw,roll):
        yaw = np.radians(yaw)
        pitch = np.radians(pitch)
        roll = np.radians(roll)
        # update angling
        # Rotation matrix for yaw (about y-axis)
        R_yaw = np.array([
            [np.cos(yaw), 0, np.sin(yaw)],
            [0, 1, 0],
            [-np.sin(yaw), 0, np.cos(yaw)]
        ])

        # Rotation matrix for pitch (about x-axis)
        R_pitch = np.array([
            [1, 0, 0],
            [0, np.cos(pitch), -np.sin(pitch)],
            [0, np.sin(pitch), np.cos(pitch)]
        ])

        # Rotation matrix for roll (about z-axis)
        R_roll = np.array([
            [np.cos(roll), -np.sin(roll), 0],
            [np.sin(roll), np.cos(roll), 0],
            [0, 0, 1]
        ])
        # generate the rotation matrix
        R = np.dot(R_yaw,np.dot(R_pitch,R_roll))
        #apply it to each boundary of our viewport
        v1 = self._d1
        v2 = self._d2
        v3 = self._d3
        v4 = self._d4
        h = self._heading
        v1 = np.dot(R,v1)
        v1 /= np.linalg.norm(v1)
        v2 = np.dot(R,v2)
        v2 /= np.linalg.norm(v2)
        v3 = np.dot(R,v3)
        v3 /= np.linalg.norm(v3)
        v4 = np.dot(R,v4)
        v4 /= np.linalg.norm(v4)
        h = np.dot(R,h)
        h /= np.linalg.norm(h)
        self._d1 = v1
        self._d2 = v2
        self._d3 = v3
        self._d4 = v4
        self._heading = h

    def print_data(self):
        print(self._pitch,self._roll,self._yaw)
        print(self._d1,self._d2,self._d3,self._d4)

    def get_heading(self):
        return self._heading

    def generate_rays(self,width,height):
        """
        Generate a ray for every pixel of the screen and return a list containing all rays.
        :param width:
        :param height:
        :return:
        """
        v1 = self._d1
        v2 = self._d2
        v3 = self._d3
        v4 = self._d4
        # We use the concept that everypoint on the view plane is a linear combination of the top line and side line
        # of the viewport. so each point is going to be the top left point - 1/width*top line - 1/height*side line
        top_line = v4 - v1
        side_line = v4-v3
     #   rays = np.empty((height,width),dtype=object)
        rays = np.empty((width,height),dtype=object)
        for x in range(width):
            alpha = x/width
            tmp = v4 - alpha*top_line
            for y in range(height):
                beta = y/height
                coef_1 = (1-beta)
                coef_2 = (1-alpha)
                d = coef_1*(coef_2*v4+alpha*v1)+beta*(coef_2*v3+alpha*v2) # old method using some weird math

                d = tmp - beta *side_line   #this gives similar results.
                new_direction = [d[0], d[1], d[2]]
                #new_direction = [self._d4[0]+step_x*x,self._d2[1]+step_y*y,self._d3[2]+step_z*y]
                new_ray = ray.Ray(self._origin,new_direction)
                #rays.append(new_ray.get_point(1))
                #rays.append(new_ray)
#                rays[y][x]=new_ray
                rays[x][y] =new_ray
        return rays

    def generate_rays_vectorized(self,width,height):
        v1 = self._d1
        v2 = self._d2
        v3 = self._d3
        v4 = self._d4
        # We use the concept that everypoint on the view plane is a linear combination of the top line and side line
        # of the viewport. so each point is going to be the top left point - 1/width*top line - 1/height*side line
        top_line = v4 - v1
        side_line = v4 - v3
        rays = np.empty((height*width,3))
        origins = np.empty((height*width,3))
        for x in range(width):
            alpha = x / width
            tmp = v4 - alpha * top_line
            for y in range(height):
                beta = y / height
                coef_1 = (1 - beta)
                coef_2 = (1 - alpha)
                #d = coef_1 * (coef_2 * v4 + alpha * v1) + beta * (
                #            coef_2 * v3 + alpha * v2)  # old method using some weird math

                d = tmp - beta * side_line  # this gives similar results.
                new_direction = [d[0], d[1], d[2]]
                # new_direction = [self._d4[0]+step_x*x,self._d2[1]+step_y*y,self._d3[2]+step_z*y]
                #new_ray = ray.Ray(self._origin, new_direction)
                # rays.append(new_ray.get_point(1))
                # rays.append(new_ray)
                index = height*x+y
                rays[index] = d
                origins[index] = self._origin
        return rays,origins

    def generate_rays_test(self,width,height):
        """
        Generate a ray for every pixel in widthxheight and determin if it intersects a ploygon
        :param width:
        :param height:
        :return:
        """
        step_x = (self._d1[0]-self._d4[0])/width
        step_y = (self._d1[1]-self._d2[1])/height
        step_z = (self._d1[2]-self._d3[2])/width      # Not sure if this will accurately make a ray
        rays = []
        v1 = Vertex(-1, 0, 3)
        v2 = Vertex(0, 1.72, 3)
        v3 = Vertex(1, 0, 3)
        s1 = Surface(v1, v2, v3)
        for x in range(width):
            for y in range(height):
                new_direction = [self._d4[0]+step_x*x,self._d2[1]+step_y*y,self._d3[2]+step_z*y]
                new_ray = ray.Ray(self._origin,new_direction)
                if not s1.check_intersection(new_ray):
                    rays.append(new_ray.get_point(1))
        return rays


def plot_3d_points(points):
    """
    Plots a set of 3D points.

    :param points: List or array of (x, y, z) coordinates.
    """
    points = np.array(points)  # Convert to numpy array for easy indexing
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Scatter plot of points
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c='red', marker='o')

    # Labels
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")
    ax.set_title("3D Point Plot")

    plt.show()

def plot_3d_arrows(points, origin=(0, 0, 0)):
    """
    Plots a set of 3D points as arrows from a common origin.

    :param points: List or array of (x, y, z) coordinates.
    :param origin: The starting point of the arrows (default: (0, 0, 0)).
    """
    points = np.array(points)  # Convert to numpy array
    origin = np.array(origin)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Extract components
    x, y, z = origin  # Origin coordinates
    u, v, w = points[:, 0], points[:, 1], points[:, 2]  # Endpoints of arrows

    # Plot arrows
    ax.quiver(x, y, z, u, v, w, color='r', length=1, normalize=True)

    # Set axis labels
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")
    ax.set_title("3D Arrow Plot")

    plt.show()


"""c1 = Camera()
#c1.change_angle(yaw=45)
c1.print_data()
p1=c1.generate_rays_test(140,80)
print(p1)
plot_3d_points(p1)
#plot_3d_arrows(p1)"""