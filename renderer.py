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
        self._count = 0

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
        self._root.after(100, self.update)
        self._root.mainloop()

    def update(self):
        # change angle is called just for demo purposes, comment out for static camera
        self._camera.add_rotation(yaw=random.randint(-10,10))
        self._camera.add_rotation(pitch=random.randint(-10,10))
        self._camera.add_movement(0.3,.1,0)
        self._camera.print_data()

        # Create a list of rays that were generated
        self.fill_image()
        self._root.after(UPDATE, self.update)

    def fill_image(self):
        rays = self._camera.generate_rays(self._width, self._height)
        img = np.array(self.get_color_of_every_ray(rays), dtype=object)
        img = np.rot90(img)
        print(img)
        img = Image.fromarray(img.astype(np.uint8)) # May need to rotate and flip or transpose first. Origin is top left, but width may be inverted
        img = ImageTk.PhotoImage(img)
        self._label.configure(image=img)
        self._label.image = img
    
    def get_color_of_every_ray(self, rays):
        """
        Gets the color of every ray on the screen. returns a width x height matrix
        """
        objects = self._space.object_list()
        img = [[self.get_color_of_ray(ray, objects) for ray in ray_row] for ray_row in rays]
        print(img)
        return img
        
    def get_color_of_ray(self, ray, objects):
        """
        Gets the color of the closest intersection for a ray. Returns a tuple of the form (r,g,b)
        """
        self._count += 1
        print(self._count)
        values = np.array(self.get_t_and_color_for_objects(objects, ray), dtype=object)
        mask = np.array([bool(cell[1]) for cell in values])
        new_values = values[mask]
        if len(new_values):
            index = np.argmin([cell[0] for cell in new_values])
            return new_values[index][1]
        return (0, 0, 0)
        
    def get_t_and_color_for_objects(self, objects, ray):
        """
        returns an 1 x m array for m objects. Each cell is (t, (r,g,b)).
        """

        return [self.get_smallest_t_and_color_for_solid(s, ray) for s in objects]

    def get_smallest_t_and_color_for_solid(self, solid, ray):
        """
        Gets the t value and color for every surface in the solid, then finds the color of the smallest t value which intersects a surface.
        returns a tuple of the form (t, (r,g,b))
        """
        solid = self._space.get_object(solid)
        values = np.array(self.get_t_and_color_for_solid(solid, ray),dtype=object)
        mask = np.array([bool(cell[1]) for cell in values])
        new_values = values[mask]
        if len(new_values):
            index = np.argmin([cell[0] for cell in new_values])
            return new_values[index]
        return (0, False)
        
    def get_t_and_color_for_solid(self, solid, ray):
        """
        Returns a 1xn array with each cell containing the t value and color for a given surface
        """
        surfaces = solid.get_surfaces()
        return [self.get_t_and_color(s, ray) for s in surfaces]
        #func = np.vectorize(self.get_t_and_color, otypes=[object])
        #return func(surfaces, ray)
        
    def get_t_and_color(self, surface, ray):
        """
        Returns the t value for a given surface and the color if a ray intersects it
        """
        #print(surface)
        t = surface.find_t(ray)
        #print(t)
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

