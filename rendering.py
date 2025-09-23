import tkinter as tk
import ray_marching
import numpy as np
import multiprocessing


def get_normal(objects,point,epsilon=0.001):
    #calculate the normal at a point on the surface of an object using central differences
    #the gradient of the SDF at that point should be perpendicular to the surface 
    dx = np.array([epsilon,0,0])
    dy = np.array([0,epsilon,0])
    dz = np.array([0,0,epsilon])

    #this  might be a bit too expensive but well see
    normal = np.array([
        ray_marching.scene_sdf(objects,point + dx) - ray_marching.scene_sdf(objects,point - dx),
        ray_marching.scene_sdf(objects,point + dy) - ray_marching.scene_sdf(objects,point - dy),
        ray_marching.scene_sdf(objects,point + dz) - ray_marching.scene_sdf(objects,point - dz),
    ])
    normal /= np.linalg.norm(normal)
    return normal


def light_intensity(normal_vector,point,light_source):
    #ambient - even if objects are far away we can still see them 
    ambient_lighting = 0.1

    #diffuse - depends on the angle between the light source and the normal vector
    light_direction = light_source - point
    light_direction /= np.linalg.norm(light_direction)
    
    diffuse_light = max(np.dot(normal_vector,light_direction),0)

    return min(ambient_lighting + diffuse_light,1)

def render_pixel(pos,width,height,objects,camera,light_sources):
    WIDTH = width
    HEIGHT = height
    fov = np.pi / 3  # 60 degrees field of view
    aspect_ratio = WIDTH / HEIGHT

    x,y = pos
    # Normalized device coordinates
    ndc_x = (x / WIDTH ) * 2 - 1
    ndc_y = (y / HEIGHT ) * 2 - 1

    # Screen space coordinates
    screen_x = (ndc_x) * aspect_ratio * np.tan(fov / 2)
    screen_y = (ndc_y) * np.tan(fov / 2)

    # Ray direction
    ray_direction = np.array([screen_x, screen_y,1]) @ camera.rotation
    ray_direction /= np.linalg.norm(ray_direction)  # Normalize the direction
    
    objects = [obj for obj in objects.values() if obj.bounding_sphere_intersection]

    result = ray_marching.cast_ray(objects,camera.position, ray_direction)
    
    rgb = [0,0,0]
    if result["hit"]:
        point = result["point"]
        normal_vector = get_normal(objects,point)
        for light_source in light_sources.values():
            intensity = light_intensity(normal_vector,point,light_source.position)

            if light_source.color == "white":
                rgb[0] = min(rgb[0]+ intensity,1)
                rgb[1] = min(rgb[1]+ intensity,1)
                rgb[2] = min(rgb[2]+ intensity,1)

            elif light_source.color == "red":
                rgb[0] = min(rgb[0]+ intensity,1)
            elif light_source.color == "green":
                rgb[1] = min(rgb[1]+ intensity,1)

            elif light_source.color == "blue":
                rgb[2] = min(rgb[2]+ intensity,1) 
    rgb = [*map(lambda x: int(x*255),rgb)]
    return (x,y,rgb)
def render_scene(canvas,all_objects,camera,light_sources):
    """
    Render the scene onto the given Tkinter canvas using ray marching.
    canvas: Tkinter canvas where the scene will be rendered
    objects: dictionary of CSG objects in the scene
    camera: camera object with position and rotation
    light_sources: tuple of light source positions (numpy arrays)    
    """



    WIDTH = int(canvas['width'])
    HEIGHT = int(canvas['height'])
    #camera parameters
    fov = np.pi / 3  # 60 degrees field of view
    aspect_ratio = WIDTH / HEIGHT

    image = tk.PhotoImage(width=WIDTH, height=HEIGHT)
    pixels = [[i,j] for i in range(WIDTH) for j in range(HEIGHT)]

    #
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.starmap(render_pixel, [(pos,WIDTH,HEIGHT,all_objects,camera,light_sources) for pos in pixels])
        for x,y,rgb in results:
            image.put(f"#{rgb_to_hex(rgb)}", (x, y))
    
    canvas.image = image
    canvas.create_image((WIDTH // 2, HEIGHT // 2), image=image, anchor=tk.CENTER)


    # for x in range(WIDTH):
    #     for y in range(HEIGHT):
    #         # Start time measurement
    #         #start = time.time()
    #         # Normalized device coordinates
    #         ndc_x = (x / WIDTH ) * 2 - 1
    #         ndc_y = (y / HEIGHT ) * 2 - 1

    #         # Screen space coordinates
    #         screen_x = (ndc_x) * aspect_ratio * np.tan(fov / 2)
    #         screen_y = (ndc_y) * np.tan(fov / 2)

    #         # Ray direction
    #         ray_direction = np.array([screen_x, screen_y,1]) @ camera.rotation
    #         ray_direction /= np.linalg.norm(ray_direction)  # Normalize the direction
            
    #         objects = [obj for obj in all_objects.values() if obj.bounding_sphere_intersection]

    #         result = ray_marching.cast_ray(objects,camera.position, ray_direction)
            
    #         rgb = [0,0,0]
    #         if result["hit"]:
    #             point = result["point"]
    #             normal_vector = get_normal(objects,point)
    #             for light_source in light_sources.values():
    #                 intensity = light_intensity(normal_vector,point,light_source.position)

    #                 if light_source.color == "white":
    #                     rgb[0] = min(rgb[0]+ intensity,1)
    #                     rgb[1] = min(rgb[1]+ intensity,1)
    #                     rgb[2] = min(rgb[2]+ intensity,1)

    #                 elif light_source.color == "red":
    #                     rgb[0] = min(rgb[0]+ intensity,1)
    #                 elif light_source.color == "green":
    #                     rgb[1] = min(rgb[1]+ intensity,1)

    #                 elif light_source.color == "blue":
    #                     rgb[2] = min(rgb[2]+ intensity,1) 
    #         print( rgb)
    #         rgb = [*map(lambda x: int(x*255),rgb)]
    #         image.put(f"#{rgb_to_hex(rgb)}", (x, y))



def rgb_to_hex(rgb):
    """Convert an integer to an RGB tuple."""
    return f"{hex(rgb[0])[2:]:0>2}{hex(rgb[1])[2:]:0>2}{hex(rgb[2])[2:]:0>2}"