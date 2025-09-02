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
$$(x, y, z) = (0, 0, 0) + t(0, 0, 1)$$ 
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

If you experiment with other parallelograms, you'll notice that these methods don't always work. In the first case, it's because our vectors are perpendicular to each other and pretty neatly oriented about the origin. The second case depends on the y component equaling 2.  So perhaps, the first wone is the one we want to explore more.

##### The actual equations....maybe

We should now be aware that the formulas we use on a day to day basis have a lot of assumptions baked right into them. For our using our 2 edges approach, it's helpful if we consider the case where it doesn't hold up. Suppose we have 2 edges both with a length of 1. Now let's make the angle between them tiny, say maybe 5 degrees. Our parallelogram is just a thin little sliver of a shape, and should have a fairly small area. If we compare it to a square with sides of one, it's pretty clear that the square has a much larger area. Using this observation, we can surmise that the area of a parallelogram is dependent on both the size of the lengths and the angle between them. $L*W$ works for a square, but is too large for our thin sliver. We need some sort of function of the angle that is 1 when our angle is 90 and gets smaller with smaller angles. Hey, that's what Sine is!

With that in mind we can safely assume that the area for any parallelogram is given by

$$
LW*sin(\theta)
$$

The more commonly used formula is:

$$
LH
$$

Where $H$ is the distance between $L$ and its parallel line 

Now, hopefully you see the assumption in these questions: We are using scalar magnitudes to represent the lines, rather than vectors. The equations that we've memorized don't care about the shapes position in space, only the measured length. If we rewrite these equations we can get (if we assume the lower left vertex is at the origin):

$$
|AB||AC|*sin(\theta)->sqrt(B_x^2+B_y^2)*sqrt(C_x^2+C_y^2)*sin(\theta)
$$

$$
|AB|H| -> sqrt(B_x^2+B_y^2)*H
$$

Well... what the hell is $H$ in vector form?

For this, we need to use a little trick called projection. Vector projection lets us see how much one vector 'casts' to another. It's easier to visualize it like shadows.
Consider one arrow stretching flat across the x axis, and another that's short and pointing up at a $45\degree$ angle. 
From the tip of our upward pointing arrow, draw a line straight down to the x-axis. The projection is the vector from the start of our x axis arrow to that point. It's as if the sun was directly above our vectors; The projection is how long the shadow would be.

You might also have noticed that the length of the line we drew from one vector down to the other, has a magnitude of $H$
To find out $H$ we can exploit the pythagorean theorem, since vector projections always form a 90 degree angle with the base
Our projection vector is given by:

$$
\frac{AB*AC}{\|AB\|}*AB
$$

Thus, $H$ equals:

$$
H^2=\|AC\|^2 - \|\frac{AB*AC}{\|AB\|}*AB\|^2
$$

$$
H^2 = (C_x^2+C_y^2)-\|\frac{B_xC_x+B_yC_y}{\sqrt{B_x^2+B_y^2}}*AB\|^2
$$

This gets messy very quickly, and thankfully, there's an easier way to look at all of this:

Let's break down our area formula and see if we can get any interesting insights from it.

$$
LWsin(\theta)
$$

Again, our understanding of geometry began with magnitudes rather than vectors, so let's show that

$$
\|A\|\|B\|sin(\theta)
$$

$$
\sqrt{A_x^2+A_y^2}\sqrt{B_x^2+B_y^2}sin(\theta)
$$

Our simple formula is hiding some rather ugly math. Our original equation $LW$ hinged only 2 assumptions: We only know the magnitudes of the sides, and our $sin(\theta)$ is equal to 1. Let's add a third assumption: One of our vectors is aligned along the x-axis. We'll see why this is convenient later. If we have the components of our vectors we can actually redfine the sine portion of our equation as such (alpha and beta represnting the angle of our 2d vectors from the x axis):

$$
sin(\theta) = sin(\alpha)
$$

$$
sin(\theta) = \frac{A_y}{\|A\|}
$$

$$
sin(\theta) = \frac{A_y}{\sqrt{A_x^2+A_y^2}}
$$

