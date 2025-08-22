# A Ray Tracer and Renderer using Python and tkinter

Renders simple geometry that is capable of various transforms.

## Description

This library displays a 3d scene in a tkinter window. The scene utilizes simple, vertex based geometry and a rudimentary ray tracing algorithm. By building this in python and limiting the libraries used, a deep understanding of 3d graphics, matrix multiplication, and vector calculus can be achieved. However, this comes at a significant downside: performance. Avoiding OpenGL, low-level languages, and graphical python libraries, means that the frame rate is much slower than would be expected. This is hindered further by using tkinter to render the scene.

My goal with this project was to try to logic my way through the graphic rendering process, using as few resources as possible. 

## Road map

### What I'd like to add

* Instead of recalculating the normal and plane constant for every object, instead transform the ray by the inverse transformation matrix. This should allow for intersection checking at a much lower cost
* Add scale to objects (need to adjust all references to local coordinates)
* Add lens options, FOV adjustment
* Save every rendered image and stitch it together as a gif or video
* Wireframe mode
* Lighting

## How it works

For those curious about ray optics and 3d graphics, this guide aims to help walk through the concepts and math used.

### Prerequisites

While understanding how all this works can be done with no special background or previous knowledge, having some cursory understanding of the following will be exceedingly helpful.

* Vector math
  * Things like dot products and cross products, as well as normals, magnitudes, and unit vectors
* 3D Geometry
  * 3D coordinate math, line segments, and plane equations.
* Linear Algebra
  * Matrix multiplication, identity matrices, transpositions, and transformations
* Computer Science, Data Structures, and Algorithm Analysis
  * Knowledge in this domain is not necessary to understand the concept of ray tracing, but is vital for implementing an efficient implementation. For example, recognizing that using native python loops over every pixel, for every object in the scene, for every surface in the object, becomes expensive very quickly.
 
Don't feel discouraged if you are unfamiliar with these concepts. I like to think about this sort of material in the simplest ways possible and build up from there. This guide is written with as few established axioms as possible.

### Vision

#### Background

Richard Feynman once described computers as hyper efficient filing clerks. Their speed and efficiency allows them to mimic human actions, but the actual mechanism to achieve that action is wildly different than a humans. This can be thought of as a reverse cargo-cult: Computers enact completely different rituals, but achieve (what appears to be) the same result. A better way of describing it is that computers are masters of illusion.

Everything a computer does is an illusion; There is a sea of abstraction between the input and the output. Consider a Last Will and Testament. This document is very valuable, and its authenticity is important. The owner wants to make sure that the document is safe and can be accessed when they pass. The owner decides a safe is the best bet and locks the will in the safe. When they pass, the safe can be accessed and all parties are assured that the document is the original. The paper is the same, the ink is the same, and humans all agree that this is the same object that the owner had made years ago. Suppose that owner typed their Will on their computer. They can save that document to the hard drive, and their heirs can open it when they pass. Initially, most would agree that opening a saved word document is identical to getting the physical original out again. However, the computer doesn't save the document the same way we save a physical document. Afterall, it's just data; the word processor can look at the raw data and reconstruct the document upon request. This may be obvious, but it's important to recognize the distinction: Computers can take a human action and emulate it, humans recognize and equate the emulation with the original action, but the mechanism varies so much that the end result is an illusion of the original action. Typing a letter doesn't physical put the letter on a page like a typewriter does, projecting a movie on a screen doesn't put actors on the stage like a play would, and talking on the phone doesn't make their original sound waves hit your eardrums the way talking in person does.

Why is this important? Trying to emulate a 3D environment in a one-to-one parallel with reality is not feasible. Accepting that you're making an illusion gives you a lot more room to play and optimize what you're doing.

#### Vision (actually now)

In the physical world, vision is a biological phenomenon. Certain subatomic processes cause atoms to release energy. When this energy collides with another atom, some of it gets absorbed while some of it gets reflected. Most terrestrial life found it advantageous to exploit this fact. Life also found it helpful to exploit the fact that light is sometimes absorbed by objects. By specializing photoreceptors, life can pick up on how much was absorbed and discern between objects. From this we get a very general outline of how vision works:

* One object emits energy (light)
* The light travels through space
* The light bounces off objects and is changed by those objects
* The light collides with photoreceptors which signal the brain that light was detected
  
There are many other processes involved, but even trying to emulate this simple layout from the ground up is a fools errand.

If our goal is to create an illusion of all this happening, we can greatly simplify matters. First, let's assume that lighting is uniform in space. That is, visibility is not determined by a source of light. Let's also assume that light is never absorbed and that color is an intrinsic property of an object. With these suppositions, it's clear that we don't care how a light ray bounces around space before colliding with the eye; We only care about the very last reflection. This means we can treat light as a ray that travels from an object to the eye. If we invert this thought experiment, and instead have light travel from the eye to the object, the result is pretty much the same: We can see whatever object intersects that ray. 

#### Rays

Let's first examine how we can exploit the base case of our thought experiment. Consider vision with only a single photocell. For all intents and purposes, we can treat this photocell as a little square. A ray of light is fired from that square straight forward. Suppose that the ray then hits the side of a yellow cube that is some distance away. Our little square photocell will then turn yellow. Let's add some mathematical and geometric basis to our simulation.

Let's set our photocell to the origin in 3D space at (0, 0, 0) and let's assume it stretches 1 unit wide by 1 unit tall and 0 units deep. If this is hard to visualize, imagine it's a really thin square of paper. The ray that gets fired straight outward then has an origin point of (0, 0, 0) and a direction vector of (0, 0, 1). As a reminder, the equation for a ray and all of the points it intersects is given by: 
$$P(t) = Origin + Direction * t$$ 
Which means any point in 3d space that our ray intersects with is: 
$(x, y, z) = (0, 0, 0) + t(0, 0, 1)$ 
Where t is the distance from the photocell to that point.

