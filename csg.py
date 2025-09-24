import numpy as np

class Primitive: 
    """
    Super class for all primitives outlines the basic structure and methods that all primitives should have.
    All primitives are centered at the origin and can be transformed using translation and rotation.
    

    attributes:
        translation: np.array of shape (3,) representing the translation of the object in 3D space from the origin
        rotation: np.array of shape (3,3) representing the inverse rotation matrix of the object(representing the cumulative rotation of the object)
        bounding_sphere_radius: float representing the radius of the bounding sphere of the object - used for quick rejection of rays that are too far from the object

    methods:
        sdf(p): method that takes a point p in 3D space and returns the signed distance from the point to the surface of the object
        reverse_transform(p): method that applies the inverse transformation (translation and rotation) to a given point p - used to calculate the sdf in the object 

    """
    def __init__(self):
        #We create variables that store the transformations performed on the object
        #this allows us to consider the signed distance function(SDF) 
        self.translation = np.zeros(3)
        self.rotation = np.eye(3)

        #the bounding sphere radius is used for quick rejection of rays that are too far from the object
        self.bounding_sphere_radius = 0 # this will be set in the child classes
    
    def reverse_transform(self,p:np.array):
        # this method applies the inverse transformation to a given p
        p = p - self.translation
        p = p @ self.rotation
        return p

class Box(Primitive):
    """
    Class representing a box primitive. Inherits from Primitive class.
    
    Unique attributes:
        side_lengths: np.array of shape (3,) representing the lengths of the sides of the box along the x, y, and z axes
        """

    def __init__(self,length=1,width=1,height=1):
        super().__init__()
        self.side_lengths = np.array([length,width,height])

        self.bounding_sphere_radius = np.linalg.norm(self.side_lengths) / 2

    def sdf(self,p:np.array):
        p = self.reverse_transform(p)
        #since the box has axial symmetry we can consider the p where all coordinates are positive
        p = np.abs(p)
        q = p - (self.side_lengths / 2)
        distance = np.linalg.norm(np.maximum(q,0)) + min(0,max(q[0],q[1],q[2]))
        return distance
        

class Sphere(Primitive):
    """
    Class representing a sphere primitive. Inherits from Primitive class.
    
    Unique attributes:
        radius: float representing the radius of the sphere
    """

    def __init__(self,radius=1):
        super().__init__()
        self.r = radius

        self.bounding_sphere_radius = radius
    
    def sdf(self,p:np.array):
        p = self.reverse_transform(p)
        distance = np.linalg.norm(p) - self.r
        return distance



class Cylinder(Primitive):
    """
    Class representing a cylinder primitive. Inherits from Primitive class.

    Unique attributes:
        radius: float representing the radius of the cylinder
        height: float representing the height of the cylinder
    """
    def __init__(self,radius=1,height=1):
        super().__init__()
        self.r = radius
        self.h = height

        self.bounding_sphere_radius = np.linalg.norm(np.array([radius,height/2]))

    
    def sdf(self,p:np.array):
        p = self.reverse_transform(p)
        p = np.abs(p)

        d = np.array([np.linalg.norm(p[:2]) - self.r, p[2] - self.h / 2])
        distance = np.minimum(np.maximum(d[0], d[1]), 0) + np.linalg.norm(np.maximum(d, 0))
        return distance


