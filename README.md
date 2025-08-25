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
$$
P(t) = (0,0,0) + t(x,y,1)
$$
Where x and y are the cells coordinates. This ray also happens to describes the ray that projects outward from the photocell. If you guessed we can just use the vector field $$F(x,y,1) = i + j + k$$ you would be correct! Using these ray definitions we've emulated an important aspect of vision: As something moves closer to the viewer, it will occupy more of the visual field.

### Objects

#### Background

You may have noticed that our reality is occupied by things! Things have physical properties like volume and are composed of matter. While the metaphysics and real physics on the subject of matter and existence are fascinating, we can ignore most of it. For our illusion, we can treat and view objects like most people do: They just are. However, we can make an interesting distinction. We only have to worry about the surfaces of our objects.

#### Surfaces

If our goal is to eventually construct the yellow cube from our earlier example, we should start with the simplest type of surface we can think of. How about a triangle. 

We can define a triangle as the area bounded by 3 intersecting line segments. However, a simpler (and more effective) way is instead define it by the 3 intersections themselves. You probably recall that these are called vertices. A vertex is just a singular point in space defined by its (x,y,z) coordinates. We'll add some other interesting attributes to our vertices later, but just the 3 dimensional points will suffice for now. 

So our triangle is defined by these 3 vertices and the plane between them. Boom. Easy. Done. Until....

#### Plane equations, intersections, and barycentrics, oh my!

How do we actually tell if a ray collides with this triangle? It's a little tricky, but we can break it down into 4 steps:
1. Find the plane equation
2. Check if the ray and plane are parallel
3. Find the intersection between the ray and the plane
4. Determine if that point is actually inside the triangle

#### Plane Equations

We need a way of defining all of the points in space that exist inside our triangle. We could always discretize our simulation and collect the finite set of points in the triangle into a single collection. However, we want something that's continuous like reality (again, we'll ignore other interpretations of reality), less burdensome on memory, and more elegant. To do this, we first start with the plane that the triangle resides on. 

To help illustrate what this means, imagine our triangle is drawn on a piece of paper. If this our flat triangle in 3D space, the plane is that piece of paper. Except, imagine that the paper extends infinitely in either direction. If 3D space is defined by 3 dimensions stretching infinitely, a plane is a 2D subset of that space: 2 dimensions stretch infinitely, while one direction is flat. All flat shapes (like our triangle) are subsets of a plane.

The easiest plane to define would be the plane that stretches up and down the Y axis, and left and right along the X axis. This is a lot like our 2x2 grid from earlier. Since it stretches infinitely in the x and y directions, any combination of values for x and y are valid points. Just so long as the z component is 0. In essence any point of the form (x, y, 0) exists along this plane. While this is an easy way to understand a planes domain, we need an equation to really describe it well. 

Plane equations generally have the form of: 
$$F(x, y, z) -> Ax + By + Cz + D = 0$$
The values of A, B, C, and D are constants that make this statement true for certain combinations of (x,y,z). If this is hard to understand, try to equate it with the slope-intercept form of a slope: 
$$y=mx+b$$
If you rearrange the equation you get:
$$0=mx-y+b$$
A point is along the slope if its x and y coordinates make that equation truthy. The plane equation is just a slope equation, with an extra dimension. A slope defined by the equation $y=3x+2$ can be expanded to a plane by recognizing that $A=3, B=-1, D=2$ giving the plane equation $3x - y + 0z + 2 = 0$. This is rather trivial for planes that are aligned along axes, but finding the values of A,B,C, and D can be tricky if you don't know the method.

##### Normals and Cross Products

A, B, and C can be obtained at the same time, and rather easily if you know the trick. We just need to compute the normal of the plane.

The normal is a special vector. It's the vector that is orthogonal to a plane. You can envision this in a few ways. If our plane stretches infinitely in 2 directions, the normal is the line that stretches infinitely in the third direction. If our plane was a plot of land, trees on that plot grow in the direction of the normal. When you use the screen of your phone to find your way in a dark room, the screen is the plane and the direction of the light is the normal. Physics problems involving sums of forces make extensive use of normals.

