import tkinter
from tkinter import ttk
from tkinter import simpledialog,messagebox
import os

def xyz_coordinates_entries(frame, entry_row):
        """
        returns the 3 entry fields for the coordinates of the center
        
        """
        # Center X
        ttk.Label(frame, text="X:").grid(row=entry_row, column=0, padx=5, pady=5, sticky="w")
        x_entry = ttk.Entry(frame)
        x_entry.grid(row=entry_row, column=1, padx=5, pady=5, sticky="ew")

        # Center Y
        ttk.Label(frame, text="Y:").grid(row=entry_row, column=2, padx=5, pady=5, sticky="w")
        y_entry = ttk.Entry(frame)
        y_entry.grid(row=entry_row, column=3, padx=5, pady=5, sticky="ew")

        # Center Z
        ttk.Label(frame, text="Z:").grid(row=entry_row, column=4, padx=5, pady=5, sticky="w")
        z_entry = ttk.Entry(frame)
        z_entry.grid(row=entry_row, column=5, padx=5, pady=5, sticky="ew")

        return (x_entry,y_entry,z_entry)


def simple_field(frame,entry_row,prompt):
        """
        Returns a single entry field with a prompt label
        """

        ttk.Label(frame, text=prompt).grid(row=entry_row, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(frame)
        entry.grid(row=entry_row, column=1, padx=5, pady=5, sticky="ew")

        return entry
        



class shpere_dialog(simpledialog.Dialog):
    """
    A dialog to get the radius of the sphere.Checks that the input is a valid number.

    Attributes:
        result (list): None if the dialog was cancelled, otherwise a list(radius)
    """

    def __init__(self, parent=None, title = None):

        super().__init__(parent, title)

    def body(self,master):

        self.radius_entry = simple_field(master,0,"Radius: ")

        #self.center_entries = center_coordinates_entries(master,1)

    def validate(self):
        """
        Function that runs when the ok button is pressed. Validates the input and sets the result attribute
        """
        #radius
        try:
            radius = self.getdouble(self.radius_entry.get())
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                f"Invalid radius"+ "\nPlease try again",
                parent = self
            )
            return 0
        
        self.result = [radius]
        return 1
 
class box_dialog(simpledialog.Dialog):
    """
    A dialog to get the dimensions of the box. Checks that the inputs are valid numbers.

    Attributes:
        result (list): None if the dialog was cancelled, otherwise a list(length,width,height)
    """
     
    def __init__(self, parent=None, title = None):
          
        super().__init__(parent, "Box")

    def body(self,master):

        self.length_entry = simple_field(master,0,"Length: ")
        self.width_entry = simple_field(master,1,"Width: ")
        self.height_entry = simple_field(master,2,"Height: ")

    def validate(self):
        """
        Function that runs when the ok button is pressed. Validates the input and sets the result attribute
        """
        #dimension of the box
        dims = []
        for name,entry in [("length",self.length_entry),("width",self.width_entry),("height",self.height_entry)]:
            try:
                dims.append(self.getdouble(entry.get()))
            except ValueError:
                messagebox.showwarning(
                    "Illegal value",
                    f"Invalid {name}"+ "\nPlease try again",
                    parent = self
                )
                return 0
            
        self.result = dims
        return 1
    
class cylinder_dialog(simpledialog.Dialog):
    """
    Dialog to get the dimensions of the cylinder. Checks that the inputs are valid numbers.
    Attributes:
        result (list): None if the dialog was cancelled, otherwise a list(radius,height)   
    """
    def __init__(self, parent=None, title = None):
          
        super().__init__(parent, "Cylinder")

    def body(self,master):

        self.radius_entry = simple_field(master,0,"Radius: ")
        self.height_entry = simple_field(master,1,"Height: ")

    def validate(self):
        #radius and height of the cylinder
        dims = []
        for name,entry in [("radius",self.radius_entry),("height",self.height_entry)]:
            try:
                dims.append(self.getdouble(entry.get()))
            except ValueError:
                messagebox.showwarning(
                    "Illegal value",
                    f"Invalid "+ "\nPlease try again",
                    parent = self
                )
                return 0
            
        self.result = [dims[0],dims[1]]
        return 1
     

