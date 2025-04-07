import bpy
import os
from ..bobh_exception import BobHException

class BOBH_OT_import_outline(bpy.types.Operator):
    bl_label = '导入描边节点'
    bl_idname = 'bobh.import_outline'

    def execute(self, context):
        # 获取插件目录路径
        addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        blend_path = os.path.join(addon_dir, "Data", "Genshin Impact Outlines v3.blend")
        
        if not os.path.exists(blend_path):
            self.report({'ERROR'}, f'找不到描边文件: {blend_path}')
            return {'CANCELLED'}
            
        try:
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                target_ng = []
                for src_ng in data_from.node_groups:
                    if src_ng == 'HoYoverse - Genshin Impact Outlines':
                        print(f'导入节点组: {src_ng}')
                        target_ng.append(src_ng)
                data_to.node_groups = target_ng
            
            # 重命名导入的节点组
            if 'HoYoverse - Genshin Impact Outlines' in bpy.data.node_groups:
                bpy.data.node_groups['HoYoverse - Genshin Impact Outlines'].name = 'GI_Outline'
                self.report({'INFO'}, '成功导入描边节点')
            else:
                raise BobHException('导入的blend文件中未找到描边节点组')
                
        except Exception as e:
            self.report({'ERROR'}, f'导入描边失败: {str(e)}')
            return {'CANCELLED'}
        
        return {'FINISHED'}

