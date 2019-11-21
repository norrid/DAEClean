# DAEClean 
Add-on for Blender 2.80

Clean geometry imported as DAE - Remove doubles, recalculate normals, triangles to quads, limitied dissolve and UV unwrap
Will also re-join loose geometry and remove imported cameras 

This is useful if importing models from SketchUp to Blender as DAE

Adds a button to UI menu (Press 'N')

A full tutorial on importing a .dae file export SketchUp into Blender can be found at https://www.dndrawings.com/add-ons

Install:
1. Navigate to File->User Preferences->Add-ons 
2. Click "Install Add-on From File"
3. Find DAEClean.py or DAEClean_2_8.zip and "Click Install Add-on From File"
4. Search for 3D View:DAE Clean and toggle check box
5. Click "Save User Settings"

Usage:
- Usually you will import a DAE file before using but can work on any scene

1. Select objects to clean in scene
2. Press Clean DAE button
3. The Status/Info bar in the Blender window will show how many vertices have been reduced from the selected objects 
