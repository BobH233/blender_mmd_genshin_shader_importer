import bpy
import os
from ..bobh_exception import BobHException

class BOBH_OT_import_outline(bpy.types.Operator):
    bl_label = '选择Outline的.blend文件'
    bl_idname = 'bobh.import_outline'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH') # type: ignore


    def append_group_node_group(self, filepath, group_name, import_name):
        node_group_path = os.path.join(filepath, 'NodeTree', group_name)
        bpy.ops.wm.append(
            filepath=node_group_path,
            directory=os.path.join(filepath, 'NodeTree'),
            filename=group_name
        )
        if group_name in bpy.data.node_groups:
            imported_group = bpy.data.node_groups[group_name]
            imported_group.name = import_name
            return True
        else:
            raise BobHException(f'无法导入节点组{group_name}, 检查blend文件路径是否正确')


    def execute(self, context):
        if not self.filepath.endswith('.blend'):
            self.report({'ERROR'}, '请选择预设的.blend.文件')
            return {'CANCELLED'}
        
        try:
            self.append_group_node_group(self.filepath, 'HoYoverse - Genshin Impact Outlines', 'GI_Outline')
        except BobHException as e:
            self.report({'ERROR'}, f'{e}')
            return {'CANCELLED'}
        
        self.report({'INFO'}, '成功导入outline节点')

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}