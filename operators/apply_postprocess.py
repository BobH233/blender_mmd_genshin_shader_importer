import bpy
import os
from bpy.types import ShaderNodeTexImage, ShaderNodeGroup
from ..bobh_exception import BobHException

class BOBH_OT_apply_postprocess(bpy.types.Operator):
    bl_label = '应用后处理'
    bl_idname = 'bobh.apply_postprocess'
    
    def try_rename_node_group(self, filepath, group_name, import_name):
        if group_name in bpy.data.node_groups:
            imported_group = bpy.data.node_groups[group_name]
            imported_group.name = import_name
            return True
        else:
            raise BobHException(f'无法导入节点组{group_name}, 检查blend文件路径是否正确')

    def apply_postprocess_node(self, context: bpy.types.Context):
        if not context.scene.use_nodes:
            context.scene.use_nodes = True
        postprocessing_node = bpy.data.node_groups.get('GI_PostProcessing')
        assert postprocessing_node is not None, '找不到 postprocessing节点'
        node_tree = context.scene.node_tree
        group_node = node_tree.nodes.new('CompositorNodeGroup')
        group_node.node_tree = postprocessing_node
        group_node.location = (200, 200)
        input_node = next((node for node in node_tree.nodes if node.type == "R_LAYERS"), None)
        output_node = next((node for node in node_tree.nodes if node.type == "COMPOSITE"), None)
        if not input_node:
            input_node = node_tree.nodes.new("CompositorNodeRLayers")
            input_node.location = (-400, 0)
            
        if not output_node:
            output_node = node_tree.nodes.new("CompositorNodeComposite")
            output_node.location = (600, 0)
            
        node_tree.links.new(input_node.outputs["Image"], group_node.inputs[0])
        node_tree.links.new(group_node.outputs[0], output_node.inputs["Image"])

    def execute(self, context):
        # 获取插件目录路径
        addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        blend_path = os.path.join(addon_dir, "Data", "Genshin Impact Post-Processing.blend")
        
        if not os.path.exists(blend_path):
            self.report({'ERROR'}, f'找不到后处理文件: {blend_path}')
            return {'CANCELLED'}
            
        try:
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                target_ng = []
                for src_ng in data_from.node_groups:
                    if src_ng == 'HoYoverse - Post Processing':
                        print(f'importing node_group: {src_ng}')
                        target_ng.append(src_ng)
                data_to.node_groups = target_ng
            self.try_rename_node_group(blend_path, 'HoYoverse - Post Processing', 'GI_PostProcessing')
            self.apply_postprocess_node(context)
        except BobHException as e:
            self.report({'ERROR'}, f'{e}')
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f'导入后处理失败: {str(e)}')
            return {'CANCELLED'}
        
        self.report({'INFO'}, '成功导入后处理节点')
        return {'FINISHED'}