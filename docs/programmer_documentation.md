# CSG Editor - Programmer Documentation

## Table of Contents

1. [Core Components](#core-components)
2. [Module Reference](#module-reference)
2. [Algorithms](#algorithms)


## Core Components

### 1. CSG System (`csg.py`)
The heart of the application implementing Constructive Solid Geometry.

**Key Classes:**
- `Primitive`: Abstract base class for all geometric primitives
- `Box`, `Sphere`, `Cylinder`: Concrete primitive implementations
- `CSG_object_node`: Tree node representing CSG operations

### 2. Ray Marching Engine (`ray_marching.py`)
Implements the ray marching algorithm for rendering CSG objects.

### 3. Rendering Pipeline (`rendering.py`)
Handles the complete rendering process with lighting and multiprocessing.

### 4. User Interface (`main.py`)
Tkinter-based GUI with comprehensive object manipulation tools.

### 5. Input System (`input_dialogues.py`)
Modal dialogs for user input with validation.

### 6. Transformation System (`rotation.py`)
3D rotation matrices and transformations.

## Module Reference

### csg.py

#### Primitive Class Hierarchy

```python
class Primitive:
    """Base class for all geometric primitives."""
    
    translation: np.array      # 3D translation vector
    rotation: np.array         # 3x3 rotation matrix (inverse)
    bounding_sphere_radius: float  # For ray culling
    
    def reverse_transform(self, p: np.array) -> np.array:
        """Transform world coordinates to local object space."""
        
    def sdf(self, p: np.array) -> float:
        """Signed Distance Function - must be implemented by subclasses."""
```

**Implementation Notes:**
- All primitives are initially centered at origin
- Transformations are stored as cumulative operations
- SDF returns negative values inside objects, positive outside

#### CSG Operations

```python
class CSG_object_node:
    """Node in CSG tree representing primitives or operations."""
    
    primitive: Primitive       # Leaf node data
    operator: str             # "union", "intersection", "difference"
    left: CSG_object_node     # Left child
    right: CSG_object_node    # Right child
    center: np.array          # Center of rotation
```

**Tree Structure:**
- Leaf nodes contain primitive objects
- Internal nodes contain boolean operations
- Tree traversal computes final SDF values

### ray_marching.py

#### core Ray Marching Algorithm

```python
def cast_ray(objects, starting_point, direction_vector, 
            iteration_limit=100, precision=0.001, clipping_distance=100):
    """
    Ray marching implementation with adaptive step size.
    
    Returns:
        dict: {"hit": bool, "distance": float, "point": np.array}
    """
```

**Algorithm Details:**
1. Start at ray origin
2. Query scene SDF at current position
3. Step forward by SDF distance (sphere tracing)
4. Repeat until hit (distance < precision) or miss (distance > clipping)

**Optimization Techniques:**
- Bounding sphere intersection tests
- Early ray termination

### rendering.py

#### Rendering Pipeline

```python
def render_scene(canvas, all_objects, camera, light_sources):
    """
    Complete rendering pipeline with multiprocessing.
    
    Pipeline:
    1. Generate rays for each pixel
    2. Ray marching for intersection
    3. Normal calculation using central differences
    4. Lighting calculation (ambient + diffuse)
    5. Color composition and display
    """
```

**Lighting Model:**
- **Ambient**: Constant base illumination (0.1)
- **Diffuse**: Lambert's cosine law for surface shading
- **Multi-light**: Additive color blending from multiple sources

**Performance Features:**
- Multiprocessing pool for parallel pixel rendering
- Bounding sphere culling for ray optimization
- Efficient normal calculation with central differences

### main.py

#### Application Architecture

```python
class App:
    """Main application controller."""
    
    objects: dict              # Scene objects {name: CSG_object_node}
    camera: camera            # Camera state
    light_sources: dict       # Light sources {id: Light_source}
    log: Log                  # Action logging system
```

**UI Organization:**
- **Panel 1**: Object creation (primitives)
- **Panel 2**: Boolean operations 
- **Panel 3**: Transformations
- **Panel 4**: Camera and lighting
- **Panel 5**: Action log

## Algorithms

### Tree Traversal for SDF

```python
def sdf(self, p: np.array) -> float:
    if self.is_leaf():
        return self.primitive.sdf(p)
    else:
        left_dist = self.left.sdf(p)
        right_dist = self.right.sdf(p)
        
        if self.operator == 'union':
            return min(left_dist, right_dist)
        elif self.operator == 'intersection':
            return max(left_dist, right_dist)
        elif self.operator == 'difference':
            return max(left_dist, -right_dist)
```

We traverse the CSG tree recursively - inorder, combining SDF values based on the operation at each node.

**Union**: The minimum distance from either child, if one is negative, the result is negative - thus the point is inside. Also if both are positive, the result is the distance to the closest surface.

**Intersection**: The maximum distance from either child, if both are negative, the result is negative - thus the point is inside both. If one is positive, the result is positive - thus the point is outside at least one.

**Difference**: The maximum of the left distance and the negation of the right distance. This effectively subtracts the right shape from the left. 
    - If the point is inside the left shape and outside the right, the result is negative (inside).
    - If it's outside the left or inside the right, the result is positive (outside).
    - If it's inside both, the result is positive (outside).





### Signed Distance Functions

>[!Note]
>A great source of information for this project is Inigo Quilez's website. The SDFs implemented here are based on his work: https://iquilezles.org/articles/ distfunctions/. He also included explanations and visualizations of the SDFs.

**Box SDF:**
```python
def sdf(self, p: np.array):
    p = self.reverse_transform(p)
    p = np.abs(p)  # Use symmetry
    q = p - (self.side_lengths / 2)
    # Distance to box surface
    return np.linalg.norm(np.maximum(q, 0)) + min(0, max(q[0], q[1], q[2]))
```
The box SDF uses symmetry by taking the absolute value of the point coordinates, simplifying distance calculations. 
then we can think about the calculations of the SDF this way:

1. first we shift the point so that the upper left corner of the box coencides with the origin
```python
    q = p - (self.side_lengths / 2)
```
2. Then we can distinguish 2 situations:
    - At least one coordinate is positive: that means this term "min(0, max(q[0], q[1], q[2]))"  is 0, and the other part calculates the distance from the nearest face, edge
    - All coordinates are negative then this "np.linalg.norm(np.maximum(q, 0))" is 0 and the other part calculates the closest face

**Sphere SDF:**
```python
def sdf(self, p: np.array):
    p = self.reverse_transform(p)
    return np.linalg.norm(p) - self.radius
```

The sphere SDF is straightforward, calculating the distance from the point to the sphere's center and subtracting the radius.


**Cylinder SDF:**
```python
def sdf(self, p: np.array):
    p = self.reverse_transform(p)
    p = np.abs(p)
    d = np.array([np.linalg.norm(p[:2]) - self.r, p[2] - self.h / 2])
    return np.minimum(np.maximum(d[0], d[1]), 0) + np.linalg.norm(np.maximum(d, 0))

```

The cylinder SDF uses symmetry by taking the absolute value of the point coordinates, simplifying distance calculations. 
then we can think about the calculations of the SDF this way:
Two important signed distances are calculated:
1. distance in the xy-plane from the point to the cylinder's side surface (d[0])
2 . distance along the z-axis from the point to the cylinder's top or bottom face (d[1])

Then we can distinguish 2 situations:
- At least one of these distances is positive: the point is outside the cylinder. The SDF combines these distances to calculate the shortest distance to the cylinder's surface.

- Both distances are negative: the point is inside the cylinder. The SDF returns the maximum of these distances, which since negative will be the closest distance to the cylinder's surface (negative value).

### Ray Marching

```python 
def cast_ray(objects, starting_point, direction_vector, 
            iteration_limit=100, precision=0.001, clipping_distance=100):
    p = starting_point
    dist = 0
    for _ in range(iteration_limit):
        p = starting_point + dist * direction_vector

        d = scene_sdf(objects,p)

        if d < 0:
            # the ray is inside of an object
            return {"hit":False}
        
        if d < precision:
            return {"hit":True,"distance" :dist,"point": p}
        
        dist += d

        if dist > clipping_distance:
            #the the ray is too far so we say it did not hit
            return {"hit":False}

    #the ray did not hit anythig after the set about of iterations
    return {"hit":False}
```

The ray marching algorithm works by iteratively stepping along the ray in increments determined by the SDF value at the current position. This is known as sphere tracing.

### Normal Calculation

Using central differences for numerical gradient:

```python
def get_normal(objects, point, epsilon=0.001):
    dx, dy, dz = [epsilon, 0, 0], [0, epsilon, 0], [0, 0, epsilon]
    
    normal = np.array([
        scene_sdf(objects, point + dx) - scene_sdf(objects, point - dx),
        scene_sdf(objects, point + dy) - scene_sdf(objects, point - dy),
        scene_sdf(objects, point + dz) - scene_sdf(objects, point - dz),
    ])
    return normal / np.linalg.norm(normal)
```

### Bounding Sphere Optimization

```python
def bounding_sphere_intersection(self, ray_origin, ray_direction) -> bool:
    if self.is_leaf():
        # Distance from ray to sphere center
        ray_to_center = ray_origin - self.primitive.translation
        distance = np.sqrt(np.dot(ray_to_center, ray_to_center) - 
                          np.dot(ray_to_center, ray_direction)**2)
        return distance < self.primitive.bounding_sphere_radius
    else:
        # Recursive check for composite objects
        return (self.left.bounding_sphere_intersection(ray_origin, ray_direction) or
                self.right.bounding_sphere_intersection(ray_origin, ray_direction))
```
First we shift the sphere center by subtracting the translation vector from the ray origin. 
Then we calculate the shortest distance from the ray to the sphere center using vector projection.

### Lighting Calculation
```python
def light_intensity(point, normal_vector, light_source):
    #ambient - even if objects are far away we can still see them 
    ambient_lighting = 0.1

    #diffuse - depends on the angle between the light source and the normal vector
    light_direction = light_source - point
    light_direction /= np.linalg.norm(light_direction)
    
    diffuse_light = max(np.dot(normal_vector,light_direction),0)

    return min(ambient_lighting + diffuse_light,1)   
```

Calculates ambient and diffuse lighting at a point based on the normal vector and light source position.

---

*This documentation covers the core architecture and implementation details. For user-facing documentation, see the [User Guide](user-guide.md).*