Now if we plug this into our earlier equation:

$$
Area = \sqrt{A_x^2+A_y^2}\sqrt{B_x^2+B_y^2} \cdot \frac{A_y}{\sqrt{A_x^2+A_y^2}}
$$

$$
Area = A_y\sqrt{B_x^2+B_y^2}
$$

$$
Area = B_xA_y
$$

For a rectangle aligned along the x-axis, this is equivalent to $LW$ as the magnitude of each vector is equivalent to its non-zero component. For a parallelogram aligned along the x-axis (where the $A$ vector has a non-zero x and y component), this equation equals the commonly known equation of $BH$. In this case $A_y$ is equivalent to the height of the parallelogram. If our vectors are not aligned along the axes, the equation gets much messier with:

$$
sin(\theta) = \sin(\alpha)cos(\beta)-sin(\beta)cos(\alpha)
$$

Note that when our B vector is aligned with the x-axis, the second term equals 0 and the first term is simply $sin(alpha)$, which is our earlier equation.

$$
sin(\theta) = \frac{A_y}{\|A\|}\frac{B_x}{\|B\|} - \frac{B_y}{\|B\|}\frac{A_x}{\|A\|}
$$

$$
sin(\theta) = \frac{A_yB_x-A_xB_y}{\sqrt{A_x^2+A_y^2}\sqrt{B_x^2+B_y^2}}
$$

The numerator of this equation will become very important later, and if you're familiar with linear algebra you can probably recognize it.

$$
Area = \|A\|\|B\|\frac{A_yB_x-A_xB_y}{\sqrt{A_x^2+A_y^2}\sqrt{B_x^2+B_y^2}}
$$

$$
Area = \sqrt{A_x^2+A_y^2}\sqrt{B_x^2+B_y^2}\frac{A_yB_x-A_xB_y}{\sqrt{A_x^2+A_y^2}\sqrt{B_x^2+B_y^2}}
$$ 

$$
Area = A_yB_x-A_xB_y
$$

That's kinda wild. If we know the components of our vectors we can find the area of the parallelogram between them with a really simple equation. No trigonometry required. Let's rewrite that formula slightly.

$$
A_xB_y-A_yB_x
$$

This is what's known as a determinant. The determinant is a measure of the dimensions of a set of vectors. You can think of it like how much they span, though this is technically incorrect as span has a very specific definition. If that's still confusing let's break down a bit more. Let's take our two vectors and imagine we want get an arbitrary point that exists between them. If we want to get the top right corner of the parallelogram we would just use $A+B$ and that points to the corner. What if we wanted to get the point halfway up the right edge? Well, that's just $.5A + B$. A point smack dab in the middle? That's just $.5A+.5B$. Thus, any point in the parallelogram is given by:

$$
P=\alpha A + \beta B,\ \ \ \text{where:  }\  0\le \alpha \le 1\ \text{and}\ 0\le\beta\le1
$$

The determinant is a handy way of telling us how much 'space' we have to play with using these vectors.

If we set our vectors side by side:

$$
(3,0),(0,2) -> \begin{bmatrix}
3 & 0 \\
0 & 2 
\end{bmatrix}
$$

We get a 2x2 Matrix with a determinant of 6. Please note that for diagonal matrices like this one (0's in every cell that isn't on the diagonal), the determinant is also the product of the diagonal entries. Depending on the order we list our vectors, the sign of the determinant changes. Let's think about what the sign means.

If our area is either 6 or -6, what is that trying to tell us? An area can't be negative like a scalar value can be. It doesn't represent a void that consumes positive space. Instead, the sign is telling us which way our space is 'facing'. You'll remember that angles that open up from the x axis are positive, while angles the open downward are negative. The same is true for areas. Suppose we look at the square formed by $(1,0)$ and $(0,1)$. If we imagine that we swept out the area from $(1,0)$, we are moving with a positive angle. That means the area should be positive. If we do the reverse and sweep from $(0,1)$ we move with a negative angle. This means our area is negative.

