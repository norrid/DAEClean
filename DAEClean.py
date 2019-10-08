import bpy

# Project Name:        DAE Clean
# License:             GPL

bl_info = {
    "name": "DAE Clean",
    "description": "Removes doubles, recalculates normals and UV unwraps all selected objects. Intended for use mainly on imported DAEs but can work on any selected objects",
    "author": "Daniel Norris, DN DRAWINGS <https://dndrawings.com>",
    "version": (0, 1, 2),
    "blender": (2, 80, 0),
    "category": "3D View",
}


# decorator
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

    if not context.selected_objects:
        self.report({"INFO"}, "No Objects Selected")
        return

    selected = [obj for obj in context.selected_objects if obj.type == "MESH"]

    for obj in selected:
        orig_verts += len(obj.data.vertices)
        # must deselect all for uv unwrapping to work
        obj.select_set(False)

    # apply transformation - remove doubles and smart project UVs
    for obj in selected:
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        # Remove Doubles
        bpy.ops.mesh.remove_doubles()
        # Recalc normals
        bpy.ops.mesh.normals_make_consistent(inside=False)
        # Tris To Quads
        bpy.ops.mesh.tris_convert_to_quads()
        # Limited Dissolve
        bpy.ops.mesh.dissolve_limited()
        # UV Unwrap
        bpy.ops.uv.smart_project()
        new_verts += len(obj.data.vertices)
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.select_set(False)
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
class PANEL_PT_CleanDAE(bpy.types.Panel):
    bl_idname = "PANEL_PT_CleanDAE"
    bl_label = "Clean DAE Model"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DAE Tools"

    def draw(self, context):
        layout = self.layout

        # box = layout.box()
        row = layout.row(align=True)
        row.alignment = "EXPAND"

        row.operator("view3d.modal_operator_dae_clean")


#############################################
# REG/UN_REG
############################################


def register():
    bpy.utils.register_class(DAECleanOperator)
    bpy.utils.register_class(PANEL_PT_CleanDAE)


def unregister():
    bpy.utils.unregister_class(DAECleanOperator)
    bpy.utils.unregister_class(PANEL_PT_CleanDAE)


if __name__ == "__main__":
    register()
