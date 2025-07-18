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


# Project Name:         Construction Lines
# License:              GPL
# Authors:              Daniel Norris, DN Drawings

bl_info = {
    "name": "DAEClean",
    "description": "Removes doubles, recalculates normals, UV unwraps and other operations to clean imported mesh. Intended for use mainly on imported DAEs but can work on any selected objects",
    "author": "Daniel Norris, DN DRAWINGS <https://dndrawings.com>",
    "version": (0, 1, 7),
    "blender": (2, 80, 0),
    "category": "3D View",
}


import importlib

from . import DAEClean
# importlib.reload(construction_lines28)

from .DAEClean import VIEW_OT_DAEClean, PANEL_PT_CleanDAE, DCSettings


import bpy  # type: ignore


############################################
# REG/UN_REG
############################################
classes = (
    VIEW_OT_DAEClean,
    PANEL_PT_CleanDAE,
    DCSettings
)


#############################################
# REG/UN_REG
############################################
classes = (VIEW_OT_DAEClean, PANEL_PT_CleanDAE, DCSettings)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.dc_settings = bpy.props.PointerProperty(type=DCSettings)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except RuntimeError:
            pass


if __name__ == "__main__":
    register()