If our square was a piece of paper with a picture on one side on a table, the sign of the area is trying to describe which way it faces; Positive means it's face up and we can see it, negative means it's face down on the table and we cannot see the picture.

In 2 dimensions, 'facing' is an artifact from 3 dimensions, and doesn't really exist or matter (outside of certain applications). Thus, we usually only concern ourselves with the absolute value of the area. $LW$ is the same as $WL$, but $L_xW_y-L_yW_x$ is not the same as $L_yW_x-L_xW_y$. More accurately, we treat 2-dimensional math as though it were a plane in 3D space, and our perspective is facing it head on. This means the $Z$ component can only be binary: positive or negative. Ok, so hold up. If we know the sign of the $Z$ component, and we're assuming the $Z$ points only straight up or down through $(0,0)$, can't we give the Z component any arbitrary value? Better yet, let's assign it the determinant! Now we've got a vector that is orthogonal to both original vectors with a magnitude equal to the area of the parallelogram that they form. This is what the cross product is doing!

#### Cross product time

Now, there's one last step to our understanding: Make it all 3D. If we go back to our vectors $(3,0)$ and $(0,2)$, we can make these 3D with relative ease. $(3,0,0)$ and $(0,2,0)$ essentially just aligns our plane along the $x$ and $y$. We know that our $z$ component is going to be $+-6$. So our vector is (x, y, +-6). If the $x$ and $y$ component were anything other than 0, our vector wouldn't be pointing straight away from the shape. That means our resultant vector is $(0, 0, +-6)$; it faces either straight up or straight down from the plane. The sign tells us which direction the plane is pointing while the magnitude is the area of the parallelogram from $(3,0)$ and $(0,2)$. We can say that the (incomplete) formula for the cross product must be:

$$
A \times B = \begin{bmatrix}
x \\
y \\
A_xB_y-A_yB_x
\end{bmatrix}
$$

Let's consider one other example to find out what the x and y components should be.

Let $A=(1,4,0)$ and $B=(3,3,0)$. We can intuit that our resultant vector is going to point straight up our down like our last, which means it's going to equal:

$$
A \times B = \begin{bmatrix}
0 \\
0 \\
A_xB_y-A_yB_x=-9
\end{bmatrix}
$$

Symmetry suggests that the $x$ and $y$ components will have similar equations, and that the equation should equal 0.

$$
x = \alpha - \beta = 0
$$
$$
y = \gamma - \delta = 0
$$
$$
\alpha = \beta
$$ 
$$
\gamma = \delta
$$

There is a really easy way to get this inequality to balance: Assume that $A_z$ and $B_z$ are components of each:
$$
A_zB_? - A_?B_z
$$
$$
A_?B_z - A_zB_?
$$

If we look to symmetry we can deduce that the unknown components on each side of an equation are the same (x and x, y and y). If the $z$ component was found using the x and y components, it follows that the $x$ component uses $y$ and $z$. So our full formula is:

$$
A \times B = \begin{bmatrix}
A_yB_z-A_zB_y \\
A_zB_x-A_xB_z \\
A_xB_y-A_yB_x
\end{bmatrix}
$$

This is the full formula of the cross product. It produces a vector that is orthogonal to the plane of 2 other vectors and has a magnitude equal to the area of the parallelogram formed by those vectors. More specifically, the magnitude of the resultant is equal to the product of the other 2 vectors magnitude and sine of the angle between them. This is why the cross product is so important and has so many applications. The main use in this ray tracer is to find the Normal vector for a given surface, and computing the area of a surface.

Remember how a the sign was all that determined the direction for the cross product in 2 dimensions and how it was binary? Well, in 3 dimensions, a surface could be facing in an infinite number of directions. That's why a 3 dimensional cross product must give us a 3 dimensional resultant; facing can be encoded as a binary in 2 dimensions, but needs to be a vector in infinite directions.

Let's see if we can tie it all together and if this has given us a deeper insight into what the hell the cross product actually does.

In 3 dimensions and with arbitrary points, the cross product finds a vector perpendicular to a surface, and finds the area contained by the basis vectors of that surface. 