class CSG_object_node:
    """
    Class representing a node in a CSG tree. Each node can be either a primitive or an operation (union, intersection, difference) combining two child nodes.
    The CSG tree is used to represent complex 3D objects by combining simpler primitives using boolean operations.
    The leaves of the tree are primitives, and the internal nodes are operations.

    attributes:
        primitive: instance of a Primitive subclass (Box, Sphere, Cylinder) if the node is a leaf, otherwise None
        operator: string representing the operation ("union", "intersection", "difference") if the node is not a leaf, otherwise None
        left: left child node (CSG_object_node) if the node is not a leaf, otherwise None
        right: right child node (CSG_object_node) if the node is not a leaf, otherwise None

        center: np.array of shape (3,) representing the center of rotation of the object and all its children - used for rotation transformations
            - for leaf nodes (primitives), the center is at the origin [0,0,0]
            - for union and intersection operations, the center is the midpoint between the centers of the two child nodes
            - for difference operations, the center is the center of the left child node (the object that remains after the difference)

    """


    def __init__(self,primitive=None,operator=None,left=None,right = None):
        self.primitive = primitive 
        self.operator = operator
        self.left = left
        self.right = right

        if primitive != None:
            self.center = np.array([0.0,0.0,0.0])
        elif operator == "intersection" or operator == "union": 
            #for these two operations the center is the midpoint between the centers of the two objects
            self.center = (self.left.center + self.right.center)/ 2
        elif operator == "difference":
            # for difference the center is the center of the object that remains so the 
            self.center = self.left.center
    
    def is_leaf(self):
        """
        True if the node is a leaf (i.e., it contains a primitive), False otherwise.
        """
        #this funtion determines whether the node is a leaf becuase only the lease
        return self.primitive is None
    
    def bounding_sphere_intersection(self,ray_origin,ray_direction):
        """
        calcualtes whether a ray and bounding sphere intersect.
        ray_origin a point on the ray
        ray_direction: normalized direction vector of the ray

        returns: True if the ray intersects the bounding sphere, False otherwise
        """
        
        if self.is_leaf():
            ray_origin -= self.primitive.translation()
            distance_from_center = np.sqrt(np.dot(ray_origin,ray_origin)-np.dot(ray_origin,ray_direction)**2)

            if distance_from_center < self.primitive.bounding_sphere_radius:
                return True
            else:
                return False
        
        else:
            l = self.left.bounding_sphere_intersection(ray_origin,ray_direction)
            # if l is true then it returns true if not it returns
            return l or self.right.bounding_sphere_intersection(ray_origin,ray_direction)

    
   
    def sdf(self,p:np.array) -> np.float32:
        """
        calculates the signed distance from point p to the surface of the CSG object represented by the tree rooted at this node.

        returns: signed distance as a float
        """

        if self.is_leaf():
            return self.primitive.sdf(p)
        else:
            left_dist = self.left.sdf(p)
            right_dist = self.right.sdf(p)
            if self.operator == 'union': 
                # this operation is not perfect while it determines the exterior distance correctly the interior distance is not always correct
                # for now we will use it as is
                return min(left_dist, right_dist) 
            elif self.operator == 'intersection':
                return max(left_dist, right_dist)
            elif self.operator == 'difference':
                return max(left_dist, -right_dist)
            else:
                raise ValueError("Unknown operator")
            

    def translate(self,v:np.array ):
        """
        Translates the CSG object and all its children by vector v.
        """
        if self.is_leaf():
            self.primitive.translation += v
        else:
            self.left.translate(v)
            self.right.translate(v)
        self.center += v

    def rotate(self,rot_matrix,inverse_rot_matrix):
        """
        Rotates the CSG object and all its children using the given rotation matrix.

        rot_matrix: np.array of shape (3,3) representing the rotation 
        inverse_rot_matrix: np.array of shape (3,3) representing the inverse rotation 
        """


        if self.is_leaf():
            self.primitive.rotation = self.primitive.rotation @ inverse_rot_matrix
        else:
            self.left.rotate(rot_matrix,inverse_rot_matrix)
            center_diff =self.center - self.left.center
            self.left.translate(center_diff)
            self.left.translate(-center_diff@rot_matrix)

            center_diff = self.center - self.right.center 
            self.right.rotate(rot_matrix,inverse_rot_matrix)
            self.right.translate(center_diff)
            self.right.translate(-center_diff@rot_matrix)


# We define funtions whose input is are two CSG nodes and output is a new CSG node with the appropriate operator

def CSG_union(obj1:CSG_object_node,obj2:CSG_object_node):
    """ 
    Creates a new CSG_object_node representing the union of two CSG objects.
    """
    return CSG_object_node(operator="union",left = obj1,right=obj2)

def CSG_intersection(obj1:CSG_object_node,obj2:CSG_object_node):
    """
    Creates a new CSG_object_node representing the intersection of two CSG objects.
    """
    return CSG_object_node(operator="intersection",left = obj1,right=obj2)

def CSG_difference(obj1:CSG_object_node,obj2:CSG_object_node):
    """
    Creates a new CSG_object_node representing the difference of two CSG objects (obj1 - obj2).
    """
    return CSG_object_node(operator="difference",left = obj1,right=obj2)






 