Let's suppose we want to see more than just a tiny little square and are curious about the $k+1$ case. We're going to increase our photocells from 1 to 4, arranged in a 2x2 pattern at the origin. In this example, our origin points for each ray will be (0,0,0), (0,1,0), (1,0,0), and (1,1,0). If each ray is firing out in a straight line, then every direction vector is still going to be (0, 0, 1) (you might see why this will be a problem). So now it's just a matter of firing every ray outward and checking what they intersect with; each photocell can thus display a different color than either neighbor. This means our 2x2 grid has better image definition than our 1x1 

We've now considered the case of $n=1$ and $n=k+1$, so we can extrapolate this model out to any arbitrary dimension. For example, 1920x1080 photocells, or rather the number of pixels in a typical computer monitor. By associating each pixel on the screen to a 'photocell', we've established the first step in our illusion: how to emulate vision on a computer screen.

#### Frustums

In our 2x2 example, every cell had the same direction vector: (0, 0, 1). This creates an interesting problem; No sense of depth. 

Suppose our 2x2 grid moves closer to the yellow cube in front of it. Does the cube appear larger? If the grid moves away, does the cube appear smaller? As you may have guessed, it does not. Since all of our rays project outward in parallel lines, the cross-sectional area of our rays stays constant with respect to distance. In order to give the sense of depth that natural vision provides, we need to find a way to make closer objects absorb more rays than further ones. Or rather, the further our rays travel, the more area they should cover.

In essence we want our rays to create a positively divergent, radial vector field. If that doesn't make sense, consider a balloon with spots on it. As the balloon inflates, the spots not onnly get further from the center of the balloon, but further apart as well. The surface area of the balloon increases with the radius. It's just a matter of adapting this model to our 2x2 grid.

Consider if each photocell in our 2x2 grid was a dot on the surface of the balloon. After some inflation and expansion, our 2x2 grid might take up the space of a 3x3 grid. Then after a little more, maybe it takes the same space as a 4x4. Critically, it's important to remember that we aren't getting more photocells. They're just larger and take more space. Now lets overlay each of these planes in space. We have our 2x2 grid at 0-z, a 3x3 at 1-z, and a 4x4 at 2-z. If we connect the each corner of our grids we get a 3d shape called a frustum. An easy way to imagine a frustum is to take a pyramid and slice off the top of it. If our grid of photocells and pixels is the smaller of the 2 ends of the frustum, the volume of the frustum is the field of vision.

Let's see if we can find an easy way to define this vector field. An initial instinct might be to find the angle between opposite edges of the frustum and then subdivide that by the width and height. Then each ray projects outward in increments of that subdivision. This definitely works, but it involves using trigonometry and either defining our vectors using angles, or converting between angles and cartesian coordinates. Instead let's exploit how vector directions are defined.

Consider the top of the pyramid we lopped off to make our frustum. Center the tip at the origin and point it straight ahead along (0, 0, 1). Let's say the bottom of our pyramid tip is a 3x3 grid of photocells. Instead of being aligned with the origin, it's centered on (0, 0, 1). That's the location of the central photocell, while the top left corner is at (-1, 1, 1). If we create a ray from the origin to each cell, we can define it as: 
$$P(t) = (0,0,0) + t(x,y,1)$$
Where x and y are the cells coordinates. This ray also happens to describes the ray that projects outward from the photocell. If you guessed we can just use the vector field $$F{x,y,1} = i + j + k$$ you would be correct! Using these ray definitions we've emulated an important aspect of vision: As something moves closer to the viewer, it will occupy more of the visual field.

### Objects

#### Background

You may have noticed that our reality is occupied by things! Things have physical properties like volume and are composed of matter. While the metaphysics and real physics on the subject of matter and existence are fascinating, we can ignore most of it. For our illusion, we can treat and view objects like most people do: They just are. However, we can make an interesting distinction. We only have to worry about the surfaces of our objects.
 
## The Journey

My first venture into this project began in my vector calculus class. I realized that a visual field could be approximated by emitting vectors in a cone or similar shape. I later learned that this shape is called a frustum. It was at this point I connected the dots and realized that computer graphics could emulate a 3d environment by emitting a ray from every pixel in the direction defined by the line that pixel makes to the convergence point. I jumped into my IDE and went about implementing a prototype. This was harder said than done.

The first snag I ran into was how to define the objects in the environment. The instinctive answer was to use vertices and then generate line segments between these vertices. An objects would simply be the space bounded by these lines. That seemed to be an easy straight forward solution and I was confident I would have a working prototype that evening. So, there I was, My camera was emitting rays across the field of vision and I had objects defined in 3d space. Unfortunately, I had just realized that I need to determine if these rays intersect any of those surfaces. It was clear that this would be a 2 step problem. I was already familiar with: define the plane that the surface exists on, find the t value of the ray that intersects that plane, and then use that to get the coordinates. The second step was much more elusive: Determine if a point rested on the actual surface.

I was determined not to look up an answer to this problem. I ran through different possible solutions: doing hacky comparisons between components (i.e. checking that the x coordinate is greater than at least 1 x vertex coordinate and greater than 1 x vertex coordinate) or representing the point as a linear combination of 2 of the edges. It wasn't until I realized that a point that was inside a triangle divided the triangles area into 3 parts that summed to its whole, and that the angles between all lines from the point and the vertices summed to 2 pi. I later learned that was I was describing is called Baryonic Coordinates.

## Authors

Contributors names and contact info
