# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


bl_info = {
    "name": "Bobh_mmd_genshin_shader_importer",
    "author": "BobH",
    "description": "import festivities genshin shader automatically to MMD Model",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

"""
See YouTube tutorial here: https://youtu.be/Qyy_6N3JV3k
"""

bl_info = {
    "name": "My Custom Panel",
    "author": "Victor Stepanov",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D Viewport > Sidebar > My Custom Panel category",
    "description": "My custom operator buttons",
    "category": "Development",
}

# give Python access to Blender's functionality
import bpy
import os

class BOBH_PT_main_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    bl_category = "BobHTool"
    bl_label = "BobHTool"

    def draw(self, context):
        layout = self.layout
        box1 = layout.box()
        current_box = box1
        row = current_box.row()
        row.label(text="导入原神Shader")
        row = current_box.row()
        row.operator("bobh.import_shader", text="导入原神Shader预设")

class BOBH_OT_import_shader_operator(bpy.types.Operator):
    bl_label = "Select .blend"
    bl_idname = "bobh.import_shader"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    MAT_LIST = [
        ('HoYoverse - Genshin Body', 'GI_Body'),
        ('HoYoverse - Genshin Face', 'GI_Face'),
        ('HoYoverse - Genshin Hair', 'GI_Hair'),
        ('HoYoverse - Genshin Outlines', 'GI_Outlines'),
    ]

    def try_import_material(self, filepath, origin_name, import_name):
        material_path = material_path = os.path.join(filepath, "NodeTree", "Material", origin_name)
        bpy.ops.wm.append(filepath=material_path, directory=os.path.join(self.filepath, "Material"), filename=origin_name)
        if origin_name in bpy.data.materials:
            imported_material = bpy.data.materials[origin_name]
            imported_material.name = import_name
            return True
        else:
            raise Exception(f"无法导入材质{origin_name}, 检查blend文件路径是否正确")

    def execute(self, context):
        if not self.filepath.endswith(".blend"):
            self.report({'ERROR'}, "请选择预设的.blend.文件")
            return {'CANCELLED'}
        
        try:
            for mat_name, import_name in self.MAT_LIST:
                self.try_import_material(self.filepath, mat_name, import_name)
        except Exception as e:
            self.report({'ERROR'}, f"{str(e)}")
            return {'CANCELLED'}
        
        self.report({'INFO'}, "导入Shader预设成功")

        return {'FINISHED'}

    def invoke(self, context, event):
        self.bl_label = "Select .blend"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(BOBH_PT_main_panel)
    bpy.utils.register_class(BOBH_OT_import_shader_operator)


def unregister():
    bpy.utils.unregister_class(BOBH_PT_main_panel)
    bpy.utils.unregister_class(BOBH_OT_import_shader_operator)


if __name__ == "__main__":
    register()