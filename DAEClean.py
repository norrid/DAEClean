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

import bpy  # type: ignore
import bmesh  # type: ignore

from bpy.props import BoolProperty, FloatProperty  # type: ignore


l_disolve_setting = {
    "normal": 'NORMAL',
    "material": 'MATERIAL'

}

def return_l_dissolve_setting(dissolve_by_material: bool):
    if dissolve_by_material:
        return l_disolve_setting["material"]
    return l_disolve_setting["normal"]


# decorator
def change_mouse_cursor(func):
    def change_cursor(*args):
        bpy.context.window.cursor_modal_set("WAIT")
        func(*args)
        bpy.context.window.cursor_modal_set("DEFAULT")

    return change_cursor


def clean_up():
    bpy.context.window.cursor_modal_set("DEFAULT")


def join_loose_faces(context, selected):
    rem_list = []

    i = -1
    max_i = len(selected)
    while i < max_i:
        i += 1
        try:
            obj = bpy.context.scene.objects[selected[i]]
            rem_list = traverse_groups(context, [c.name for c in obj.children])
            selected = [x for x in selected if x not in rem_list]
        except:
            continue

    return selection_by_name(selected)


def traverse_groups(context, selected):
    rem_list = []
    obj_store = []
    objs = []

    for obj_n in selected:
        # make sure item is not already assigned to the obj_store
        if obj_n in (item for sublist in obj_store for item in sublist):
            continue
        s_o = obj_n
        if obj_n.find(".") != -1:
            s_o = obj_n.split(".")[0]

        objs = [o for o in selected if o.find(s_o + ".") != -1 and
                o != obj_n and
                o not in (item for sublist in obj_store for item in sublist)
                ]
        if objs:
            objs.append(obj_n)
            obj_store.append(objs)

    deselect_all(context)
    rem_list = []
    # join objects
    for group in obj_store:
        for obj in group:
            ob = bpy.context.scene.objects[obj]
            ob.select_set(True)
            context.view_layer.objects.active = ob
            rem_list.append(obj)
        bpy.ops.object.join()
        rem_list.pop(-1)
        context.view_layer.objects.active.select_set(False)

    return rem_list


def remove_doubles(selected, tolernace):
    meshes = set(o.data for o in selected)

    bm = bmesh.new()

    for m in meshes:
        bm.from_mesh(m)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=tolernace)
        bm.to_mesh(m)
        m.update()
        bm.clear()
    bm.free()


def apply_transforms(selected, context: bpy.context):
    for obj in selected:
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply()
        obj.select_set(False)


def select_objects(objects):
    for obj in objects:
        obj.select_set(True)


def deselect_all(context):
    for obj in context.selected_objects:
        obj.select_set(False)


def selection_by_name(names):
    selected = []
    for obj in names:
        ob = bpy.context.scene.objects[obj]
        ob.select_set(True)
        selected.append(ob)

    return selected


@change_mouse_cursor
def clean_DAE(self, context):
    orig_verts = 0
    new_verts = 0

    b_remd = context.scene.dc_settings.dc_rem_doubles_bool
    b_limd = context.scene.dc_settings.dc_limited_disolve_bool
    b_limd_mat = context.scene.dc_settings.dc_limited_disolve_material_bool
    b_triq = context.scene.dc_settings.dc_tri_quad_bool
    b_joinl = context.scene.dc_settings.dc_loose_face_bool
    b_delc = context.scene.dc_settings.dc_camera_del_bool
    f_rdtol = context.scene.dc_settings.dc_rem_d_tol_float
    b_auto_smt = context.scene.dc_settings.dc_rem_auto_smooth_norms_bool
    b_rem_csn = context.scene.dc_settings.dc_rem_custom_split_normals
    b_apl_trans = context.scene.dc_settings.dc_apply_transforms

    if context.mode == "EDIT_MESH":
        bpy.ops.object.mode_set(mode="OBJECT")

    if not context.selected_objects:
        self.report({"INFO"}, "No Objects Selected")
        return

    cams = [obj for obj in context.selected_objects if obj.type == "CAMERA"]

    # join loose faces
    if b_joinl:
        selected = join_loose_faces(
            context, [obj.name for obj in context.selected_objects])
    else:
        selected = context.selected_objects

    selected = [obj for obj in selected if obj.type == "MESH"]

    for obj in selected:
        orig_verts += len(obj.data.vertices)
        # must deselect all for uv unwrapping to work
        obj.select_set(False)

    # Remove Doubles
    if b_remd:
        remove_doubles(selected, f_rdtol)

    # Apply all transforms
    if b_apl_trans:
        apply_transforms(selected, context)

    # deselect all
    deselect_all(context)

    # apply transformations to individual objects
    for obj in selected:
        obj.select_set(True)
        context.view_layer.objects.active = obj

        # Mesh Clean
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        try:
            # Tris To Quads
            if b_triq:
                bpy.ops.mesh.tris_convert_to_quads()
            # Limited Dissolve
            if b_limd:
                bpy.ops.mesh.dissolve_limited(delimit={return_l_dissolve_setting(b_limd_mat)})
            # Clear custom split normals
            if b_rem_csn:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            # UV Unwrap
            bpy.ops.uv.smart_project()
            # Recalc normals
            bpy.ops.mesh.normals_make_consistent(inside=False)

            new_verts += len(obj.data.vertices)
        except Exception as e:
            print(e)
            print("Unable to clean object: " + obj.name)

        # Switch back to Object mode
        bpy.ops.object.mode_set(mode="OBJECT")

        # Auto-smooth normals
        if b_auto_smt:
            bpy.ops.object.shade_auto_smooth(use_auto_smooth=False)

        obj.select_set(False)

    if b_delc:
        select_objects(cams)
        bpy.ops.object.delete()

    deselect_all(context)
    rem_v = orig_verts - new_verts
    self.report({"INFO"}, "Doubles removed:%s" % (rem_v))

