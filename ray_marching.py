def scene_sdf(objects,p):
    if len(objects) == 0:
        return 1000
    else:
        #return the maximum distance the ray can march without hitting an object
        return min(map(lambda object: object.sdf(p),objects)) 



def raymarching(starting_point,direction_vector, iteration_limit= 100,precision = 0.001,clipping_distance=100):
    """This funtion marches a ray from the viewpoint and return the point of intersection with an object or None
       Starting point: origin of the ray -> pixel on the projective plane?
       direction vector: normalised vector that shows the direction of the ray
       objects: list of all the CSG objects -> maybe just the list of nearby objects
    """
    #think about objects within objects how should it work?
    p = starting_point
    dist = 0
    for _ in range(iteration_limit):
        # TODO inside of the pbject 
        p = starting_point + dist * direction_vector

        d = scene_sdf(p)

        if d < 0:
            return "inside of object"
        
        if d < precision:
            return {"hit":True,"distance" :dist,"point": p}
        
        dist += d

        if dist > clipping_distance:
            #the the ray is too far so we say it did not hit
            return {"hit":False}

    #the ray did not hit anythig after the set about of iterations
    return {"hit":False}
    


