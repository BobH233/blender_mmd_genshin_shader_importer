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
    'blender': (3, 6, 0),
    'version': (0, 0, 1),
    'location': '3D Viewport > Sidebar > BobHTool',
    'category': 'Generic',
}

import bpy
import os
from .operators.apply_shader_to_mmd_mode import BOBH_OT_apply_shader_to_mmd_model
from .operators.set_character_material_directory import BOBH_OT_set_character_material_directory
from .operators.apply_light_and_outline import BOBH_OT_apply_light_and_outline
from .operators.apply_postprocess import BOBH_OT_apply_postprocess

class BOBH_OT_open_url(bpy.types.Operator):
    """Operator to open URLs in web browser"""
    bl_idname = "bobh.open_url"
    bl_label = "Open URL"
    bl_description = "Open URL in web browser"
    
    url: bpy.props.StringProperty(name="URL", default="")
    
    def execute(self, context):
        import webbrowser
        webbrowser.open(self.url)
        return {'FINISHED'}

class BOBH_PT_main_panel(bpy.types.Panel):
    """Main panel for Genshin Impact shader tools"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BobHTool'
    bl_label = '仿原神渲染'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Main functionality box
        box = layout.box()
        box.label(text="一键导入原神Shader", icon='MATERIAL')
        
        # Material directory settings
        row = box.row()
        row.operator('bobh.set_material_directory', text='设置角色材质目录')
        
        row = box.row()
        row.label(text=f'当前材质目录: {scene.material_directory}')
        
        # Main operators
        row = box.row()
        row.operator('bobh.apply_shader_to_mmd_model', text='应用材质到选定mmd模型')
        
        row = box.row()
        row.operator('bobh.apply_light_and_outline', text='应用灯光和描边效果')
        
        row = box.row()
        row.operator('bobh.apply_postprocess', text='应用后处理')
        
        # Credits section
        layout.separator()
        credits_box = layout.box()
        credits_box.label(text="Credits:")
        
        # Original author
        row = credits_box.row(align=True)
        row.label(text="shader原作者:")
        op = row.operator('bobh.open_url', text='festivity', emboss=False)
        op.url = "https://github.com/festivities"
        
        # Modifier
        row = credits_box.row(align=True)
        row.label(text="shader修改:")
        op = row.operator('bobh.open_url', text='克里斯提亚娜', emboss=False)
        op.url = "https://space.bilibili.com/322607631"

def register():
    """Register all classes and properties"""
    bpy.utils.register_class(BOBH_OT_open_url)
    bpy.utils.register_class(BOBH_PT_main_panel)
    bpy.utils.register_class(BOBH_OT_set_character_material_directory)
    bpy.utils.register_class(BOBH_OT_apply_shader_to_mmd_model)
    bpy.utils.register_class(BOBH_OT_apply_light_and_outline)
    bpy.utils.register_class(BOBH_OT_apply_postprocess)

    bpy.types.Scene.material_directory = bpy.props.StringProperty(
        name='Material Directory',
        description='Directory for character materials',
        subtype='DIR_PATH',
        default=""
    )

def unregister():
    """Unregister all classes and properties"""
    bpy.utils.unregister_class(BOBH_OT_open_url)
    bpy.utils.unregister_class(BOBH_PT_main_panel)
    bpy.utils.unregister_class(BOBH_OT_set_character_material_directory)
    bpy.utils.unregister_class(BOBH_OT_apply_shader_to_mmd_model)
    bpy.utils.unregister_class(BOBH_OT_apply_light_and_outline)
    bpy.utils.unregister_class(BOBH_OT_apply_postprocess)

    del bpy.types.Scene.material_directory

if __name__ == '__main__':
    register()