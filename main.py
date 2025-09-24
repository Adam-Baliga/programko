import csg
import rotation
from input_dialogues import *
import rendering


import numpy as np
import tkinter as tk
from tkinter import ttk,messagebox,simpledialog,scrolledtext
from PIL import Image, ImageTk
import time

def save_image(imgtk):
    """
    Function to save the rendered image to a file. Opens a dialog to get the file name and saves the image as a PNG file.
    Checks if there is an image to save and shows an error message if not.
    The dialog chcecks if there is a file with the same name and asks the user to choose another one if so.

    imgtk: ImageTk.PhotoImage object to be saved
    
    """

    if imgtk is None:
        tk.messagebox.showerror("Error", "No image to save. Please render the scene first.")
        return
    
    name = get_file_name()
    if name is None:
        return
    img = ImageTk.getimage( imgtk )
    img.save(f"{name}.png")

class Light_source:
    """
    class to store the position and color of the light source

    Attributes:
        position: numpy array of shape (3,)
        color: string, can be "white","red","green","blue"

    """
    def __init__(self,position,color):
        self.position = position
        if color not in ["white","red","green","blue"]:
            raise ValueError("Color must be one of 'white','red','green','blue'")
        self.color = color

class camera:
    """ 
    class to store the position and rotation of the camera

    To change the position and rotation of the camera use the translate and rotate methods

    Attributes:
        position: numpy array of shape (3,) representing the position of the camera
        rotation: numpy array of shape (3,3) representing the rotation matrix

    Example:

    cam = camera(np.array([0,0,-5]))
    cam.rotate(np.array([[-1,0,0],[0,1,0],[0,0,1]])))

    """
    def __init__(self,position=np.array([0,0,0])):
        self.position = position
        self.rotation = np.eye(3)
    def rotate(self,rotation_matrix):
        """
        Rotate the camera by the given rotation matrix

        rotation_matrix: numpy array of shape (3,3)
        """
        self.rotation = rotation_matrix @ self.rotation
    def translate(self,translation_vector):
        """
        Translate the camera by the given translation vector
        translation_vector: numpy array of shape (3,)
        """
        self.position = self.position + translation_vector

class Log():
    """
    class to store the log of actions performed in the application

    includes methods to write to the log and clear the log
    root: Tkinter root window

    Example:
    log = Log(root)
    log.write("Added box1")
    log.clear()
    """

    def __init__(self,root):
        log = scrolledtext.ScrolledText(root,width=60,height=20)
        log.pack()
        self.log = log
    def write(self,message):
        self.log.insert(tk.END,message + "\n")
        self.log.see(tk.END)
    def clear(self):
        self.log.delete(1.0,tk.END)
      