class Dialog_2_objects(simpledialog.Dialog):
    """
    Dialog to get two objects from a list of objects. Creates two fields with a dropdown menu to select the objects.

    Objects: list of object names
    
    Attributes:
        result (tuple): None if the dialog was cancelled, otherwise a tuple (obj_name1,obj_name2)
    """
    def __init__(self, parent=None, title=None, objects=[]):
        self.objects = objects
        super().__init__(parent, title)
        

    def body(self,master):
        label1 = ttk.Label(master,text="object 1")
        cb1 =ttk.Combobox(master=master,values=self.objects)
        cb1.set("Select an object")

        label1.grid(row=0,column=0)
        cb1.grid(row =1,column=0,padx=10,pady=10)

        label2 = ttk.Label(master,text="object 2")

        cb2 =ttk.Combobox(master=master,values=self.objects)
        cb2.set("Select an object")

        label2.grid(row=0,column=1)
        cb2.grid(row =1,column=1,padx=10,pady=10)

        self.object1 = cb1
        self.object2 = cb2

    def validate(self):
        
        obj1 = self.object1.get()
        if obj1 == "Select an object":
            messagebox.showwarning(
                    "Illegal value",
                    f"Please select object1",
                    parent = self
                )
            return 0
        
        obj2 = self.object2.get()
        if obj2 == "Select an object":
            messagebox.showwarning(
                    "Illegal value",
                    f"Please select object2",
                    parent = self
                )
            return 0

        self.result = (obj1,obj2)
        return 1
    
def get_2_objects(title:str,objects:dict):
    """
    Takes in the title of the prompt and the objects returns a tuple (obj_name1,obj_name2)

    Title: str
    Objects: dictionary of objects, keys are object names
    """

    d = Dialog_2_objects(title=title,objects=[*objects.keys()])
    return d.result
        
class Dialog_1_object(simpledialog.Dialog):
    """
    Dialog to get one object from a list of objects. Creates a field with a dropdown menu to select the object.
    Objects: list of object names
    Attributes:
        result (str): None if the dialog was cancelled, otherwise the name of the selected object
    """
    def __init__(self, parent=None, title=None, objects=[]):
        self.objects = objects
        super().__init__(parent, title)
        

    def body(self,master):
        label1 = ttk.Label(master,text="Select object")
        cb1 =ttk.Combobox(master=master,values=self.objects)
        cb1.set("Select an object")

        label1.grid(row=0,column=0)
        cb1.grid(row =1,column=0,padx=10,pady=10)

        self.object = cb1

    def validate(self):
        
        obj1 = self.object.get()
        if obj1 == "Select an object":
            messagebox.showwarning(
                    "Illegal value",
                    f"Please select object or press cancel",
                    parent = self
                )
            return 0

        self.result = obj1
        return 1

        
def get_object(title,objects):
    """
    Takes in the title of the pop-up and the objects returns the name of the selected object or None 
    """
    d = Dialog_1_object(title=title,objects=[*objects.keys()])
    return d.result

class Dialog_translation(simpledialog.Dialog):
    """
    class for the dialog that asks for the transaltion vector and the object to translate in one dialog

    Attributes:
        result (tuple): None if the dialog was cancelled, otherwise a tuple (obj_name,[x,y,z])
    """
    def __init__(self, parent=None, title=None,objects=[]):
        self.objects = objects
        super().__init__(parent, title)

    def body(self,master):
        label1 = ttk.Label(master,text="Select object")
        cb1 =ttk.Combobox(master=master,values=self.objects)
        cb1.set("Select an object")

        label1.grid(row=0,column=0)
        cb1.grid(row =0,column=1,padx=10,pady=10)

        self.object = cb1

        ttk.Label(master, text="Translation vector:").grid(row=1, column=0, padx=5, pady=5, sticky="w", columnspan=6)

        self.x_entry,self.y_entry,self.z_entry = xyz_coordinates_entries(master,2)

    def validate(self):
        obj1 = self.object.get()
        if obj1 == "Select an object":
            messagebox.showwarning(
                    "Illegal value",
                    f"Please select object",
                    parent = self
                )
            return 0

        try:
            x = self.getdouble(self.x_entry.get())
            y = self.getdouble(self.y_entry.get())
            z = self.getdouble(self.z_entry.get())
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                f"Invalid translation vector"+ "\nPlease try again",
                parent = self
            )
            return 0

        self.result = (obj1,[x,y,z])
        return 1

