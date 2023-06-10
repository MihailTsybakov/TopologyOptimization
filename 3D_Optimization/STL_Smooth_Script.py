import bpy

import_path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data\\Model.gltf'
export_path = 'C:\\Users\\mihai\\Desktop\\Unik\\Optimization\\3D\\Data\\STL_Models\\Smooth_model.stl'

# Importing GLTF scene
bpy.ops.import_scene.gltf(filepath = import_path)

# Deleting Renderer node:
bpy.ops.object.select_all(action = 'DESELECT')
bpy.data.objects['Renderer Node'].select_set(True)
bpy.ops.object.delete()

# Deleting Camera node:
bpy.ops.object.select_all(action = 'DESELECT')
bpy.data.objects['Camera Node'].select_set(True)
bpy.ops.object.delete()

# Deleting Camera:
bpy.ops.object.select_all(action = 'DESELECT')
bpy.data.objects['Camera'].select_set(True)
bpy.ops.object.delete()

# Deleting Cube:
bpy.ops.object.select_all(action = 'DESELECT')
bpy.data.objects['Cube'].select_set(True)
bpy.ops.object.delete()

# Deleting Light:
bpy.ops.object.select_all(action = 'DESELECT')
bpy.data.objects['Light'].select_set(True)
bpy.ops.object.delete()

# Setting origin
bpy.ops.object.select_all(action = 'DESELECT')
bpy.data.objects['mesh0'].select_set(True)

bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')

# Rotating
ov=bpy.context.copy()
ov['area']=[a for a in bpy.context.screen.areas if a.type=="VIEW_3D"][0]
bpy.ops.transform.rotate(ov, value = 3.1415/2, orient_axis = 'Y')

# Moving to (0, 0, 0)
bpy.data.objects['mesh0'].location = (0,0,0)

# Catmull-Clark surface subdivision
object_ = bpy.data.objects['mesh0']

# Setting active object
bpy.context.view_layer.objects.active = object_

# Adding modifier
bpy.ops.object.modifier_add(type='SUBSURF')
bpy.context.object.modifiers["Subdivision"].levels = 2

# Applying modifier
bpy.ops.object.modifier_apply(modifier = 'Subdivision', report = True)

# Exporting like STL file
bpy.ops.export_mesh.stl(filepath = export_path)