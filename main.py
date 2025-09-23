import csg
import rotation
from input_dialogues import *
import rendering


import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import time

def save_image(imgtk):
    img = ImageTk.getimage( imgtk )
    img.save("rendered_image.bmp")

class Light_source:
    #light source class to store the position and color of the light source
    def __init__(self,position,color):
        self.position = position
        self.color = color

class camera:
    #camera class to store the position and rotation of the camera
    def __init__(self,position=np.array([0,0,0])):
        self.position = position
        self.rotation = np.eye(3)
    def rotate(self,rotation_matrix):
        self.rotation = rotation_matrix @ self.rotation
    def translate(self,translation_vector):
        self.position = self.position + translation_vector

class Log():
    def __init__(self,root):
        log = scrolledtext.ScrolledText(root,width=50,height=20)
        log.pack()
        self.log = log
    def write(self,message):
        self.log.insert(tk.END,message + "\n")
        self.log.see(tk.END)
    def clear(self):
        self.log.delete(1.0,tk.END)
      
class App:

    def __init__(self,camera_pos = [0,0,-5],light_pos = [10,-10,10],screen_width=300,screen_height=300):
        
        self.objects = dict()
        self.camera = camera(np.array(camera_pos))
        
        self.width = screen_width
        self.height = screen_height

        window = tk.Tk()
        window.title("CSG")

        self.window = window

        #used for assigning ids to objects
        self.object_id = 0 
        self.light_id = 0

        self.light_sources = dict()
        self.add_light(position=light_pos)
    #function to render the scene
    def render(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.window,width=self.width,height=self.height,bg="black")
        canvas.pack()

        self.canvas = canvas
        #render the scene and print the time taken
        start_time = time.time()
        self.log.write("Rendering scene...")
        rendering.render_scene(self.canvas,self.objects,self.camera,self.light_sources)
        end_time = time.time()
        self.log.write(f"Scene rendered in {end_time - start_time:.2f} seconds")

        print("Rendering complete")
        self.window.mainloop()

    #fuctions for adding, removing and manipulating objects
    def add_box(self):
        d = box_dialog()
        d = d.result
        if d == None:
            return
        
        #create the box and add it to the objects dictionary
        self.objects[f"box{self.object_id}"] = csg.CSG_object_node(csg.Box(d[0],d[1],d[2]))

        #wrtite to log
        self.log.write(f"Added box{self.object_id} with dimensions {d[0]}, {d[1]}, {d[2]}")

        #increment the object id
        self.object_id += 1
    
    def add_sphere(self):

        d = shpere_dialog()
        d = d.result
        if d == None:
            return


        self.objects[f"sphere{self.object_id}"] = csg.CSG_object_node(csg.Sphere(d[0]))
        #wrtite to log
        self.log.write(f"Added sphere{self.object_id} with radius {d[0]}")
         #increment the object id
        self.object_id += 1
    
    def add_cylinder(self):

        d = cylinder_dialog()
        d = d.result
        if d == None:
            return


        self.objects[f"cylinder{self.object_id}"] = csg.CSG_object_node(csg.Cylinder(d[0],d[1]))
        self.log.write(f"Added cylinder{self.object_id} with radius {d[0]} and height {d[1]}")
        self.object_id += 1   

    def remove_object(self,object_name=None):
        
        if object_name == None:
            object_name = get_object(title="Remove object",objects=self.objects)

        if object_name in self.objects:
            self.log.write(f"Removed object {object_name}")
            del self.objects[object_name]
        else:
            print(f"Object {object_name} not found")

            
    def translate_object(self):
        object_name,translation_vector = get_translation(objects=self.objects)

        if object_name in self.objects:
            self.objects[object_name].translate(np.array(translation_vector))
            self.log.write(f"Translated object {object_name} by vector {translation_vector}")
        else:
            print(f"Object {object_name} not found")

    def rotate_object(self):
        object_name,angle,rotation_plane = get_rotation(objects=self.objects)

        angle = np.radians(angle)

        if object_name in self.objects:
            rot_mat = rotation.rotation_matrix(angle,rotation_plane,inverse=False)
            inverse_rot_mat = rotation.rotation_matrix(angle,rotation_plane,inverse=True)


            self.objects[object_name].rotate(rot_mat,inverse_rot_mat)
            self.log.write(f"Rotated object {object_name} by {np.degrees(angle)} degrees in the {rotation_plane} plane")

        else:
            print(f"Object {object_name} not found")

    def combine_objects(self,operation):
        """
        Takes an operation (union, difference, intersection) and combines them into a new object and removes the original objects.
        The new object is named "combined-{operation}{id}"
        """
        result = get_2_objects(title=operation,objects=self.objects)
        
        if result == None:
            return
        
        obj_name1,obj_name2 = result[0],result[1]

        if obj_name1 in self.objects and obj_name2 in self.objects:
            if operation == "union":
                self.objects[f"combined-union{self.object_id}"] = csg.CSG_union(self.objects[obj_name1],self.objects[obj_name2])
            elif operation == "difference":
                self.objects[f"combined-difference{self.object_id}"] = csg.CSG_difference(self.objects[obj_name1],self.objects[obj_name2])
            elif operation == "intersection":
                self.objects[f"combined-intersection{self.object_id}"] = csg.CSG_intersection(self.objects[obj_name1],self.objects[obj_name2])

            self.log.write(f"Combined objects {obj_name1} and {obj_name2} using {operation} to create combined-{operation}{self.object_id}")
            self.object_id += 1

            #remove the original objects
            del self.objects[obj_name1]
            del self.objects[obj_name2]
        else:
            print(f"One or both objects not found: {obj_name1}, {obj_name2}")

    #function to manipulate the camera
    def move_camera(self,translation_vector):
        self.camera.translate(np.array(translation_vector))

        self.log.write(f"Moved camera by vector {translation_vector}")
    
    def rotate_camera(self,angle,rotation_plane:str):
        angle = np.radians(angle)
        self.camera.rotate(rotation.rotation_matrix(angle,rotation_plane))

        self.log.write(f"Rotated camera by {np.degrees(angle)} degrees in the {rotation_plane} plane")


    #function to manipulate the light sources
    def add_light(self,position=None,color="white"):
        if position is None:
            position,color = get_light_source()
            self.log.write(f"Added {color} light source at position {position}")
            

        self.light_sources[f"{color}{self.light_id}"] = Light_source(np.array(position),color)
        
        self.light_id += 1

    def remove_light(self,light_id):
        if light_id in self.light_sources:
            del self.light_sources[light_id]
            self.log.write(f"Removed light source {light_id}")
        else:
            print(f"Light source {light_id} not found")

    def change_resolution(self):
        width,height = get_resolution()
        if width == None or height == None:
            return
        self.width = width
        self.height = height
        self.log.write(f"Changed resolution to {width}x{height}")

    
    #UI
    def setup_ui(self):
        root = tk.Tk()
        root.title("CSG Application")

        main_container = ttk.PanedWindow(root,orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)

        #creating objects
        panel1 = ttk.Frame(main_container)
        panel1.grid(row=0,column=0, padx=5)

        create_container = ttk.LabelFrame(panel1,text="Create objects",padding=10)
        create_container.pack()

        primitives = [
        ("Sphere", self.add_sphere),
        ("box", self.add_box),
        ("cylinder",self.add_cylinder)
        ]
    
        for i, (name, command) in enumerate(primitives):
            btn = ttk.Button(create_container, text=name, command=command)
            btn.grid(row=i,column=1) 

        


        #combining objects
        panel2 = ttk.Frame(main_container)
        panel2.grid(row=0,column=1, padx=5)
        combine_container = ttk.LabelFrame(panel2,text="Object operations",padding=10)
        combine_container.pack()

        operations = [
        ("Union", lambda : self.combine_objects("union")),
        ("intersection", lambda: self.combine_objects("intersection")),
        ("difference",lambda: self.combine_objects("difference")),
        ("Remove object",self.remove_object)
        ]

        for i, (name, command) in enumerate(operations):
            btn = ttk.Button(combine_container, text=name, command=command)
            btn.grid(row=i,column=1) 

        
        #Object transformations
        panel3 = ttk.Frame(main_container)
        panel3.grid(row=0,column=2, padx=5)
        transform_container = ttk.LabelFrame(panel3,text="Transform objects",padding=10)
        transform_container.pack()

        transformations = [
        ("Translate", self.translate_object),
        ("Rotate", self.rotate_object)
        ]
        for i, (name, command) in enumerate(transformations):
            btn = ttk.Button(transform_container, text=name, command=command)
            btn.grid(row=i,column=1)


        #render button
        render_scene_button = ttk.Button(main_container,command=self.render,text="render scene")
        render_scene_button.grid(row=1,column=0,columnspan=2,padx=10,pady=10)

        #save image button
        save_image_button = ttk.Button(main_container,command=lambda: save_image(self.canvas.image),text="Save image")
        save_image_button.grid(row=1,column=2,padx=10,pady=10)


        # Camera controls and lighting
        panel4 = ttk.Frame(main_container)
        panel4.grid(row=0,column=3, padx=5)
        camera_container = ttk.LabelFrame(panel4,text="Camera and lighting",padding=10)
        camera_container.pack()
        camera_operations = [
        ("Move camera", lambda: self.move_camera(get_translation_vector())),
        ("Rotate camera", lambda: self.rotate_camera(get_camera_rotation())),
        ("Add light", self.add_light),
        ("Remove light", lambda: self.remove_light(get_light_id(self.light_sources)))
        ]
        for i, (name, command) in enumerate(camera_operations):
            btn = ttk.Button(camera_container, text=name, command=command)
            btn.grid(row=i,column=1)
        
        #Log of all the actions that were performed
        panel5 = ttk.Frame(main_container)
        panel5.grid(row=0,column=4, padx=5,rowspan=2)
        log_container = ttk.LabelFrame(panel5,text="Action log",padding=10)
        log_container.grid(row=0,column=3,padx=5,pady=5)
        
        #change of resolution
        #button to change resolution  
        resolution_button = ttk.Button(main_container, text="Change resolution", command=lambda: self.change_resolution())
        resolution_button.grid(row=1,column=3,padx=5,pady=5)



        self.log = Log(log_container)

        self.log.write("Camera position: " + str(self.camera.position))
        self.log.write("Looking direction: [0,0,1]")
        self.log.write("Added light source white0 at position " + str(self.light_sources["white0"].position))

        root.mainloop()
    
if __name__ == "__main__":
    #resolution of the image
    WIDTH = 600
    HEIGHT = 400
    CAMERA_POSITION = np.array([0,0,-6])
    LIGHT_POSITION = np.array([10,10,-10])

    app = App(camera_pos=CAMERA_POSITION,light_pos=LIGHT_POSITION,screen_width=WIDTH,screen_height=HEIGHT)
    
    app.setup_ui()



