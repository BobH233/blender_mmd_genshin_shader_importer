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
    'name': 'Bobh_mmd_genshin_shader_importer',
    'author': 'BobH',
    'description': 'import festivities genshin shader automatically to MMD Model',
    'blender': (3, 60, 0),
    'version': (0, 0, 1),
    'location': '3D Viewport > Sidebar > BobHTool',
    'category': 'Generic',
}

import bpy
import os
from .operators.apply_shader_to_mmd_mode import BOBH_OT_apply_shader_to_mmd_model
from .operators.import_shader import BOBH_OT_import_shader
from .operators.set_character_material_directory import BOBH_OT_set_character_material_directory
from .operators.import_outline import BOBH_OT_import_outline

class BOBH_PT_main_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bl_category = 'BobHTool'
    bl_label = 'BobHTool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box1 = layout.box()
        current_box = box1
        row = current_box.row()

        row.label(text='一键导入原神Shader', icon='MATERIAL')

        row = current_box.row()
        row.operator('bobh.import_shader', text='导入原神Shader预设')
        row = current_box.row()
        row.operator('bobh.import_outline', text='导入原神描边预设')

        row = current_box.row()
        row.operator('bobh.set_material_directory', text='设置角色材质目录')
        row = current_box.row()
        row.label(text=f'当前材质目录: {scene.material_directory}')

        row = current_box.row()
        row.operator('bobh.apply_shader_to_mmd_model', text='应用材质到选定mmd模型')


def register():
    bpy.utils.register_class(BOBH_PT_main_panel)

    bpy.utils.register_class(BOBH_OT_import_shader)
    bpy.utils.register_class(BOBH_OT_set_character_material_directory)
    bpy.utils.register_class(BOBH_OT_apply_shader_to_mmd_model)
    bpy.utils.register_class(BOBH_OT_import_outline)
    bpy.types.Scene.material_directory = bpy.props.StringProperty(
        name='Material Directory',
        description='Directory for character materials',
        subtype='DIR_PATH'
    )


def unregister():
    bpy.utils.unregister_class(BOBH_PT_main_panel)

    bpy.utils.unregister_class(BOBH_OT_import_shader)
    bpy.utils.unregister_class(BOBH_OT_set_character_material_directory)
    bpy.utils.unregister_class(BOBH_OT_apply_shader_to_mmd_model)
    bpy.utils.unregister_class(BOBH_OT_import_outline)
    del bpy.types.Scene.material_directory


if __name__ == '__main__':
    register()