class App:
    """
    class for the main application that handles the UI and interactions

    Input parameters:
    camera_pos: list of 3 floats representing the initial position of the camera
    light_pos: list of 3 floats representing the initial position of the light source
    screen_width: int, width of the rendering screen
    screen_height: int, height of the rendering screen
    
    Attributes:
        camera_pos,light_pos
        screen_width,screen_height

        objects: dictionary of CSG objects in the scene - Key: object name, Value: CSG_object_node
        camera: camera object
        light_sources: dictionary of light sources in the scene - Key: color+id, Value: Light_source object
        canvas_window: Tkinter root window for the canvas
        canvas: Tkinter canvas on which the scene will be rendered
        object_id: int, used to assign unique ids to objects
        light_id: int, used to assign unique ids to light sources
        log: Log object to write out actions performed in the application
    
    """

    def __init__(self,camera_pos = [0,0,-5],light_pos = [10,-10,10],screen_width=300,screen_height=300):
        
        self.objects = dict()
        self.camera = camera(np.array(camera_pos))
        
        self.width = screen_width
        self.height = screen_height

        window = tk.Tk()
        window.title("Rendered Scene")

        self.canvas_window = window
        self.canvas = tk.Canvas(self.canvas_window,width=self.width,height=self.height,bg="black")
        self.canvas.pack()
        self.canvas.image = None

        #used for assigning ids to objects
        self.object_id = 0 
        self.light_id = 0

        self.light_sources = dict()
        self.add_light(position=light_pos)


    #function to render the scene
    def render(self):
        """
        Renders the scene onto the canvas in the canvas window and starts the Tkinter main loop for that window 
        """

        #clear the window of any previous canvas
        for widget in self.canvas_window.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.canvas_window,width=self.width,height=self.height,bg="black")
        canvas.pack()

        self.canvas = canvas
        #render the scene and print the time taken
        start_time = time.time()
        self.log.write("Rendering scene...")
        rendering.render_scene(self.canvas,self.objects,self.camera,self.light_sources)
        end_time = time.time()
        self.log.write(f"Scene rendered in {end_time - start_time:.2f} seconds")

        print("Rendering complete")
        self.canvas_window.mainloop()

    #function to clear the scene

    def clear_scene(self):
        """
        Clears the scene by removing all objects and light sources from the scene
        """
        self.objects = dict()
        self.light_sources = dict()
        self.object_id = 0
        self.light_id = 0
        self.log.clear()
        self.log.write("Cleared scene - all objects and light sources removed")

    #fuctions for adding, removing and manipulating objects
    def add_box(self):
        """
        Opens a dialog to get the dimensions of the box and adds it to the objects dictionary with a unique id  
        """
        d = box_dialog()
        d = d.result
        if d == None:
            return
        
        #create the box and add it to the objects dictionary
        self.objects[f"box{self.object_id}"] = csg.CSG_object_node(csg.Box(d[0],d[1],d[2]))

        #wrtite to log
        self.log.write(f"Added box{self.object_id} with dimensions {d[0]}, {d[1]}, {d[2]}")

        #increment the object id to ensure unique ids
        self.object_id += 1
    
    def add_sphere(self):
        """
        Opens a dialog to get the radius of the sphere and adds it to the objects dictionary with a unique id
        """

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
        """
        Opens a dialog to get the radius and height of the cylinder and adds it to the objects dictionary with a unique id
        """

        d = cylinder_dialog()
        d = d.result
        if d == None:
            return


        self.objects[f"cylinder{self.object_id}"] = csg.CSG_object_node(csg.Cylinder(d[0],d[1]))
        self.log.write(f"Added cylinder{self.object_id} with radius {d[0]} and height {d[1]}")
        self.object_id += 1   

    def remove_object(self,object_name=None):
        """
        Removes the object with the given name from the objects dictionary or opens a dialog to get the name if not provided
        """

        
        if object_name == None:
            object_name = get_object(title="Remove object",objects=self.objects)

        if object_name in self.objects:
            self.log.write(f"Removed object {object_name}")
            del self.objects[object_name]
        else:
            print(f"Object {object_name} not found")

            
    def translate_object(self):
        """
        Opens a dialog to get the object name and translation vector and translates the object by that vector
        """

        object_name,translation_vector = get_translation(objects=self.objects)

        if object_name in self.objects:
            self.objects[object_name].translate(np.array(translation_vector))
            self.log.write(f"Translated object {object_name} by vector {translation_vector}")
        else:
            print(f"Object {object_name} not found")

    def rotate_object(self):
        """
        Opens a dialog to get the object name, angle and rotation axis and rotates the object by that angle around its center along that axis
        positive angle -> counter clockwise
        negative angle -> clockwise
        """

        object_name,angle,rotation_axis = get_rotation(objects=self.objects)

        angle = np.radians(angle)

        if object_name in self.objects:
            rot_mat = rotation.rotation_matrix(angle,rotation_axis,inverse=False)
            inverse_rot_mat = rotation.rotation_matrix(angle,rotation_axis,inverse=True)


            self.objects[object_name].rotate(rot_mat,inverse_rot_mat)
            self.log.write(f"Rotated object {object_name} by {np.degrees(angle)} degrees along the {rotation_axis} axis")

        else:
            print(f"Object {object_name} not found")

    def combine_objects(self,operation):
        """
        Opens a dialog to get the names of the two objects to be combined and combines them using the given operation

        operation: string, can be "union","difference","intersection"
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
    def move_camera(self,position_vector):
        """
        Moves the camera to the given position
        positon_vector: list of 3 floats
        """
        
        if position_vector is None:
            return
        self.camera.position = (np.array(position_vector))



        self.log.write(f"Moved camera to {position_vector}")
    
    def rotate_camera(self,info):
        """
        rotates the camera by the given angle along the given rotation axis
        positive angle -> counter clockwise
        """
        if info is None:
            return
        
        else:
            angle,rotation_axis = info
        angle = np.radians(angle)
        self.camera.rotate(rotation.rotation_matrix(angle,rotation_axis))

        self.log.write(f"Rotated camera by {np.degrees(angle)} degrees along the {rotation_axis} axis")


    #function to manipulate the light sources
    def add_light(self,position=None,color="white"):
        """
        Adds a light source at the given position with the given color or opens a dialog to get the position and color if not provided
        position: list of 3 floats
        color: string, can be "white","red","green","blue"    
        """
        if position is None:
            position,color = get_light_source()
            self.log.write(f"Added {color} light source at position {position}")
            

        self.light_sources[f"{color}{self.light_id}"] = Light_source(np.array(position),color)
        
        self.light_id += 1

    def remove_light(self,light_id):
        """
        Removes the light source with the given id from the light_sources dictionary 
        """
        if light_id in self.light_sources:
            del self.light_sources[light_id]
            self.log.write(f"Removed light source {light_id}")
        else:
            print(f"Light source {light_id} not found")

    def change_resolution(self):
        """
        Opens a dialog to get the new resolution and changes the width and height of the rendering screen
        """
        width,height = get_resolution()
        if width == None or height == None:
            return
        self.width = width
        self.height = height
        self.log.write(f"Changed resolution to {width}x{height}")

    
    #UI
    def setup_ui(self):
        """
        Main method of the application that sets up the UI in a separate window and starts the Tkinter main loop for that window

        5 main panels:
            1. Creating objects: sphere,box,cylinder
            2. Combining objects : union, intersection, difference, remove object
            3. Transforming objects : translate, rotate
            4. Camera and lighting controls : move camera, rotate camera, add light, remove light
            5. Log of actions performed: shows all the actions performed in the application

        3 buttons:
            button to render the scene 
            button to change the resolution of the rendering screen
            button to save the rendered image

        """
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
        ("Box", self.add_box),
        ("Cylinder",self.add_cylinder)
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
        ("Intersection", lambda: self.combine_objects("intersection")),
        ("Difference",lambda: self.combine_objects("difference")),
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
        render_scene_button = ttk.Button(main_container,command=self.render,text="Render scene")
        render_scene_button.grid(row=1,column=0,padx=10,pady=10)

        #clear scene button
        clear_scene_button = ttk.Button(main_container,command=self.clear_scene,text="Clear scene")
        clear_scene_button.grid(row=1,column=1,padx=10,pady=10)

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
    WIDTH = 400
    HEIGHT = 400
    CAMERA_POSITION = np.array([0,0,-6])
    LIGHT_POSITION = np.array([10,10,-10])

    app = App(camera_pos=CAMERA_POSITION,light_pos=LIGHT_POSITION,screen_width=WIDTH,screen_height=HEIGHT)
    
    app.setup_ui()



