# CSG Editor - Programmer Documentation

## Table of Contents

2. [Core Components](#core-components)
3. [Module Reference](#module-reference)
4. [Data Structures](#data-structures)
5. [Algorithms](#algorithms)
6. [Extension Points](#extension-points)
7. [Performance Considerations](#performance-considerations)
8. [Development Guidelines](#development-guidelines)


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

#### Core Algorithm

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
- Adaptive precision thresholds

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

**State Management:**
- Centralized object registry with unique IDs
- Immutable transformations (objects are replaced, not modified)
- Comprehensive action logging for debugging

**UI Organization:**
- **Panel 1**: Object creation (primitives)
- **Panel 2**: Boolean operations 
- **Panel 3**: Transformations
- **Panel 4**: Camera and lighting
- **Panel 5**: Action log

## Data Structures

### Coordinate Systems

**World Space**: Global 3D coordinate system
- Camera and lights positioned in world space
- Final object positions after all transformations

**Object Space**: Local coordinate system for each primitive
- All primitives defined at origin initially
- Transformations convert world→object space for SDF evaluation

**Screen Space**: 2D projection for rendering
- Normalized device coordinates [-1,1]
- Field of view and aspect ratio corrections

### Transformation Chain

```python
# Forward transform: Object → World
world_point = object_point @ rotation_matrix + translation

# Reverse transform: World → Object (used in SDF)
object_point = (world_point - translation) @ inverse_rotation
```

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

## Algorithms

### Signed Distance Functions

**Box SDF:**
```python
def sdf(self, p: np.array):
    p = self.reverse_transform(p)
    p = np.abs(p)  # Use symmetry
    q = p - (self.side_lengths / 2)
    # Distance to box surface
    return np.linalg.norm(np.maximum(q, 0)) + min(0, max(q[0], q[1], q[2]))
```

**Sphere SDF:**
```python
def sdf(self, p: np.array):
    p = self.reverse_transform(p)
    return np.linalg.norm(p) - self.radius
```

**Cylinder SDF:**
```python
def sdf(self, p: np.array):
    p = self.reverse_transform(p)
    p = np.abs(p)
    d = np.array([np.linalg.norm(p[:2]) - self.r, p[2] - self.h / 2])
    return np.minimum(np.maximum(d[0], d[1]), 0) + np.linalg.norm(np.maximum(d, 0))
```

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

## Extension Points

### Adding New Primitives

1. **Create primitive class**:
```python
class Torus(Primitive):
    def __init__(self, major_radius=2, minor_radius=1):
        super().__init__()
        self.R = major_radius
        self.r = minor_radius
        self.bounding_sphere_radius = major_radius + minor_radius
    
    def sdf(self, p: np.array):
        p = self.reverse_transform(p)
        q = np.array([np.linalg.norm(p[:2]) - self.R, p[2]])
        return np.linalg.norm(q) - self.r
```

2. **Add UI dialog**:
```python
class torus_dialog(simpledialog.Dialog):
    # Implementation similar to existing dialogs
```

3. **Register in main application**:
```python
def add_torus(self):
    d = torus_dialog()
    if d.result:
        major_r, minor_r = d.result
        self.objects[f"torus{self.object_id}"] = csg.CSG_object_node(Torus(major_r, minor_r))
        self.object_id += 1
```

### Adding New Operations

```python
def CSG_smooth_union(obj1: CSG_object_node, obj2: CSG_object_node, k=0.1):
    """Smooth union operation for organic blending."""
    return CSG_object_node(operator="smooth_union", left=obj1, right=obj2, blend_factor=k)

# Add to CSG_object_node.sdf():
elif self.operator == 'smooth_union':
    h = max(0, min(1, (0.5 + (right_dist - left_dist) / (2 * self.blend_factor))))
    return lerp(right_dist, left_dist, h) - self.blend_factor * h * (1 - h)
```

### Custom Shaders

```python
def custom_lighting(normal_vector, point, light_source, material_properties):
    """Extended lighting with material properties."""
    # Implement Phong, Blinn-Phong, or PBR lighting
    ambient = material_properties.ambient
    diffuse = material_properties.diffuse * lambertian_factor
    specular = material_properties.specular * specular_factor
    return ambient + diffuse + specular
```

## Performance Considerations

### Memory Usage

**Object Storage:**
- Objects stored in dictionaries with string keys
- NumPy arrays for efficient mathematical operations
- Tree structures minimize memory overhead for complex scenes

**Ray Marching Optimization:**
- Bounding sphere tests eliminate ~60-80% of unnecessary SDF calls
- Adaptive step sizes reduce iteration counts
- Early termination for rays that miss scene bounds

### Computational Complexity

**SDF Evaluation**: O(n) where n = number of primitives in scene
**Ray Marching**: O(m) where m = average iterations per ray (typically 10-50)
**Rendering**: O(w × h × n × m) for full scene

**Bottlenecks:**
1. **SDF computation** - Most expensive per-pixel operation
2. **Normal calculation** - Requires 6 additional SDF evaluations per hit
3. **Multiprocessing overhead** - Process creation and data serialization

### Optimization Strategies

**Spatial Optimization:**
```python
# Current: Bounding spheres
# Potential: Octree spatial partitioning, BVH (Bounding Volume Hierarchy)
```

**Algorithmic Improvements:**
```python
# Current: Central differences for normals
# Potential: Analytical normals where possible, tetrahedron technique
```

**Rendering Optimizations:**
```python
# Current: Brute force all pixels
# Potential: Adaptive sampling, progressive rendering, LOD systems
```

## Development Guidelines

### Code Style

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `CSG_object_node`)
- Functions: `snake_case` (e.g., `cast_ray`)
- Constants: `UPPER_CASE` (e.g., `ITERATION_LIMIT`)
- Private methods: `_snake_case` prefix

**Type Hints:**
```python
def sdf(self, p: np.array) -> float:
    """Always specify parameter and return types."""
    
def cast_ray(objects: list[CSG_object_node], 
             starting_point: np.array, 
             direction_vector: np.array) -> dict:
    """Use descriptive parameter names and return type hints."""
```

### Error Handling

**Validation Patterns:**
```python
def validate_primitive_parameters(self, **params):
    """Validate geometric parameters before object creation."""
    for name, value in params.items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"Parameter {name} must be positive number")
```

**Graceful Degradation:**
```python
def render_with_fallback(self):
    """Attempt multiprocessing, fall back to single-threaded."""
    try:
        return self.render_multiprocess()
    except Exception as e:
        self.log.write(f"Multiprocessing failed: {e}, using single thread")
        return self.render_single_thread()
```

### Testing Strategies

**Unit Tests:**
```python
def test_sphere_sdf():
    """Test sphere SDF for known values."""
    sphere = Sphere(radius=1.0)
    
    # Test surface points
    assert abs(sphere.sdf(np.array([1, 0, 0]))) < 1e-6
    assert abs(sphere.sdf(np.array([0, 1, 0]))) < 1e-6
    
    # Test interior/exterior
    assert sphere.sdf(np.array([0, 0, 0])) < 0  # Inside
    assert sphere.sdf(np.array([2, 0, 0])) > 0  # Outside
```

**Integration Tests:**
```python
def test_csg_operations():
    """Test CSG boolean operations."""
    box = CSG_object_node(Box(2, 2, 2))
    sphere = CSG_object_node(Sphere(1.5))
    
    union = CSG_union(box, sphere)
    intersection = CSG_intersection(box, sphere)
    difference = CSG_difference(box, sphere)
    
    # Test SDF values at known points
    test_point = np.array([0.5, 0.5, 0.5])
    assert union.sdf(test_point) < 0
    assert intersection.sdf(test_point) < 0
```

### Debugging Tools

**Logging System:**
```python
class DebugLog(Log):
    """Extended logging with debug levels."""
    
    def debug(self, message):
        if DEBUG_MODE:
            self.write(f"DEBUG: {message}")
    
    def performance(self, operation, time_taken):
        self.write(f"PERF: {operation} took {time_taken:.3f}s")
```

**Visualization Helpers:**
```python
def visualize_sdf_slice(objects, y=0, resolution=100):
    """Generate 2D SDF visualization for debugging."""
    # Create heatmap of SDF values in XZ plane
```

### Future Enhancements

**Planned Features:**
- [ ] Material system with texture support
- [ ] Animation system with keyframe interpolation
- [ ] Advanced lighting (shadows, reflections)
- [ ] Export to standard 3D formats (STL, OBJ)
- [ ] GPU acceleration with compute shaders
- [ ] Procedural texture generation
- [ ] Physics simulation integration

**Architecture Improvements:**
- [ ] Plugin system for custom primitives
- [ ] Scripting interface (Python API)
- [ ] Undo/redo system with command pattern
- [ ] Scene serialization and loading
- [ ] Multi-threaded UI with background rendering

---

*This documentation covers the core architecture and implementation details. For user-facing documentation, see the [User Guide](user-guide.md).*