class BOBH_OT_apply_light_and_outline(bpy.types.Operator):
    bl_label = '将灯光和描边节点应用给模型'
    bl_idname = 'bobh.apply_light_and_outline'

    def find_mmd_root_object(self, obj: bpy.types.Object):
        while obj is not None and obj.mmd_type != 'ROOT':
            obj = obj.parent
        return obj

    def set_parent_keep_matrix_world(self, child_obj: bpy.types.Object, parent_obj: bpy.types.Object):
        child_world_matrix = child_obj.matrix_world.copy()
        child_obj.parent = parent_obj
        child_obj.matrix_local = parent_obj.matrix_world.inverted() @ child_world_matrix
    
    def set_head_empty_parent(self, model_name):
        head_origin_obj = bpy.data.objects.get(f'{model_name}Head Origin')
        head_forward_obj = bpy.data.objects.get(f'{model_name}Head Forward')
        head_up_obj = bpy.data.objects.get(f'{model_name}Head Up')
        
        if not all([head_origin_obj, head_forward_obj, head_up_obj]):
            raise BobHException('找不到头部控制空物体，请确保已应用材质')
        
        self.set_parent_keep_matrix_world(head_forward_obj, head_origin_obj)
        self.set_parent_keep_matrix_world(head_up_obj, head_origin_obj)

    def find_armature_in_child(self, root_obj):
        for child in root_obj.children:
            if child.type == 'ARMATURE':
                return child
            result = self.find_armature_in_child(child)
            if result:
                return result
        return None

    def constrain_head_origin_to_head_bone(self, mmd_root_obj, model_name):
        armature_obj = self.find_armature_in_child(mmd_root_obj)
        if armature_obj is None:
            raise BobHException('找不到当前角色的骨骼对象')
        
        head_bone_name = "頭"
        if head_bone_name not in armature_obj.data.bones:
            raise BobHException('找不到当前角色的头部骨骼')
            
        head_origin_obj = bpy.data.objects.get(f'{model_name}Head Origin')
        if head_origin_obj is None:
            raise BobHException('找不到HeadOrigin空物体')
            
        constraint = head_origin_obj.constraints.new(type='CHILD_OF')
        constraint.target = armature_obj
        constraint.subtarget = head_bone_name
        constraint.use_scale_x = False
        constraint.use_scale_y = False
        constraint.use_scale_z = False
        
    def add_light_vector_geo_modifier(self, model_name, mesh_obj: bpy.types.Object):
        geo_modifier = next(
            (mod for mod in mesh_obj.modifiers 
             if mod.type == 'NODES' and mod.node_group and mod.node_group.name == 'Light Vectors'),
            None
        )
        
        if not geo_modifier:
            geo_modifier = mesh_obj.modifiers.new(name='Light Vector Geo Modifier', type='NODES')
            light_vector_node = bpy.data.node_groups.get('Light Vectors')
            if light_vector_node is None:
                raise BobHException('找不到LightVector节点组，请先导入shader预设')
            geo_modifier.node_group = light_vector_node
        
        # 设置输入参数
        required_objects = {
            'Input_3': f'{model_name}Light Direction',
            'Input_4': f'{model_name}Head Origin',
            'Input_5': f'{model_name}Head Forward',
            'Input_6': f'{model_name}Head Up'
        }
        
        for input_key, obj_name in required_objects.items():
            obj = bpy.data.objects.get(obj_name)
            if obj is None:
                raise BobHException(f'找不到{obj_name}空物体')
            geo_modifier[input_key] = obj
        
    def add_outline_geo_modifier(self, model_name, mesh_obj: bpy.types.Object):
        # 首先检查是否已导入outline节点组
        outline_node = bpy.data.node_groups.get('GI_Outline')
        
        # 如果未找到，尝试自动导入
        if outline_node is None:
            # 获取插件目录路径
            addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            blend_path = os.path.join(addon_dir, "Data", "Genshin Impact Outlines v3.blend")
            
            if not os.path.exists(blend_path):
                raise BobHException(f'找不到描边文件: {blend_path}')
                
            try:
                with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                    target_ng = []
                    for src_ng in data_from.node_groups:
                        if src_ng == 'HoYoverse - Genshin Impact Outlines':
                            target_ng.append(src_ng)
                    data_to.node_groups = target_ng
                
                # 重命名导入的节点组
                if 'HoYoverse - Genshin Impact Outlines' in bpy.data.node_groups:
                    bpy.data.node_groups['HoYoverse - Genshin Impact Outlines'].name = 'GI_Outline'
                    outline_node = bpy.data.node_groups.get('GI_Outline')
                else:
                    raise BobHException('导入的blend文件中未找到描边节点组')
                    
            except Exception as e:
                raise BobHException(f'导入描边失败: {str(e)}')
        
        # 查找或创建几何节点修改器
        geo_modifier = next(
            (mod for mod in mesh_obj.modifiers 
             if mod.type == 'NODES' and mod.node_group and mod.node_group.name == 'GI_Outline'),
            None
        )
            
        if not geo_modifier:
            geo_modifier = mesh_obj.modifiers.new(name='Outline Geo Modifier', type='NODES')
            geo_modifier.node_group = outline_node
        
        # 设置材质输入
        material_inputs = {
            'Input_10': f'GI_{model_name}_Hair',
            'Input_5': f'GI_{model_name}_Hair_Outline',
            'Input_11': f'GI_{model_name}_Body',
            'Input_9': f'GI_{model_name}_Body_Outline',
            'Input_14': f'GI_{model_name}_Face',
            'Input_15': f'GI_{model_name}_Face_Outline'
        }
        
        for input_key, mat_name in material_inputs.items():
            mat = bpy.data.materials.get(mat_name)
            if mat is None:
                raise BobHException(f'找不到材质: {mat_name}')
            geo_modifier[input_key] = mat
        
        # 设置其他参数
        geo_modifier['Input_7'] = 1.0  # 描边宽度
        geo_modifier['Input_12'] = True  # Base Geometry
        
    def execute(self, context):
        select_obj = context.active_object
        if select_obj is None or select_obj.type != 'MESH':
            self.report({'ERROR'}, '请选中一个MMD模型角色的mesh对象')
            return {'CANCELLED'}
        
        mmd_root_obj = self.find_mmd_root_object(select_obj)
        if not mmd_root_obj:
            self.report({'ERROR'}, '请选中一个MMD模型角色')
            return {'CANCELLED'}
            
        model_name = f'{mmd_root_obj.mmd_root.name}_{mmd_root_obj.mmd_root.name_e}_'

        try:
            self.set_head_empty_parent(model_name)
            self.constrain_head_origin_to_head_bone(mmd_root_obj, model_name)
            self.add_light_vector_geo_modifier(model_name, select_obj)
            self.add_outline_geo_modifier(model_name, select_obj)
        except BobHException as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f'应用灯光和描边时发生错误: {str(e)}')
            return {'CANCELLED'}
        
        self.report({'INFO'}, '成功应用灯光和描边效果')
        return {'FINISHED'}