$$
A \times B = \begin{bmatrix}
A_yB_z-A_zB_y \\
A_zB_x-A_xB_z \\
A_xB_y-A_yB_x
\end{bmatrix}
$$
$$
Area = \|A\times B\|
$$

Now if we imagine our surface is on the plane of $z=0$, then we know the following to be true:

$$
A \times B = \begin{bmatrix}
0 \\
0 \\
A_xB_y-A_yB_x
\end{bmatrix}
$$

$$
Area = A_xB_y-A_yB_x = C_z
$$

Based on our assumptions, we don't really care about the resultant vector, only its magnitude and sign. Now let's add another assumption: we only care about magnitudes (afterall this is what we physically measure). So instead of vectors, we say a parallelogram with sides of 2 and 3 and a height of 1. This let's assume assume one vector is aligned along the x axis and thus has a null $y$ component.

$$
Area = A_xB_y = base \cdot B_y = base \cdot height
$$

Hopefully this illustrates how our simple area formulas are shorthands for very specific cross products and how the cross product is what we've actually been doing since elementary school. We've already shown how the square is a specific instance of our formula where $height = B_y = \|B\|$, but almost all area formulas are simple implementations of this as well.

##### Triangle:

$$
\frac{\vec{A} \times \vec{B}}{2} = \frac{1}{2}bh
$$

##### Trapezoid:

$$
\frac{a+b}{2}h =ah + \frac{b-a}{2}h = C\times A + \frac{(B-A)\times C}{2}
$$

##### Hexagon:

$$
\frac{3 \sqrt{3}}{2}a^2 = 3 \|A_1\|\|A_2||\sin(120^\circ) = 3\frac{\sqrt{3}}{2}\|A||^2 = 3(A_1 \times A_2)
$$

Though, trigonometric functions are still needed for this one if we want to get the vectorized form of each side.


#### Why?

There is still the question of why this works. While I love analyzing things with no established axioms, I think we're better off accepting that it just works.

No?

Fine, let's see if we can figure it out.

Let's imagine any plane that's not aligned with any of our basis axes.
Our normal vector is going to point off into another arbitrary direction.
Imagine we are constructing our normal, component by component.
If we start with the $z$ component, we get a vector that either points straight forward, or staight away.
Then if we move on the $x$ component, our vector yaws to either side.
Finally, the $y$ component causes our vector to pitch up or down.

It should be clear that the normal is being dialed in, bit by bit. This suggests there is something systematic and innate that's causing this
It might be helpful to consider an alternative definition:

$$
\vec{A} \cdot \vec{C} = 0 = \vec{B} \cdot \vec{C} 
$$

$$
A_xC_x + A_yC_y + A_zC_z = 0 = B_xC_x + B_yC_y + B_zC_z
$$

This tells us that our resultant vector is only orthogonal to both bases vectors if it balances these equations. From this, it should be pretty clear that $C$ doesn't have very much freedom if $A$ and $B$ are fixed. Another detail hidden by this is that the length of $C$ is irrelevant. Any vector that is a scalar multiple of $C$ is going to balance the equation. 

There's not too much that we can do with this equation at a basic level other than to recognize that the set of solutions for $C$ lies upon a line; the nature of this balancing act forces a unique solution.

It still doesn't sufficiently explain why $z$ is determined by the $x$ and $y$. For that, it'll help to step back into 2D land. Suppose we have the following vectors:

$$
A = \begin{bmatrix}
1 \\
1 \\
1
\end{bmatrix}
B = 
\begin{bmatrix}
3 \\
2 \\
4
\end{bmatrix}
$$

If we drop them to 2D by losing the z coordinate we get:

$$
\begin{bmatrix}
1 \\
1
\end{bmatrix} \text{ and } \begin{bmatrix}
3 \\
2
\end{bmatrix}
$$

