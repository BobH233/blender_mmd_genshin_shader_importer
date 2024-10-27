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
        # print("previous: ", child_world_matrix)
        child_obj.parent = parent_obj
        child_obj.matrix_local = parent_obj.matrix_world.inverted() @ child_world_matrix
        # print("after: ", child_obj.matrix_world)
    
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
        
    def add_light_vector_geo_modifier(self, model_name, mesh_obj: bpy.types.Object):
        # Get or create geo_modifier
        geo_modifier: bpy.types.Modifier = None
        for mod in mesh_obj.modifiers:
            if mod.type == 'NODES' and mod.node_group and mod.node_group.name == "Light Vectors":
                geo_modifier = mod
                print('已经附加了LightVector属性, 直接修改即可')
                break
        if geo_modifier == None:
            geo_modifier = mesh_obj.modifiers.new(name='Light Vector Geo Modifier', type    = 'NODES')
            light_vector_node = bpy.data.node_groups.get("Light Vectors")
            if light_vector_node is None:
                raise BobHException('找不到LightVector节点, 是否忘记导入shader预设了?')
            geo_modifier.node_group = light_vector_node
        
        head_origin_obj = bpy.data.objects.get(f'{model_name}Head Origin')
        head_forward_obj = bpy.data.objects.get(f'{model_name}Head Forward')
        head_up_obj = bpy.data.objects.get(f'{model_name}Head Up')
        light_direction_obj = bpy.data.objects.get(f'{model_name}Light Direction')
        if head_origin_obj is None:
            raise BobHException('找不到HeadOrigin, 是否已经应用了材质?')
        if head_forward_obj is None:
            raise BobHException('找不到HeadForward, 是否已经应用了材质?')
        if head_up_obj is None:
            raise BobHException('找不到HeadUp, 是否已经应用了材质?')
        if light_direction_obj is None:
            raise BobHException('找不到LightDirection, 是否已经应用了材质?')
        geo_modifier['Input_3'] = light_direction_obj
        geo_modifier['Input_4'] = head_origin_obj
        geo_modifier['Input_5'] = head_forward_obj
        geo_modifier['Input_6'] = head_up_obj
        
    
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
            self.add_light_vector_geo_modifier(model_name, select_obj)
        except BobHException as e:
            self.report({'ERROR'}, f'{e}')
            return {'CANCELLED'}
        
        self.report({'INFO'}, '应用灯光和描边效果成功')
        return {'FINISHED'}