def get_translation(objects:dict):
    """
    Takes in the objects returns a tuple (obj_name,[x,y,z]) or None if cancelled
    """
    d = Dialog_translation(title="Translate object",objects=[*objects.keys()])
    return d.result


class Dialog_rotation(simpledialog.Dialog):
    """
    class for the dialog that asks for the rotation angle and axis and the object to rotate in one dialog

    Objects: list of object names
    rotation axis: "x","y","z"
    angle: in degrees

    Attributes:
        result (tuple): None if the dialog was cancelled, otherwise a tuple (obj_name,angle,axis)
    """
    def __init__(self, parent=None, title=None,objects=[]):
        self.objects = objects
        super().__init__(parent, title)

    def body(self,master):
        label1 = ttk.Label(master,text="Select object")
        cb1 =ttk.Combobox(master=master,values=self.objects)
        cb1.set("Select an object")

        label1.grid(row=0,column=0)
        cb1.grid(row =0,column=1,padx=10,pady=10)

        self.object = cb1

        self.angle_entry = simple_field(master,1,"Angle (degrees): ")

        ttk.Label(master, text="Rotation axis:").grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.axis_cb = ttk.Combobox(master=master,values=["x","y","z"])
        self.axis_cb.set("Select axis")
        self.axis_cb.grid(row=2,column=1,padx=10,pady=10)


    def validate(self):
        obj1 = self.object.get()
        if obj1 == "Select an object":
            messagebox.showwarning(
                    "Illegal value",
                    f"Please select object",
                    parent = self
                )
            return 0

        try:
            angle = self.getdouble(self.angle_entry.get())
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                f"Invalid angle"+ "\nPlease try again",
                parent = self
            )
            return 0

        axis = self.axis_cb.get()
        if axis not in ["x","y","z"]:
            messagebox.showwarning(
                    "Illegal value",
                    f"Please select rotation axis",
                    parent = self
                )
            return 0

        self.result = (obj1,angle,axis)
        return 1
    
def get_rotation(objects):
    d = Dialog_rotation(title="Rotate object",objects=[*objects.keys()])
    return d.result

class Dialog_xyz_coordinates(simpledialog.Dialog):
    def __init__(self, parent=None, title=None):
        super().__init__(parent, title)

    def body(self,master):

        self.center_entries = xyz_coordinates_entries(master,0)

    def validate(self):
        coords = []
        for name,entry in zip(["X","Y","Z"],self.center_entries):
            try:
                coords.append(self.getdouble(entry.get()))
            except ValueError:
                messagebox.showwarning(
                    "Illegal value",
                    f"Invalid {name} coordinate"+ "\nPlease try again",
                    parent = self
                )
                return 0
            
        self.result = coords
        return 1


class Dialog_only_rotation(simpledialog.Dialog):
    def __init__(self, parent=None, title=None):
        super().__init__(parent, title)

    def body(self,master):

        self.angle_entry = simple_field(master,0,"Angle (degrees): ")

        ttk.Label(master, text="Rotation axis:").grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.axis_cb = ttk.Combobox(master=master,values=["x","y","z"])
        self.axis_cb.set("Select axis")
        self.axis_cb.grid(row=1,column=1,padx=10,pady=10)


    def validate(self):

        try:
            angle = self.getdouble(self.angle_entry.get())
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                f"Invalid angle"+ "\nPlease try again",
                parent = self
            )
            return 0

        axis = self.axis_cb.get()
        if axis not in ["x","y","z"]:
            messagebox.showwarning(
                    "Illegal value",
                    f"Please select rotation axis",
                    parent = self
                )
            return 0

        self.result = (angle,axis)
        return 1
    

