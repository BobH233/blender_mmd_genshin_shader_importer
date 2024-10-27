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

    OBJECT_LIST = [
        ('Light Direction', 'Light Direction Template'),
    ]

    NODE_GROUP_LIST = [
        ('Light Vectors', 'Light Vectors')
    ]

    def try_rename_node_group(self, filepath, group_name, import_name):
        # node_group_path = os.path.join(filepath, 'NodeTree', group_name)
        # bpy.ops.wm.append(
        #     filepath=node_group_path,
        #     directory=os.path.join(filepath, 'NodeTree'),
        #     filename=group_name
        # )
        if group_name in bpy.data.node_groups:
            imported_group = bpy.data.node_groups[group_name]
            imported_group.name = import_name
            return True
        else:
            raise BobHException(f'无法导入节点组{group_name}, 检查blend文件路径是否正确')

    def try_rename_material(self, filepath, origin_name, import_name):
        # material_path = material_path = os.path.join(filepath, 'NodeTree', 'Material', origin_name)
        # bpy.ops.wm.append(filepath=material_path, directory=os.path.join(self.filepath, 'Material'), filename=origin_name)
        if origin_name in bpy.data.materials:
            imported_material = bpy.data.materials[origin_name]
            imported_material.name = import_name
            return True
        else:
            raise BobHException(f'无法导入材质{origin_name}, 检查blend文件路径是否正确')
    
    def try_rename_and_hide_objects(self, filepath, origin_name, import_name, hide=True):
        # object_path = os.path.join(filepath, "Object", origin_name)
        # bpy.ops.wm.append(filepath=object_path, directory=os.path.join(self.filepath, 'Object'), filename=origin_name)
        if origin_name in bpy.data.objects:
            imported_object = bpy.data.objects[origin_name]
            imported_object.name = import_name
            imported_object.hide_viewport = hide
            imported_object.hide_render = hide
            imported_object.parent = None
            for collection in imported_object.users_collection:
                collection.objects.unlink(imported_object)
            bpy.context.scene.collection.objects.link(imported_object)
        else:
            raise BobHException(f'无法导入物体{origin_name}, 检查blend文件路径是否正确')

    def execute(self, context):
        if not self.filepath.endswith('.blend'):
            self.report({'ERROR'}, '请选择预设的.blend.文件')
            return {'CANCELLED'}
        
        try:
            with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
                desire_mat_name = [item[0] for item in self.MAT_LIST]
                desire_obj_name = [item[0] for item in self.OBJECT_LIST]
                desire_ng_name = [item[0] for item in self.NODE_GROUP_LIST]
                target_mat = []
                target_obj = []
                target_ng = []
                for src_mat in data_from.materials:
                    if src_mat in desire_mat_name:
                        print(f"importing mat: {src_mat}")
                        target_mat.append(src_mat)
                for src_obj in data_from.objects:
                    if src_obj in desire_obj_name:
                        print(f"importing obj: {src_obj}")
                        target_obj.append(src_obj)
                for src_ng in data_from.node_groups:
                    if src_ng in desire_ng_name:
                        print(f"importing node_group: {src_ng}")
                        target_ng.append(src_ng)
                data_to.materials = target_mat
                data_to.objects = target_obj
                data_to.node_groups = target_ng
            
            for mat_name, import_name in self.MAT_LIST:
                self.try_rename_material(self.filepath, mat_name, import_name)
            for obj_name, import_name in self.OBJECT_LIST:
                self.try_rename_and_hide_objects(self.filepath, obj_name, import_name)
            for ng_name, import_name in self.NODE_GROUP_LIST:
                self.try_rename_node_group(self.filepath, ng_name, import_name)
            
        except BobHException as e:
            self.report({'ERROR'}, f'{e}')
            return {'CANCELLED'}
        
        self.report({'INFO'}, '导入Shader预设成功')

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}