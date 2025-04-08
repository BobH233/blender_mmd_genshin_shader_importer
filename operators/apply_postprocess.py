import bpy
import os
from bpy.types import ShaderNodeTexImage, ShaderNodeGroup
from ..bobh_exception import BobHException


class BOBH_OT_apply_postprocess(bpy.types.Operator):
    bl_label = '应用后处理'
    bl_idname = 'bobh.apply_postprocess'
    
    def try_rename_node_group(self, filepath, group_name, import_name):
        """安全重命名节点组"""
        if group_name not in bpy.data.node_groups:
            raise BobHException(f'节点组"{group_name}"不存在于文件中')
        bpy.data.node_groups[group_name].name = import_name
        return True

    def setup_compositor_nodes(self, context):
        """设置合成器节点连接"""
        scene = context.scene
        if not scene.use_nodes:
            scene.use_nodes = True
            
        tree = scene.node_tree
        if tree is None:
            raise BobHException('无法获取场景节点树')

        # 清除现有节点和连接
        tree.nodes.clear()

        # 创建标准节点布局
        render_node = tree.nodes.new('CompositorNodeRLayers')
        render_node.location = (-400, 0)
        
        post_group = bpy.data.node_groups.get('GI_PostProcessing')
        if not post_group:
            raise BobHException('后处理节点组未加载')

        group_node = tree.nodes.new('CompositorNodeGroup')
        group_node.node_tree = post_group
        group_node.location = (0, 0)

        # 严格按照API创建合成节点
        comp_node = tree.nodes.new('CompositorNodeComposite')
        comp_node.location = (400, 0)
        comp_node.use_alpha = False  # 根据API文档设置默认值

        # 确保使用正确的socket名称连接
        try:
            # 渲染层 -> 后处理
            tree.links.new(
                render_node.outputs.get('Image'),
                group_node.inputs.get('Image') or group_node.inputs[0]
            )
            
            # 后处理 -> 合成
            tree.links.new(
                group_node.outputs.get('Image') or group_node.outputs[0],
                comp_node.inputs.get('Image')
            )
        except Exception as e:
            raise BobHException(f'节点连接失败: {str(e)}')

    def execute(self, context):
        """主执行函数"""
        addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        blend_path = os.path.join(addon_dir, "Data", "Genshin Impact Post-Processing.blend")
        
        if not os.path.exists(blend_path):
            self.report({'ERROR'}, f'文件不存在: {blend_path}')
            return {'CANCELLED'}
            
        try:
            # 导入节点组
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                if 'HoYoverse - Post Processing' not in data_from.node_groups:
                    raise BobHException('目标节点组不在文件中')
                data_to.node_groups = ['HoYoverse - Post Processing']

            # 重命名并设置
            self.try_rename_node_group(blend_path, 'HoYoverse - Post Processing', 'GI_PostProcessing')
            self.setup_compositor_nodes(context)

        except BobHException as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f'操作失败: {str(e)}')
            return {'CANCELLED'}
        
        self.report({'INFO'}, '后处理应用成功')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BOBH_OT_apply_postprocess)


def unregister():
    bpy.utils.unregister_class(BOBH_OT_apply_postprocess)
