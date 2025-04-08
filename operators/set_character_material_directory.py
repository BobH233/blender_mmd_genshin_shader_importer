import bpy
import os
from ..bobh_exception import BobHException


class BOBH_OT_set_character_material_directory(bpy.types.Operator):
    bl_label = '选择角色解包材质目录'
    bl_idname = 'bobh.set_material_directory'
    directory: bpy.props.StringProperty(subtype='DIR_PATH') # type: ignore

    # 必需的材质文件列表
    REQUIRED_MAT_FILES = [
        '_Tex_Body_Diffuse.png',
        '_Tex_Body_Lightmap.png',
        '_Tex_Body_Shadow_Ramp.png',
        '_Face_Diffuse.png',
        '_Hair_Diffuse.png',
        '_Hair_Lightmap.png',
        '_Hair_Shadow_Ramp.png',
    ]

    # 必需的描边文件列表
    REQUIRED_OUTLINE_FILES = [
        '_Mat_Body.json',
        '_Mat_Face.json',
        '_Mat_Hair.json',
    ]

    # 可选的描边文件列表（_Mat_Dress.json和_Mat_Leather.json作用相同，任选其一即可）
    OPTIONAL_OUTLINE_FILES = [
        '_Mat_Dress.json',
        '_Mat_Leather.json',
    ]

    def validate_path(self, path):
        """验证材质目录结构"""
        # 检查主目录下的PNG文件
        png_files = [f for f in os.listdir(path) if f.endswith('.png')]
        missing_mat_files = [file for file in self.REQUIRED_MAT_FILES 
                           if not any(f.endswith(file) for f in png_files)]
        if missing_mat_files:
            raise BobHException(f'目录缺少以下必需的材质文件: {", ".join(missing_mat_files)}')

        # 检查Materials子目录
        materials_dir = os.path.join(path, 'Materials')
        if not os.path.isdir(materials_dir):
            raise BobHException('目录中缺少 "Materials" 文件夹')

        # 检查必需的描边文件
        materials_files = [f for f in os.listdir(materials_dir)]
        missing_required_outline = [file for file in self.REQUIRED_OUTLINE_FILES 
                                  if not any(f.endswith(file) for f in materials_files)]
        if missing_required_outline:
            raise BobHException(f'Materials 文件夹中缺少以下必需文件: {", ".join(missing_required_outline)}')

        # 检查可选的描边文件（至少存在其中一个即可）
        has_optional_outline = any(
            any(f.endswith(file) for f in materials_files)
            for file in self.OPTIONAL_OUTLINE_FILES
        )
        if not has_optional_outline:
            self.report({'WARNING'}, f'Materials 文件夹中缺少以下可选文件(任选其一即可): {", ".join(self.OPTIONAL_OUTLINE_FILES)}')

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
