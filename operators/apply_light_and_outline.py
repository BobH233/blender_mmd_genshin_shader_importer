import bpy
from bpy.types import ShaderNodeTexImage, ShaderNodeGroup
from ..bobh_exception import BobHException

class BOBH_OT_apply_light_and_outline(bpy.types.Operator):
    bl_label = '将灯光和描边节点应用给模型'
    bl_idname = 'bobh.apply_light_and_outline'

    def find_mmd_root_object(self, obj: bpy.types.Object):
        while obj is not None and obj.mmd_type != 'ROOT':
            obj = obj.parent
        return obj

    '''设置物体的父物体，同时不改变子物体原本的位置'''
    def set_parent_keep_matrix_world(self, child_obj: bpy.types.Object, parent_obj: bpy.types.Object):
        child_world_matrix = child_obj.matrix_world.copy()
        print("previous: ", child_world_matrix)
        child_obj.parent = parent_obj
        child_obj.matrix_local = parent_obj.matrix_world.inverted() @ child_world_matrix
        print("after: ", child_obj.matrix_world)
    
    def set_head_empty_parent(self, model_name):
        head_origin_obj = bpy.data.objects.get(f'{model_name}Head Origin')
        head_forward_obj = bpy.data.objects.get(f'{model_name}Head Forward')
        head_up_obj = bpy.data.objects.get(f'{model_name}Head Up')
        
        if head_origin_obj is None:
            raise BobHException('找不到HeadOrigin, 是否已经应用了材质?')
        if head_forward_obj is None:
            raise BobHException('找不到HeadForward, 是否已经应用了材质?')
        if head_up_obj is None:
            raise BobHException('找不到HeadUp, 是否已经应用了材质?')
        
        self.set_parent_keep_matrix_world(head_forward_obj, head_origin_obj)
        self.set_parent_keep_matrix_world(head_up_obj, head_origin_obj)
        
        
    
    def execute(self, context):
        select_obj = context.active_object
        if select_obj.type != 'MESH':
            self.report({'ERROR'}, f'请选中一个MMD模型角色的mesh')
            return {'CANCELLED'}
        
        mmd_root_obj = self.find_mmd_root_object(select_obj)
        if not mmd_root_obj:
            self.report({'ERROR'}, f'请选中一个MMD模型角色')
            return {'CANCELLED'}
        model_name = f'{mmd_root_obj.mmd_root.name}_{mmd_root_obj.mmd_root.name_e}_'

        try:
            self.set_head_empty_parent(model_name)
        except BobHException as e:
            self.report({'ERROR'}, f'{e}')
            return {'CANCELLED'}