This gives us an illusion of our original 2 vectors; a projection. For all intents and purposes we can view these 2 vectors as though we grew them on graph paper. If we wanted to draw a line that is perpendicular to both vectors, we cannot on the paper. We are limited by our 2 dimensions. The only direction that satisfies the condition is straight up from the page, which means we have to introduce a 3rd dimension. So our perpendicular vector is some multiple of:

$$
\begin{bmatrix}
0 \\
0 \\
1
\end{bmatrix}
$$

Because our dot product equation from earlier showed us how each component of the cross product is dependent on the other components, we know it cannot be an arbitrary value. For now, let's assume the multiple is the area between the 2D vectors.

$$
\begin{bmatrix}
0 \\
0 \\
-1
\end{bmatrix}
$$

Now, let's repeat this, but imagine we're looking at our vectors from the side. Specifically, our point of view is aligned along the x axis. This means we can lop off the x coordinates:

$$
\begin{bmatrix}
y=1 \\
z=1
\end{bmatrix} \text{ and } \begin{bmatrix}
y=2 \\
z=4
\end{bmatrix}
$$

Much like our last example, we know that our normal to these 2 is going to only have an $x$ component. Again, let's assume that it's gonna be the area between these 2.

$$
\begin{bmatrix}
2 \\
0 \\
0
\end{bmatrix}
$$

If we do the same thing but with the $y$ axis, we get a normal of:

$$
\begin{bmatrix}
0 \\
-1 \\
0
\end{bmatrix}
$$

Now, if add these vectors together, we actually get the normal for our original 3 dimensional coordinate plane.

$$
\begin{bmatrix}
2 \\
-1 \\
-1
\end{bmatrix}
$$

This should illustrate exactly how the normal gets dialed in and how the normal is constructed by examining the plane along each basis vector. It also demonstrates how the area of our surface is a construction from each of these 'projected areas'. Each of the projections we examined had an area of 2, 1, and 1. Our actual surface had an area of $\sqrt{6}$. Interestingly, the area of our surface is given by $\sqrt{A_1^2 + A_2^2 + A_3^2}$. I'll be honest, I can't think of an intuitive way to explain why the the surface area of a surface is found by the pythagorean theorem of the projected areas. At the very least, it demonstrates that if each component in the cross product is the area of that projection, the magnitude of the cross product must be the area of the unprojected surface.

This also demonstrates another interesting feature. If you don't really know what the shape is, and only know the sizes of these 3 shadows, you can actually determine the area of the shape and what direction it's facing. I'm not sure what sort of bizarro world this could be applied to, but it's a fun little nugget of knowledge.





## The Journey

My first venture into this project began in my vector calculus class. I realized that a visual field could be approximated by emitting vectors in a cone or similar shape. I later learned that this shape is called a frustum. It was at this point I connected the dots and realized that computer graphics could emulate a 3d environment by emitting a ray from every pixel in the direction defined by the line that pixel makes to the convergence point. I jumped into my IDE and went about implementing a prototype. This was harder said than done.

The first snag I ran into was how to define the objects in the environment. The instinctive answer was to use vertices and then generate line segments between these vertices. An objects would simply be the space bounded by these lines. That seemed to be an easy straight forward solution and I was confident I would have a working prototype that evening. So, there I was, My camera was emitting rays across the field of vision and I had objects defined in 3d space. Unfortunately, I had just realized that I need to determine if these rays intersect any of those surfaces. It was clear that this would be a 2 step problem. I was already familiar with: define the plane that the surface exists on, find the t value of the ray that intersects that plane, and then use that to get the coordinates. The second step was much more elusive: Determine if a point rested on the actual surface.

I was determined not to look up an answer to this problem. I ran through different possible solutions: doing hacky comparisons between components (i.e. checking that the x coordinate is greater than at least 1 x vertex coordinate and greater than 1 x vertex coordinate) or representing the point as a linear combination of 2 of the edges. It wasn't until I realized that a point that was inside a triangle divided the triangles area into 3 parts that summed to its whole, and that the angles between all lines from the point and the vertices summed to 2 pi. I later learned that was I was describing is called Barycentric Coordinates.

## Authors

Contributors names and contact info
