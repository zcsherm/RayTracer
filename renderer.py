import random
import timeit
import time
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
UPDATE = 100

# To do:
# Add lighting, to be lit, surfaces must be parallel to perpendicular to the normal of the lighting,
# Add wireframe, check if any neighbor pixel was rendered using a different surface, if so, then color black

class Renderer:
    def __init__(self,width,height):
        self._width = width
        self._height = height

    def add_camera(self,camera):
        self._camera = camera

    def add_space(self,space):
        self._space = space

    def color_pixel(self,x,y,color):
        self._img.put(color,(x,y))

    def color_pixel_big(self,x,y,color):
        self._img.put(color,(x,y))
        self._img.put(color, (x+1, y))
        self._img.put(color, (x, y+1))
        self._img.put(color, (x+1, y+1))

    def add_surface(self,surface):
        self._space.add_object(surface)

    def add_solid(self,solid):
        for s in solid.get_surfaces():
            print(s)
            self.add_surface(s)

    def create_window(self):
        self._root = tk.Tk()
        self._root.title("Renderer")
        self._root.geometry(f"{self._width//2}x{self._height//2}")  # Set window siz e
        self._img = tk.PhotoImage(width=self._width//2, height=self._height//2)
        self._label = tk.Label(self._root, image=self._img)
        self._label.pack()
        self._root.after(1, self.update)
        self._root.mainloop()

    def update(self):
        # change angle is called just for demo purposes, comment out
        self._camera.change_angle(yaw=random.randint(-10,10))
        self._camera.change_angle(pitch=random.randint(-10,10))
        self._camera.move_origin(0.3,.1,0)
        self._camera.print_data()
        print(self._camera.get_heading())
        #self._canvas.create_rectangle(0,0,self._width,self._height,fill='white')
        # Create a list of rays that were generated
        rays,origins = self._camera.generate_rays_vectorized(self._width//2,self._height//2)
        self.render_screen_vectorized(rays,origins)
        # How many rays were made
        counter = 0
        #self.render_screen(rays)
#        for ray in rays:
            # Every height pixels, we go to the next column
#            pixel_x = counter // self._height
            #pixel_y = self._height - counter % self._height
#            pixel_y = counter % self._height
            # Reset the appearance of the canvas
#           self.color_pixel(pixel_x,pixel_y,'white')
#            surfaces = list(self._space.surfaces().values())
            # This helps us decide which to render, only the one with the lowest t value
#            min_t = 999999999

#            for surface in surfaces:
#                result = surface.check_intersection(ray)
#                if result:
#                    if result[0]<min_t and result[0]>0:
#                        min_t = result[0]
#                        color = surface.color()
#                        if color == 'green':
#                            #print(ray.direction())
#                            #print(pixel_x,pixel_y)
#                            pass
#                        self.color_pixel(pixel_x,pixel_y,color)

            #self.color_pixel(rays[0],rays[1],rays[2])

#            counter += 1
        self._root.after(UPDATE, self.update)

    def intersect_rays_surfaces(self,ray_origins, ray_directions, vertices, side_one, side_two):
        """
        Vectorized Möller–Trumbore algorithm for ray-triangle intersections.

        :param ray_origins: (N, 3) array of ray origins
        :param ray_directions: (N, 3) array of ray directions
        :param vertices: (M, 3) array of triangle vertex 0 positions
        :param side_one: (M, 3) array of triangle first edge vectors
        :param side_two: (M, 3) array of triangle second edge vectors
        :return: (N, M) array of intersection distances, -1 if no intersection
        """

        # Compute h = cross(ray_direction, side_two) for all rays and all surfaces
        h = np.cross(ray_directions[:, None, :], side_two[None, :, :])  # Shape: (N, M, 3)

        # Compute determinant a = dot(side_one, h)


        #a = np.einsum('nij,mj->nm', h, side_one[None, :, :])  # Shape: (N, M)
        a = np.einsum('nij,ij->ni', h, side_one)
        # Filter out near-zero values (ray parallel to triangle)
        parallel_mask = np.abs(a) < 1e-12
        a[parallel_mask] = np.inf  # Avoid division by zero

        # Compute s = ray_origin - vertex_0
        s = ray_origins[:, None, :] - vertices[None, :, :]  # Shape: (N, M, 3)
        #s = ray_origins-vertices
        # Compute u = dot(s, h) / a

        u = np.einsum('nij,nij->ni', h, s) / a  # Shape: (N, M)
        u_mask = (u < 0) | (u > 1)

        # Compute q = cross(s, side_one)
        q = np.cross(s, side_one)  # Shape: (N, M, 3)

        # Compute v = dot(ray_direction, q) / a
        v = np.einsum('nij,nj->ni', q, ray_directions) / a  # Shape: (N, M)
        v_mask = (v < 0) | (u + v > 1)

        # Compute t = dot(side_two, q) / a (ray intersection distance)
        #t = np.einsum('mij,mj->mi', q, side_two) / a  # Shape: (N, M)
        t = np.sum(q * side_two[None, :, :], axis=2) / a
        #t = np.einsum('mij,mij->mi', q, side_two[None, :, :]) / a
        # Filter invalid intersections
        t[(parallel_mask | u_mask | v_mask)] = -1

        return t  # Shape: (N, M) where N = rays, M = surfaces


    def render_screen_vectorized(self,rays,origins):
        start = time.time()
        vertices, edge_ones, edge_twos, colors = self._space.surfaces_2()
        t = self.intersect_rays_surfaces(origins,rays,vertices,edge_ones,edge_twos)
        closest_t = np.min(np.where(t > 0, t, np.inf), axis=1)
        print(closest_t.shape)
        new_rays = self._camera.generate_rays(self._width//2,self._height//2)
        counter=0
        size = new_rays.size
        new_rays = np.reshape(new_rays, (size,))
        closest_t[closest_t == np.inf] = -1  # No intersection
        closest_surface_indices = np.argmin(np.where(t > 0, t, np.inf), axis=1)
        closest_surface_indices[closest_t == -1] = -1
        ray_colors = np.where(closest_surface_indices[:, None] == -1,
        #                      "black",  # String for no hit (black)
                                [128,0,0],
                              colors[closest_surface_indices])
        #print(colors)
        #print(ray_colors.shape)
        end = time.time()
        print(f"time: {end-start}")
        #ray_colors = np.delete(ray_colors,1,1)
        #shaped_colors = ray_colors.reshape(self._height//2,self._width//2,3)
        shaped_colors = ray_colors.reshape(self._width//2,-1,3).transpose(1,0,2)
        print(f'shape: {shaped_colors.shape}')
        #shaped_colors=ray_colors
        start = time.time()
        image = Image.fromarray(shaped_colors.astype(np.uint8))
        tk_image = ImageTk.PhotoImage(image)
        self._label.configure(image=tk_image)
        #image.show()
        self._label.image = tk_image
#        for y in range(self._height//2):
#            for x in range(self._width//2):
#                #self.color_pixel_big(2*x,2*y,shaped_colors[y][x])
#                self.color_pixel_big(2*x,2*y,shaped_colors[self._height//2*x+y][0])
        end = time.time()
        print(f"time: {end - start}")

    def render_screen(self,rays):
        # Deprecated function. Performs calculation element wise.
        #print(rays)
        start = time.time()
        t= 0
        for y in range(self._height//2):
            for x in range(self._width//2):
                min_t = 99999999
                surfaces = list(self._space.surfaces().values())
                for surface in surfaces:
                    new_start = time.time()
                    result = surface.check_intersection(rays[y][x])
                    end = time.time()
                    t += end - new_start
                    if result:
                        if result[0] < min_t and result[0] > 0:
                            min_t = result[0]
                            color = surface.color()
                            if color == 'green':
                                # print(ray.direction())
                                # print(pixel_x,pixel_y)
                                pass
                self.color_pixel_big(2*x, 2*y, color)
        end = time.time()
        print('time was ', t)
