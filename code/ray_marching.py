import numpy as np

def scene_sdf(objects,p):
    """
    Calculate the signed distance from point p to the nearest object in the scene.
    If there are no objects in the scene, returns a large value 1000.

    p: point in space where we want to calculate the SDF
    objects: list of all the CSG objects in the scene used to calculate the SDF
    """

    if len(objects) == 0:
        return 1000
    else:
        #return the maximum distance the ray can march without hitting an object
        return min(map(lambda object: object.sdf(p),objects)) 



def cast_ray(objects,starting_point,direction_vector, iteration_limit= 100,precision = 0.001,clipping_distance=100):
    """
    Cast a ray from a starting point in a given direction using the ray marching algorithm.
    Is limited by iteration_limit(maximum number of iterations) and clipping_distance(maximum distance from the starting point).

    objects: list of all the CSG objects in the scene - used to calculate the SDF
    starting_point: the point from which the ray is cast - numpy array
    direction_vector: normalized direction vector of the ray - numpy array
    iteration_limit: maximum number of iterations to perform
    precision: minimum distance to consider a hit
    clipping_distance: maximum distance the ray can travel before we consider it a miss

    returns: dictionary with keys "hit" (boolean), "distance" (float), "point" (numpy array)
    """

    p = starting_point
    dist = 0
    for _ in range(iteration_limit):
        # TODO inside of the pbject 
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
    


