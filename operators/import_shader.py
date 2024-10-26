import bpy
import os
from ..bobh_exception import BobHException

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
            raise BobHException(f'无法导入材质{origin_name}, 检查blend文件路径是否正确')

    def execute(self, context):
        if not self.filepath.endswith('.blend'):
            self.report({'ERROR'}, '请选择预设的.blend.文件')
            return {'CANCELLED'}
        
        try:
            for mat_name, import_name in self.MAT_LIST:
                self.try_import_material(self.filepath, mat_name, import_name)
        except BobHException as e:
            self.report({'ERROR'}, f'{e}')
            return {'CANCELLED'}
        
        self.report({'INFO'}, '导入Shader预设成功')

        return {'FINISHED'}

    def invoke(self, context, event):
        self.bl_label = 'Select .blend'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}