The A, B, and C coefficients are simply the x, y, and z components of the normal. In the case of our plane along (x, y, 0), the normal vector pointing outward is given by (0, 0, 1). This means our plane equation is $$0x + 0y + 1z + D = 0 -> z + D = 0$$. 

Finding the normal requires a fun little operation called the cross product. This operation takes 2 vectors and finds a vector that is orthogonal to both. Point your left index finger forward, your middle finger to the right, and your thumb straight up. The cross product of your index and middle finger will equal your thumb.

The actual math of the cross product is frustrating. It's a simple function, but the ordering of each component is just a matter of rote memorization. If you're like me, this may not be your strong suit. The intuition for what it's actually doing and why it works at a geometric level is also not immediately clear. If you're doubly like me and 3D reasoning is your even worse suit, the intuition may forever elude you. I wouldn't worry about it for right now, and just treat the cross product as a black box.

Using the cross product to find the normal for a given plane means we need one of two things:
1. 2 vectors along the plane
2. 3 vertices on the plane
You may have noticed a few interesting things about this fact. These 2 statements are pretty much identical, and that we already have 3 vertices from our surface.

If our triangle is bounded by vertices $LMN$, we just need the line segments $LM$ and $MN$. These are given by $M-L$ and $N-M$. We can then find the cross product, $$LM x MN$$. The result of this function is our normal vector, $n=(A, B, C)$. 

##### Plane constant

The last item we need to find is the constant $D$. This is our plane constant. This is very similar to the intercept value in a slope intercept equation, and it may help to think of it as where the plane intercepts the normal.

Now, there's 2 ways to find $D$. The simplest way is to find any point in the plane (such as a vertex from our triangle) and plug those values into the $Ax + By + Cz + D = 0$ equation, then just solve for D. The second way is a little cleverer and I greatly prefer it.

You may have noticed something about the $Ax, By, Cz$ portion of the equation. If our normal is $(A, B, C)$ and our vertex is $(x, y, z)$, then the non-$D$ portion of the equation is the dot product of the normal and a point on the plane! If you're unfamiliar with the dot product, it's just the sum of an elementwise multiplication of two vectors. With this in mind, we can rewrite our equation as: 

$$
N*P + D = 0
$$

Which means that D can be simplified as the negative dot product of the Normal and a Point on the plane! Now, sometimes you'll see D listed as the positive dot product, and sometimes as the negative dot product. I prefer listing it as the negative dot product, as that's what you get with the plane equation (and your vector calculus teachers will mark you down for a flipped D value). However, keeping it as the positive is very helpful later on when checking intersections and is just easier to grok and remember.

There is one main takeaway you should remember from this: If a point $P$ is known to exist on a plane with the normal $N$, then a point $Q$ in space that satisifies the equation $P * N = Q * N$ also exists on the plane. 

##### Example

Suppose we have 3 points

$$
P = (1, 2, 3)
$$

$$
Q = (4, 3, 2)
$$

$$
R = (2, 0, -1)
$$

Try to image the triangle. If you're standing on the origin looking straight ahead, the triangle is going to form a roughly 45 degree angle with the ground and is tilted towards the origin.

To find the normal we construct our 2 line segments and find the normal:

$$
PQ = Q-P = (4-1, 3-2, 2-3) = (3, 1, -1)
$$

$$
RP = P-R = (1-2, 2-0, 3-(-1)) = (-1, 2, 4)
$$

$$
N = RP x PQ = (-6, 11, -7) 
$$

Note that we should try to stay consistent with the order we select our edges, as this determines the 'facing' of our surface.

Let's think about whether this makes sense: the triangle is angled upwards towards the ceiling, and when we turn, it's sorta pointing back at us. So we should expect the normal to point above our heads and behind us. With $(-6, 11, -7)$ it's clear that this normal points upwards and behind us. Cool!

Now, we find D:

$$
N*P + D = 0
$$

$$
(-6, 11, -7) * (1, 2, 3) + D = 0
$$

$$
(-6 + 22 - 21) + D = 0
$$

$$
D = 5
$$

Any arbitrary point $S$ in space is on the plane if either of these 2 equations are truthy:

$$
-6(Sx) + 11(Sy) + -7(Sz) + 5 =0
$$

$$
N * S = -5 = N * P
$$

#### Parallelism

With our plane equation in hand, we can start checking if our vision ray intersects the plane. But first, it's important to imagine and think about what situations a ray may or may not intersect a plane. One case that our ray doesn't intersect our plane, is if the plane is behind the origin of the ray. Afterall, we only care about objects in our line of vision. But what if the object is ahead of the origin? Is there any situation where the ray doesn't intersect with the plane created by that object? There exists only a single instance: if the ray is parallel to the surface.

Imagine you're in a race car travelling down an infinitely long straight stretch of road. This race car is special and can't turn and travels in a perfectly straight line. There is a guard rail on the right hand side of the road. No matter how far you go, you will never collide with the guard rail. This is because you're always going straight ahead, and the guard rail stretches in a straight line along the same direction. Your movement and the guard rail are parallel. Now, suppose that the guard rail was angled ever so slightly towards the center of the road. No matter how slight this angle is, your car will eventually collide with the guard rail; you and the guard rail are no longer parallel.



### Cross Product - revisited

If you can't stand treating the cross product as a black box, then let's see if we can work our way through the logic of it.

In 2 dimensions, we often find ourselves taking the area of a shape for granted. It really is a mystical operation and years of public school have made it seem less than it really is. We all innately know that a rectangle is $b*h$ and that a triangle is $1/2 b *h$ and so on and so forth. But somehow, we're taking the single dimensional sides of a shape and computing a scalar of a 2 dimensional construct: the area. You should note that many area formulas are similar or even the same. For example, the area of a rectangle is a special case of the area of a parallelogram, as $sin(90) = 1$. These equations are all special cases of 3 dimensional area equations, where the z component is 0.

Consider a rectangle with a base of 3 and a height of 2 and an area of 6. If we put this on on a 2D grid, we get a rectangle with 4 corners: $(0,0),(3,0),(0,2),(3,2)$. Let's see if we can play around with these numbers and see if we can get any new insights on what our number pushing means.

We can define the following vectors:

$$
E_1 = <3,0>\\\\  
E_2 = <0,2>,\\\\   
D_1 = <3, -2>, 
D_2 = <3, 2>
$$

We can get our target number in some interesting ways:

$$
||E_1||||E_2||
$$

$$
||D_1 + D_2||
$$

If you experiment with other parallelograms, you'll notice that these methods don't always work. This should tell you that these equations are actually special cases of a more general form. In the first case, it's because our vectors are perpendicular to each other and pretty neatly oriented about the origin.


## The Journey

My first venture into this project began in my vector calculus class. I realized that a visual field could be approximated by emitting vectors in a cone or similar shape. I later learned that this shape is called a frustum. It was at this point I connected the dots and realized that computer graphics could emulate a 3d environment by emitting a ray from every pixel in the direction defined by the line that pixel makes to the convergence point. I jumped into my IDE and went about implementing a prototype. This was harder said than done.

The first snag I ran into was how to define the objects in the environment. The instinctive answer was to use vertices and then generate line segments between these vertices. An objects would simply be the space bounded by these lines. That seemed to be an easy straight forward solution and I was confident I would have a working prototype that evening. So, there I was, My camera was emitting rays across the field of vision and I had objects defined in 3d space. Unfortunately, I had just realized that I need to determine if these rays intersect any of those surfaces. It was clear that this would be a 2 step problem. I was already familiar with: define the plane that the surface exists on, find the t value of the ray that intersects that plane, and then use that to get the coordinates. The second step was much more elusive: Determine if a point rested on the actual surface.

I was determined not to look up an answer to this problem. I ran through different possible solutions: doing hacky comparisons between components (i.e. checking that the x coordinate is greater than at least 1 x vertex coordinate and greater than 1 x vertex coordinate) or representing the point as a linear combination of 2 of the edges. It wasn't until I realized that a point that was inside a triangle divided the triangles area into 3 parts that summed to its whole, and that the angles between all lines from the point and the vertices summed to 2 pi. I later learned that was I was describing is called Barycentric Coordinates.

## Authors

Contributors names and contact info