#############################################
# OPERATOR
############################################
class VIEW_OT_DAEClean(bpy.types.Operator):
    """Removes doubles, recalculates normals and UV unwraps all selected objects"""

    bl_idname = "view3d.modal_operator_dae_clean"
    bl_label = "Clean DAE"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            clean_DAE(self, context)
        except Exception as e:
            print(e)
            clean_up()
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
        box.label(text="Clean Mesh:")
        row = layout.row(align=True)
        row.alignment = "EXPAND"

        row = box.row()
        row.prop(context.scene.dc_settings,
                 "dc_tri_quad_bool", text="Tris To Quads")

        row = box.row()
        row.prop(
            context.scene.dc_settings, "dc_rem_doubles_bool", text="Remove Doubles"
        )

        row.prop(
            context.scene.dc_settings, "dc_rem_d_tol_float", text="Distance"
        )

        row = box.row()
        row.prop(
            context.scene.dc_settings, "dc_loose_face_bool", text="Join Loose Faces"
        )

        row.prop(
            context.scene.dc_settings, "dc_camera_del_bool", text="Remove Cameras"
        )

        row = box.row()
        row.prop(
            context.scene.dc_settings, "dc_rem_auto_smooth_norms_bool", text="Remove Auto-Smooth Normals"
        )

        row = box.row()
        row.prop(
            context.scene.dc_settings, "dc_rem_custom_split_normals", text="Clear Custom Split Normals"
        )

        row = box.row()
        row.prop(
            context.scene.dc_settings, "dc_apply_transforms", text="Apply All Transforms"
        )

        box = layout.box()
        box.label(text="Limited Dissolve:")
        box.prop(
            context.scene.dc_settings, "dc_limited_disolve_bool", text="Limited Dissolve"
        )

        sub = box.row()
        sub.prop(
            context.scene.dc_settings, "dc_limited_disolve_material_bool", text="Limited Dissolve By Material"
        )
        sub.enabled = context.scene.dc_settings.dc_limited_disolve_bool

        # Execute Button
        box = layout.box()
        row = box.row()
        row.operator("view3d.modal_operator_dae_clean")



#############################################
# PROPERTIES
############################################
class DCSettings(bpy.types.PropertyGroup):
    dc_limited_disolve_bool: BoolProperty(
        name="", description="Limited Dissolve Mesh", default=False
    )

    dc_limited_disolve_material_bool: BoolProperty(
        name="", description="Limited Dissolve By Material", default=False
    )


    dc_tri_quad_bool: BoolProperty(
        name="", description="Tris To Quads Active", default=True
    )

    dc_loose_face_bool: BoolProperty(
        name="", description="Join Loose Faces", default=True
    )

    dc_camera_del_bool: BoolProperty(
        name="", description="Remove Cameras", default=True
    )

    dc_rem_doubles_bool: BoolProperty(
        name="", description="Remove Doubles", default=True
    )

    dc_rem_d_tol_float: FloatProperty(
        name="", description="Remove Doubles Tolerance", default=0.001
    )

    dc_rem_auto_smooth_norms_bool: BoolProperty(
        name="", description="Remove Auto-smoothing of normals", default=True
    )

    dc_rem_custom_split_normals: BoolProperty(
        name="", description="Clear Custom Split Normals", default=True
    )

    dc_apply_transforms: BoolProperty(
        name="", description="Apply All Transforms", default=True
    )