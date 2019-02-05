import bpy

# Project Name:        DAE Clean
# License:             GPL

bl_info = {
    "name": "DAE Clean",
    "description": "Removes doubles, recalculates normals and UV unwraps all selected objects. Intended for use mainly on imported DAEs but can work on any selected objects",
    "author": "Daniel Norris, DN DRAWINGS <https://dndrawings.com>",
    "version": (0, 1),
    "blender": (2, 7, 9),
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View",
}


#decorator
def change_mouse_cursor(func):
    def change_cursor(*args):
        bpy.context.window.cursor_modal_set("WAIT")
        func(*args)
        bpy.context.window.cursor_modal_set("DEFAULT")
    return change_cursor

@change_mouse_cursor
def clean_DAE(self, context):
    orig_verts = 0
    new_verts = 0
    #count initial amount of verticies
    if context.selected_objects != []:
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                d = obj.data
                orig_verts += len(d.vertices)

    #apply transformation - remove doubles and smart project UVs
    if context.selected_objects != []:
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                context.scene.objects.active = obj
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                #Remove Doubles
                bpy.ops.mesh.remove_doubles()
                #Recalc normals
                bpy.ops.mesh.normals_make_consistent(inside=False)
                #UV Unwrap
                bpy.ops.uv.smart_project()
                d = obj.data
                new_verts += len(d.vertices)
                bpy.ops.object.editmode_toggle()
    rem_v = orig_verts - new_verts
    self.report({"INFO"}, "Doubles removed:%s" % (rem_v))

#############################################
# OPERATOR
############################################

class DAECleanOperator(bpy.types.Operator):
    """Removes doubles, recalculates normals and UV unwraps all selected objects"""

    bl_idname = "view3d.modal_operator_dae_clean"
    bl_label = "Clean DAE"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        clean_DAE(self, context)
        return {"FINISHED"}


    def invoke(self, context, event):
        return self.execute(context)


#############################################
# PANEL
############################################
class CleanDAEPanel(bpy.types.Panel):
    bl_idname = "panel.clean_DAE_panel"
    bl_label = "Clean DAE Model"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        #box = layout.box()
        row = layout.row(align=True)
        row.alignment = "EXPAND"
        
        row.operator("view3d.modal_operator_dae_clean")

#############################################
# REG/UN_REG
############################################

def register():
    bpy.utils.register_class(DAECleanOperator)
    bpy.utils.register_class(CleanDAEPanel)


def unregister():
    bpy.utils.unregister_class(DAECleanOperator)
    bpy.utils.unregister_class(CleanDAEPanel)

if __name__ == "__main__":
    register()
