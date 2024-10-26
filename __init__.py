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

# give Python access to Blender's functionality
import bpy
import os
import json

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

        row.label(text='导入原神Shader', icon='MATERIAL')

        row = current_box.row()
        row.operator('bobh.import_shader', text='导入原神Shader预设')

        row = current_box.row()
        row.operator('bobh.set_material_directory', text='设置角色材质目录')
        row = current_box.row()
        row.label(text=f'当前材质目录: {scene.material_directory}')

        row = current_box.row()
        row.operator('bobh.apply_shader_to_mmd_model', text='应用材质到选定mmd模型')


class BOBH_OT_import_shader(bpy.types.Operator):
    bl_label = '选择shader的.blend文件'
    bl_idname = 'bobh.import_shader'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH') # type: ignore

    MAT_LIST = [
        ('HoYoverse - Genshin Body', 'GI_Body'),
        ('HoYoverse - Genshin Face', 'GI_Face'),
        ('HoYoverse - Genshin Hair', 'GI_Hair'),
        ('HoYoverse - Genshin Outlines', 'GI_Outlines'),
    ]

    def try_import_material(self, filepath, origin_name, import_name):
        material_path = material_path = os.path.join(filepath, 'NodeTree', 'Material', origin_name)
        bpy.ops.wm.append(filepath=material_path, directory=os.path.join(self.filepath, 'Material'), filename=origin_name)
        if origin_name in bpy.data.materials:
            imported_material = bpy.data.materials[origin_name]
            imported_material.name = import_name
            return True
        else:
            raise Exception(f'无法导入材质{origin_name}, 检查blend文件路径是否正确')

    def execute(self, context):
        if not self.filepath.endswith('.blend'):
            self.report({'ERROR'}, '请选择预设的.blend.文件')
            return {'CANCELLED'}
        
        try:
            for mat_name, import_name in self.MAT_LIST:
                self.try_import_material(self.filepath, mat_name, import_name)
        except Exception as e:
            self.report({'ERROR'}, f'{str(e)}')
            return {'CANCELLED'}
        
        self.report({'INFO'}, '导入Shader预设成功')

        return {'FINISHED'}

    def invoke(self, context, event):
        self.bl_label = 'Select .blend'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BOBH_OT_set_character_material_directory(bpy.types.Operator):
    bl_label = '选择角色解包材质目录'
    bl_idname = 'bobh.set_material_directory'
    directory: bpy.props.StringProperty(subtype='DIR_PATH') # type: ignore

    CHECK_MAT_LIST = [
        '_Tex_Body_Diffuse.png',
        '_Tex_Body_Lightmap.png',
        '_Tex_Body_Shadow_Ramp.png',
        '_Face_Diffuse.png',
        '_Hair_Diffuse.png',
        '_Hair_Lightmap.png',
        '_Hair_Shadow_Ramp.png',
    ]

    CHECK_OUTLINE_LIST = [
        '_Mat_Body.json',
        '_Mat_Face.json',
        '_Mat_Hair.json',
    ]

    def validate_path(self, path):
        png_files = [f for f in os.listdir(path) if f.endswith('.png')]
        missing_mat_files = [file for file in self.CHECK_MAT_LIST if not any(f.endswith(file) for f in png_files)]
        if missing_mat_files:
            raise Exception(f'目录缺少以下所需的材质文件: {", ".join(missing_mat_files)}')
        materials_dir = os.path.join(path, 'Materials')
        if not os.path.isdir(materials_dir):
            raise Exception('目录中缺少 "Materials" 文件夹。')
        materials_files = [f for f in os.listdir(materials_dir)]
        missing_outline_files = [file for file in self.CHECK_OUTLINE_LIST if not any(f.endswith(file) for f in materials_files)]
        if missing_outline_files:
            raise Exception(f'Materials 文件夹中缺少以下文件: {", ".join(missing_outline_files)}')

    def execute(self, context):
        if not self.directory:
            return {'CANCELLED'}
        try:
            self.validate_path(self.directory)
            context.scene.material_directory = self.directory
            self.report({'INFO'}, f'材质目录设置为: {context.scene.material_directory}')
            bpy.context.area.tag_redraw()
        except Exception as e:
            self.report({'ERROR'}, f'{str(e)}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BOBH_OT_apply_shader_to_mmd_model(bpy.types.Operator):
    bl_label = '将Shader材质应用到角色'
    bl_idname = 'bobh.apply_shader_to_mmd_model'

    def find_mmd_root_object(self, obj: bpy.types.Object):
        while obj is not None and obj.mmd_type != 'ROOT':
            obj = obj.parent
        return obj

    def guard_shader_exist(self):
        imported_mat_name = [
            'GI_Body',
            'GI_Face',
            'GI_Hair',
            'GI_Outlines'
        ]
        for checking_name in imported_mat_name:
            if checking_name not in bpy.data.materials:
                return False
        return True
        


    def copy_meterial_for_character(self, model_name):
        meterial_name_map = {
            'Body_Mat_Name': f'GI_{model_name}_Body',
            'Hair_Mat_Name': f'GI_{model_name}_Hair',
            'Face_Mat_Name': f'GI_{model_name}_Face',
            'Face_Outline_Mat_Name': f'GI_{model_name}_Face_Outline',
            'Hair_Outline_Mat_Name': f'GI_{model_name}_Hair_Outline',
            'Body_Outline_Mat_Name': f'GI_{model_name}_Body_Outline',
        }
        if self.guard_shader_exist() == False:
            raise Exception('请先导入shader预设')
        
        # Body mat
        ref_material = bpy.data.materials['GI_Body']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Body_Mat_Name']

        # Hair mat
        ref_material = bpy.data.materials['GI_Hair']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Hair_Mat_Name']

        # Face mat
        ref_material = bpy.data.materials['GI_Face']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Face_Mat_Name']

        # Outline mat
        ref_material = bpy.data.materials['GI_Outlines']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Face_Outline_Mat_Name']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Hair_Outline_Mat_Name']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Body_Outline_Mat_Name']
    
    def read_character_outline_info(self, mat_directory):
        directory = os.path.join(mat_directory, 'Materials')
        body_json_path = None
        dress_json_path = None
        face_json_path = None
        hair_json_path = None

        def read_json_outlines(json_path):
            with open(json_path, 'r') as file:
                json_obj = json.load(file)
            return {
                'Color1': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor'],
                'Color2': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor2'],
                'Color3': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor3'],
                'Color4': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor4'],
                'Color5': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor5'],
            }

        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if file.endswith('_Mat_Body.json'):
                body_json_path = full_path
            elif file.endswith('_Mat_Dress.json'):
                dress_json_path = full_path
            elif file.endswith('_Mat_Face.json'):
                face_json_path = full_path
            elif file.endswith('_Mat_Hair.json'):
                hair_json_path = full_path

        if (not body_json_path) or (not dress_json_path) or (not face_json_path) or (not hair_json_path):
            raise Exception('无法读取描边json材质')
        
        return {
            'BodyOutline': read_json_outlines(body_json_path),
            'DressOutline': read_json_outlines(dress_json_path),
            'FaceOutline': read_json_outlines(face_json_path),
            'HairOutline': read_json_outlines(hair_json_path),
        }
        


    def execute(self, context):
        select_obj = context.active_object
        mat_directory = context.scene.material_directory
        mmd_root_obj = self.find_mmd_root_object(select_obj)
        if not mmd_root_obj:
            self.report({'ERROR'}, f'请选中一个MMD模型角色')
            return {'CANCELLED'}
        
        if (not mat_directory) or (mat_directory == ''):
            self.report({'ERROR'}, f'请指定要导入角色的材质目录')
            return {'CANCELLED'}

        model_name = f'{mmd_root_obj.mmd_root.name}_{mmd_root_obj.mmd_root.name_e}_'

        try:
            self.copy_meterial_for_character(model_name)
            self._outline_info = self.read_character_outline_info(mat_directory)
        except Exception as e:
            self.report({'ERROR'}, f'{str(e)}')
            return {'CANCELLED'}

        self.report({'INFO'}, '应用材质到角色成功')
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BOBH_PT_main_panel)
    bpy.utils.register_class(BOBH_OT_import_shader)
    bpy.utils.register_class(BOBH_OT_set_character_material_directory)
    bpy.utils.register_class(BOBH_OT_apply_shader_to_mmd_model)
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
    del bpy.types.Scene.material_directory


if __name__ == '__main__':
    register()