class Dialog_light_source(simpledialog.Dialog):
    def __init__(self, parent=None, title=None):
        super().__init__(parent, title)

    def body(self,master):

        self.position_entries = xyz_coordinates_entries(master,0)

        ttk.Label(master, text="Light color:").grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.color_cb = ttk.Combobox(master=master,values=["white","red","green","blue"])
        self.color_cb.set("Select color")
        self.color_cb.grid(row=1,column=1,padx=10,pady=10)

    def validate(self):
        coords = []
        for name,entry in zip(["X","Y","Z"],self.position_entries):
            try:
                coords.append(self.getdouble(entry.get()))
            except ValueError:
                messagebox.showwarning(
                    "Illegal value",
                    f"Invalid {name} coordinate"+ "\nPlease try again",
                    parent = self
                )
                return 0
            
        color = self.color_cb.get()
        if color not in ["white","red","green","blue"]:
            messagebox.showwarning(
                    "Illegal value",
                    f"Please select light color",
                    parent = self
                )
            return 0

        self.result = (coords,color)
        return 1


def get_translation_vector():
    """
    Prompts the user to enter the translation vector. Returns a list [x,y,z] or None if cancelled.
    """
    d = Dialog_xyz_coordinates(title="New Camera Position")
    return d.result

def get_light_id(light_sources:dict):
    """
    Prompts the user to select a light source from the list of light sources. Returns the name of the selected light source or None if cancelled.
    """
    d = Dialog_1_object(title="Select light source",objects=[*light_sources.keys()])
    return d.result


def get_camera_rotation():
    """
    Prompts the user to enter the angle and the axis that they want the camera to rotate. Returns a tuple (angle,axis) or None if cancelled.
    """

    d = Dialog_only_rotation(title="Camera rotation")
    return d.result

def get_light_source():
    """
    Prompts the user to enter the position and color of the light source. Returns a tuple ([x,y,z],color) or None if cancelled.
    """
    d = Dialog_light_source(title="Add light source")
    return d.result


class Dialog_resolution(simpledialog.Dialog):
    """
    A dialog to get the resolution of the image. Checks that the inputs are valid positive integers.
    Attributes:
        result (list): None if the dialog was cancelled, otherwise a list [width,height]
    """
    def __init__(self, parent=None, title=None):
        super().__init__(parent, title)

    def body(self,master):

        self.width_entry = simple_field(master,0,"Width (pixels): ")
        self.height_entry = simple_field(master,1,"Height (pixels): ")

    def validate(self):
        dims = []
        for name,entry in [("width",self.width_entry),("height",self.height_entry)]:
            try:
                dims.append(int(self.getint(entry.get())))
                if dims[-1] <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Illegal value",
                    f"Invalid {name}"+ "\nPlease enter a positive integer",
                    parent = self
                )
                return 0
            
        self.result = dims
        return 1
    
def get_resolution():
    """
    Prompts the user to enter the resolution of the image. Returns a list [width,height] or None if cancelled.
    """
    d = Dialog_resolution(title="Set resolution")
    return d.result


class Dialog_file_name(simpledialog.Dialog):
    """
    A dialog to get the file name to save the image. Checks that the input is valid and that the file does not already exist.

    Attributes:
        result (str): None if the dialog was cancelled, otherwise the file name without extension
    """

    def __init__(self, parent=None, title=None):
        super().__init__(parent, title)

    def body(self,master):

        self.file_name_entry = simple_field(master,0,"File name (without extension): ")

    def validate(self):
        file_name = self.file_name_entry.get()
        file_name = file_name.strip()
        if not file_name:
            messagebox.showwarning(
                "Illegal value",
                f"File name cannot be empty"+ "\nPlease try again",
                parent = self
            )
            return 0
        if os.path.exists(file_name + ".png"):
            messagebox.showwarning(
                "Illegal value",
                f"File {file_name}.png already exists"+ "\nPlease choose another filename or delete the existing file",
                parent = self
            )
            return 0  
        self.result = file_name
        return 1
    
def get_file_name():
    """
    Prompts the user to enter a file name to save the image. Returns the file name without extension or None if cancelled. 
    Checks that the file does not already exist.
    """
    d = Dialog_file_name(title="Enter file name")
    return d.result