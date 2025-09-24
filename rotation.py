import numpy as np

def rotation_matrix(angle:float,rot_plane:str,inverse=False):
    """
    This function returns the rotation matrix of a rotation by the given angle in the given rotation plane
    
    rot_plane: "xy","yz","xz"
    Angle: the angle of desired rotation in radians
    Inverse: set to True if we want the inverse rotation matrix
    """
    if inverse:
        angle = -angle # that is just the rotation in the opposite direction

    if rot_plane == "xy":
        rotation_matrix = np.array([[np.cos(angle),-np.sin(angle),0],
                                    [np.sin(angle),np.cos(angle),0],
                                    [0,0,1]])  
    elif rot_plane == "yz":
        rotation_matrix = np.array([[1,0,0],
                                    [0,np.cos(angle),-np.sin(angle)],
                                    [0,np.sin(angle),np.cos(angle)]])
    elif rot_plane == "xz":
        rotation_matrix = np.array([[np.cos(angle),0,-np.sin(angle)],
                                    [0,1,0],
                                    [np.sin(angle),0,np.cos(angle)]])

    return rotation_matrix


