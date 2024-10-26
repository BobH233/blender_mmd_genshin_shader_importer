import bpy
import os
from ..bobh_exception import BobHException


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
        '_Mat_Dress.json',
    ]

    def validate_path(self, path):
        png_files = [f for f in os.listdir(path) if f.endswith('.png')]
        missing_mat_files = [file for file in self.CHECK_MAT_LIST if not any(f.endswith(file) for f in png_files)]
        if missing_mat_files:
            raise BobHException(f'目录缺少以下所需的材质文件: {", ".join(missing_mat_files)}')
        materials_dir = os.path.join(path, 'Materials')
        if not os.path.isdir(materials_dir):
            raise BobHException('目录中缺少 "Materials" 文件夹。')
        materials_files = [f for f in os.listdir(materials_dir)]
        missing_outline_files = [file for file in self.CHECK_OUTLINE_LIST if not any(f.endswith(file) for f in materials_files)]
        if missing_outline_files:
            raise BobHException(f'Materials 文件夹中缺少以下文件: {", ".join(missing_outline_files)}')

    def execute(self, context):
        if not self.directory:
            return {'CANCELLED'}
        try:
            self.validate_path(self.directory)
            context.scene.material_directory = self.directory
            self.report({'INFO'}, f'材质目录设置为: {context.scene.material_directory}')
            bpy.context.area.tag_redraw()
        except BobHException as e:
            self.report({'ERROR'}, f'{e}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}