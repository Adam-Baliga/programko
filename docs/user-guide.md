# User guide - CSG editor

## Table of contents

1. [Getting Started](#getting-started)
3. [UI Overview](#ui-overview)

## Getting Started <a name="getting-started"></a>
### Installation
To install the CSG editor, follow these steps:
´
git clone https://github.com/Adam-Baliga/programko
pip install -r requirements.txt
´

### Running the Application

To run the CSG editor run the main.py file.

## UI overview <a name="ui-overview"></a>
There are 2 main sections of the UI:

1. viewport - where the 3D scene is rendered
2. control panel - where the user can interact with the scene

### Viewport
The viewport is a simple Tkinter canvas where the 3D scene is rendered using raymarching.

### Control panel
The control panel is where the user can create the scene. It is divided into several sections and buttons:

![Picture of the Control Panel.](docs/images/control_panel.png)


Sections:
1. **Create objects**:
    - where the user can create primitives (box, sphere, cylinder) and add them to the scene
    - all objects are added centered at the origin when first created
    - Buttons:
        - Add box > opens a dialog to input the box parameters (length, width, height) and adds the box to the scene 
        - Add sphere > opens a dialog to input the sphere parameters (radius) and adds the sphere to the scene 
        - Add cylinder > opens a dialog to input the cylinder parameters (radius, height) and adds the cylinder to the scene 

    
2. **Object operations**:
    - where the user can perform CSG operations (union, intersection, difference) on the object they select as well as delete objects
    - Each button opens a dialog to select the objects to perform the operation with
    - The user can select only two objects for union, intersection, and difference operations
    - Buttons:
        - Union > creates a new object that is the union of the two selected objects
        - Intersection > creates a new object that is the intersection of the two selected objects
        - Difference > creates a new object that is the difference of the two selected objects
        - Delete > deletes the selected object from the scene

> [!NOTE]
> Union, intersection change the center of the new object to be the midpoint of the two selected objects.
> Difference changes the center of the new object to be the center of the first selected object.

3. **Transform objects**:
    - where the user can translate, rotate the object they select
    - Each button opens a dialog to input the transformation parameters
    - Buttons:
        - Translate > translates the selected object by the input parameters (x,y,z)
        - Rotate > rotates the selected object by the angle (in degrees) around its center along the input axis "x", "y" or "z"


4. **Camera and lighting** 
    - where the user can adjust the camera position and rotation and add or remove lighting from the scene
    - Buttons:
        - Set camera position > opens a dialog to input the new camera position (x,y,z)
        - Set camera rotation > opens a dialog to input the camera rotation (in degrees) around the input axis "x", "y" or "z"
        - Add light > opens a dialog to input the light position (x,y,z) and color and adds the light to the scene
        - Remove light > opens a dialog to select the light to remove from the scene

5. **Action log** 
    - where the user can see the actions that have been performed performed

6. **Bottom buttons**:
    - Render scene > renders the scene in the viewport
    - Save image  > opens a dialog to input the file name and saves the rendered scene as a png file
    - Clear scene > clears the scene of all objects and lights
    - Change resolution > opens a dialog to input the new resolution (width, height) of the viewport

### Example workflow
1. Create a box and a sphere using the "Add box" and "Add sphere" buttons in the "Create objects" section.
2. Select the box and sphere using the "Intersection" button in the "Object operations" section to create a new object that is the intersection of the two.
3. Select the new object and use the "Translate" button in the "Transform objects" section to move it to a new position.
4. Use the "Set camera position" and "Set camera rotation" buttons in the "Camera and lighting" section to adjust the camera view.
5. Use the "Add light" button in the "Camera and lighting" section to add a light to the scene.
6. Click the "Render scene" button to render the scene in the viewport.
7. Click the "Save image" button to save the rendered scene as a png file.










