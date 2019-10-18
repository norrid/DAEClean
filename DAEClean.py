# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        DAE Clean
# License:             GPL
# Authors:             Daniel Norris, DN Drawings

import bpy

from bpy.props import BoolProperty, StringProperty

bl_info = {
    "name": "DAE Clean",
    "description": "Removes doubles, recalculates normals, UV unwraps and other operations to clean imported mesh. Intended for use mainly on imported DAEs but can work on any selected objects",
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

    b_ld = context.scene.dc_settings.dc_limited_disolve_bool
    b_tq = context.scene.dc_settings.dc_tri_quad_bool

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
        if b_tq:
            bpy.ops.mesh.tris_convert_to_quads()
        # Limited Dissolve
        if b_ld:
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

        box = layout.box()
        row = layout.row(align=True)
        row.alignment = "EXPAND"

        row.operator("view3d.modal_operator_dae_clean")

        row = box.row()
        row.prop(context.scene.dc_settings, "dc_limited_disolve_bool", text="Limited Disolve")
        row.prop(context.scene.dc_settings, "dc_tri_quad_bool", text="Tris To Quads")


#############################################
# PROPERTIES
############################################
class DCSettings(bpy.types.PropertyGroup):
    dc_limited_disolve_bool: BoolProperty(
        name="", description="Limited Disolve Active", default=False
    )

    dc_tri_quad_bool: BoolProperty(
        name="", description="Tris To Quads Active", default=True
    )


#############################################
# REG/UN_REG
############################################
classes = (
    DAECleanOperator,
    PANEL_PT_CleanDAE,
    DCSettings,
)


def register():
    from bpy.utils import register_class
    # bpy.utils.register_class(DAECleanOperator)
    # bpy.utils.register_class(PANEL_PT_CleanDAE)
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.dc_settings = bpy.props.PointerProperty(type=DCSettings)


def unregister():
    from bpy.utils import unregister_class
    # bpy.utils.unregister_class(DAECleanOperator)
    # bpy.utils.unregister_class(PANEL_PT_CleanDAE)
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except RuntimeError:
            pass


if __name__ == "__main__":
    register()
