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

    def add_object(self, object):
        self._space.add_object(object)

    def create_window(self):
        self._root = tk.Tk()
        self._root.title("Renderer")
        self._root.geometry(f"{self._width}x{self._height}")  # Set window siz e
        self._img = tk.PhotoImage(width=self._width, height=self._height)
        self._label = tk.Label(self._root, image=self._img)
        self._label.pack()
        self._root.after(1, self.update)
        self._root.mainloop()

    def update(self):
        # change angle is called just for demo purposes, comment out for static camera
        self._camera.change_angle(yaw=random.randint(-10,10))
        self._camera.change_angle(pitch=random.randint(-10,10))
        self._camera.move_origin(0.3,.1,0)
        self._camera.print_data()

        # Create a list of rays that were generated
        self.fill_image
        self._root.after(UPDATE, self.update)

    def fill_image(self):
        image = np.empty(self.width, self.height)
        rays = self._camera.generate_rays(self._width, self._height)
        img = self.get_color_of_every_ray(rays)
        img = Image.fromarray(img.astype(np.uint8)) # May need to rotate and flip or transpose first. Origin is top left, but width may be inverted
        img = ImageTk.PhotoImage(image)
        self._label.configure(image=img)
        self._label.image = img
    
    def get_color_of_every_ray(self, rays):
        """
        Gets the color of every ray on the screen. returns a width x height matrix
        """
        objects = np.array(self._space.object_list())
        func = np.vectorize(self.get_color_of_ray)
        return func(rays, objects)
        
    def get_color_of_ray(self, ray, objects):
        """
        Gets the color of the closest intersection for a ray. Returns a tuple of the form (r,g,b)
        """
        values = self.get_t_and_color_for_objects(objects, ray)
        mask = np.array([bool(cell[1]) for cell in values])
        new_values = values[mask]
        index = np.argmin([cell[0] for cell in new_values])
        return new_values[index][1]
        
    def get_t_and_color_for_objects(self, objects, ray):
        """
        returns an 1 x m array for m objects. Each cell is (t, (r,g,b)).
        """
        func = np.vectorize(self.get_smallest_t_and_color_for_solid)
        return func(objects, ray)

    def get_smallest_t_and_color_for_solid(self, solid, ray):
        """
        Gets the t value and color for every surface in the solid, then finds the color of the smallest t value which intersects a surface.
        returns a tuple of the form (t, (r,g,b))
        """
        solid = self._space.get_object(solid)
        values = self.get_t_and_color_for_solid(solid, ray)
        mask = np.array([bool(cell[1]) for cell in values])
        new_values = values[mask]
        index = np.argmin([cell[0] for cell in new_values])
        return new_values[index]
        
    def get_t_and_color_for_solid(self, solid, ray):
        """
        Returns a 1xn array with each cell containing the t value and color for a given surface
        """
        surfaces = solid.get_surfaces()
        func = np.vectorize(self.get_t_and_color)
        return func(surfaces, ray)
        
    def get_t_and_color(self, surface, ray):
        """
        Returns the t value for a given surface and the color if a ray intersects it
        """
        t = surface.find_t(ray)
        color = surface.check_if_ray_intersects_surface(ray, t)
        return (t, color)

    def get_pixel_colors(self, rays):
        # REFACTOR
        start = time.time()
        objects = self._space.objects()
        image = np.empty(self._width//2, self._height//2)
        for x in range(self._width//2):
            for y in range(self._height//2):
                ray = rays[x][y]
                t_min = None
                color_min = None
                # For every solid, check if any of its surfaces intersect with the ray
                for object in objects:
                    solid = self._space.get_object(object)
                    for surface in solid.get_surfaces():
                        t = surface.find_t(ray)
                        color = surface.check_if_ray_intersects_surface(ray, t)
                        if color is False:
                            continue
                        if t_min is None:
                            t_min = t
                            color_min = color
                        else:
                            if t < t_min:
                                t_min = t
                                color_min = color
                
                # Now get the color for that surface
                image[x][y] = color_min
        return image

    def place_color_on_screen(self, colors: np.ndarray):
        # I may need to transpose or rotate the color
        image = Image.fromarray(colors.astype(np.uint8))
        image = ImageTk.PhotoImage(image)
        self._label.configure(image=image)
        self._label.image = image
        
    def render_screen_vectorized(self,rays,origins):
        start = time.time()
        objects = self._space.objects()
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
