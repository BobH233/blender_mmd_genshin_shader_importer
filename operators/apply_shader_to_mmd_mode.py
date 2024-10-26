import bpy
import json
import os
from bpy.types import ShaderNodeTexImage, ShaderNodeGroup
from ..bobh_exception import BobHException

class BOBH_OT_apply_shader_to_mmd_model(bpy.types.Operator):
    bl_label = '将Shader材质应用到角色'
    bl_idname = 'bobh.apply_shader_to_mmd_model'

    def find_mmd_root_object(self, obj: bpy.types.Object):
        while obj is not None and obj.mmd_type != 'ROOT':
            obj = obj.parent
        return obj

    def guard_shader_exist(self):
        imported_mat_name = [
            'GI_Body',
            'GI_Face',
            'GI_Hair',
            'GI_Outlines'
        ]
        for checking_name in imported_mat_name:
            if checking_name not in bpy.data.materials:
                return False
        return True
        


    def copy_meterial_for_character(self, model_name):
        meterial_name_map = {
            'Body_Mat_Name': f'GI_{model_name}_Body',
            'Hair_Mat_Name': f'GI_{model_name}_Hair',
            'Face_Mat_Name': f'GI_{model_name}_Face',
            'Face_Outline_Mat_Name': f'GI_{model_name}_Face_Outline',
            'Hair_Outline_Mat_Name': f'GI_{model_name}_Hair_Outline',
            'Body_Outline_Mat_Name': f'GI_{model_name}_Body_Outline',
        }
        if self.guard_shader_exist() == False:
            raise BobHException('请先导入shader预设')
        
        # Body mat
        ref_material = bpy.data.materials['GI_Body']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Body_Mat_Name']

        # Hair mat
        ref_material = bpy.data.materials['GI_Hair']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Hair_Mat_Name']

        # Face mat
        ref_material = bpy.data.materials['GI_Face']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Face_Mat_Name']

        # Outline mat
        ref_material = bpy.data.materials['GI_Outlines']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Face_Outline_Mat_Name']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Hair_Outline_Mat_Name']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Body_Outline_Mat_Name']

        return meterial_name_map
    
    def read_character_outline_info(self, mat_directory):
        directory = os.path.join(mat_directory, 'Materials')
        body_json_path = None
        dress_json_path = None
        face_json_path = None
        hair_json_path = None

        def read_json_outlines(json_path):
            with open(json_path, 'r') as file:
                json_obj = json.load(file)
            return {
                'Color1': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor'],
                'Color2': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor2'],
                'Color3': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor3'],
                'Color4': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor4'],
                'Color5': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor5'],
            }

        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if file.endswith('_Mat_Body.json'):
                body_json_path = full_path
            elif file.endswith('_Mat_Dress.json'):
                dress_json_path = full_path
            elif file.endswith('_Mat_Face.json'):
                face_json_path = full_path
            elif file.endswith('_Mat_Hair.json'):
                hair_json_path = full_path

        if (not body_json_path) or (not dress_json_path) or (not face_json_path) or (not hair_json_path):
            raise BobHException('无法读取描边json材质')
        
        return {
            'BodyOutline': read_json_outlines(body_json_path),
            'DressOutline': read_json_outlines(dress_json_path),
            'FaceOutline': read_json_outlines(face_json_path),
            'HairOutline': read_json_outlines(hair_json_path),
        }
        
    def find_texture_file_path(self, end_with, mat_directory):
        for f in os.listdir(mat_directory):
            if f.endswith(end_with):
                return os.path.join(mat_directory, f)
        return ''

    def find_material_node(self, node_name, nodes):
        for node in nodes:
            if node.name == node_name:
                return node
        return None

    def apply_texture_to_material(self, mat_directory):
        # >>> tmp texture node definition <<<
        diffuse_texture_node: ShaderNodeTexImage = None
        diffuse1_texture_node: ShaderNodeTexImage = None
        lightmap_texture_node: ShaderNodeTexImage = None
        lightmap1_texture_node: ShaderNodeTexImage = None
        shadowramp_texture_node: ShaderNodeTexImage = None
        shadowramp_group_node: ShaderNodeGroup = None

        # >>> Face material <<<
        face_mat_name = self._meterial_name_map['Face_Mat_Name']
        face_mat = bpy.data.materials[face_mat_name]
        assert face_mat.use_nodes, '材质节点一定使用了节点'
        # find diffuse node
        diffuse_texture_node = self.find_material_node('Face_Diffuse', face_mat.node_tree.nodes)
        assert diffuse_texture_node is not None, '找不到Diffuse节点'
        # setup face diffuse node
        face_diffuse_file = self.find_texture_file_path('_Face_Diffuse.png', mat_directory)
        assert face_diffuse_file != '', '找不到脸部Diffuse贴图文件'
        image_data = bpy.data.images.load(face_diffuse_file)
        diffuse_texture_node.image = image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'

        # >>> Hair material <<<
        hair_mat_name = self._meterial_name_map['Hair_Mat_Name']
        hair_mat = bpy.data.materials[hair_mat_name]
        assert hair_mat.use_nodes, '材质节点一定使用了节点'
        hair_diffuse_file = self.find_texture_file_path('_Hair_Diffuse.png', mat_directory)
        hair_lightmap_file = self.find_texture_file_path('_Hair_Lightmap.png', mat_directory)
        hair_shadowramp_file = self.find_texture_file_path('_Hair_Shadow_Ramp.png', mat_directory)
        assert hair_diffuse_file != '', '找不到头发Diffuse贴图文件'
        assert hair_lightmap_file != '', '找不到头发Lightmap贴图文件'
        assert hair_shadowramp_file != '', '找不到头发Shadowramp贴图文件'
        diffuse_texture_node = self.find_material_node('Hair_Diffuse_UV0', hair_mat.node_tree.nodes)
        diffuse1_texture_node = self.find_material_node('Hair_Diffuse_UV1', hair_mat.node_tree.nodes)
        lightmap_texture_node = self.find_material_node('Hair_Lightmap_UV0', hair_mat.node_tree.nodes)
        lightmap1_texture_node = self.find_material_node('Hair_Lightmap_UV1', hair_mat.node_tree.nodes)
        shadowramp_group_node = self.find_material_node('Shadow Ramp', hair_mat.node_tree.nodes)
        assert shadowramp_group_node is not None, '找不到Shadowramp组'
        shadowramp_texture_node = self.find_material_node('Hair_Shadow_Ramp', shadowramp_group_node.node_tree.nodes)
        assert diffuse_texture_node is not None, '找不到DiffuseUV0节点'
        assert diffuse1_texture_node is not None, '找不到DiffuseUV1节点'
        assert lightmap_texture_node is not None, '找不到LightmapUV0节点'
        assert lightmap1_texture_node is not None, '找不到LightmapUV1节点'
        assert shadowramp_texture_node is not None, '找不到Shadowramp节点'
        image_data = bpy.data.images.load(hair_diffuse_file)
        diffuse_texture_node.image = image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        diffuse1_texture_node.image = image_data
        diffuse1_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse1_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        image_data = bpy.data.images.load(hair_lightmap_file)
        lightmap_texture_node.image = image_data
        lightmap_texture_node.image.colorspace_settings.name = 'Non-Color'
        lightmap_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        lightmap1_texture_node.image = image_data
        lightmap1_texture_node.image.colorspace_settings.name = 'Non-Color'
        lightmap1_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        image_data = bpy.data.images.load(hair_shadowramp_file)
        shadowramp_texture_node.image = image_data
        shadowramp_texture_node.image.colorspace_settings.name = 'sRGB'
        shadowramp_texture_node.image.alpha_mode = 'CHANNEL_PACKED'

        # >>> Body material <<<
        body_mat_name = self._meterial_name_map['Body_Mat_Name']
        body_mat = bpy.data.materials[body_mat_name]
        assert body_mat.use_nodes, '材质节点一定使用了节点'
        body_diffuse_file = self.find_texture_file_path('_Body_Diffuse.png', mat_directory)
        body_lightmap_file = self.find_texture_file_path('_Body_Lightmap.png', mat_directory)
        body_shadowramp_file = self.find_texture_file_path('_Body_Shadow_Ramp.png', mat_directory)
        assert body_diffuse_file != '', '找不到身体Diffuse贴图文件'
        assert body_lightmap_file != '', '找不到身体Lightmap贴图文件'
        assert body_shadowramp_file != '', '找不到身体Shadowramp贴图文件'
        diffuse_texture_node = self.find_material_node('Body_Diffuse_UV0', body_mat.node_tree.nodes)
        diffuse1_texture_node = self.find_material_node('Body_Diffuse_UV1', body_mat.node_tree.nodes)
        lightmap_texture_node = self.find_material_node('Body_Lightmap_UV0', body_mat.node_tree.nodes)
        lightmap1_texture_node = self.find_material_node('Body_Lightmap_UV1', body_mat.node_tree.nodes)
        shadowramp_group_node = self.find_material_node('Shadow Ramp', body_mat.node_tree.nodes)
        assert shadowramp_group_node is not None, '找不到Shadowramp组'
        shadowramp_texture_node = self.find_material_node('Body_Shadow_Ramp', shadowramp_group_node.node_tree.nodes)
        assert diffuse_texture_node is not None, '找不到DiffuseUV0节点'
        assert diffuse1_texture_node is not None, '找不到DiffuseUV1节点'
        assert lightmap_texture_node is not None, '找不到LightmapUV0节点'
        assert lightmap1_texture_node is not None, '找不到LightmapUV1节点'
        assert shadowramp_texture_node is not None, '找不到Shadowramp节点'
        image_data = bpy.data.images.load(body_diffuse_file)
        diffuse_texture_node.image = image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        diffuse1_texture_node.image = image_data
        diffuse1_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse1_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        image_data = bpy.data.images.load(body_lightmap_file)
        lightmap_texture_node.image = image_data
        lightmap_texture_node.image.colorspace_settings.name = 'Non-Color'
        lightmap_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        lightmap1_texture_node.image = image_data
        lightmap1_texture_node.image.colorspace_settings.name = 'Non-Color'
        lightmap1_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        image_data = bpy.data.images.load(body_shadowramp_file)
        shadowramp_texture_node.image = image_data
        shadowramp_texture_node.image.colorspace_settings.name = 'sRGB'
        shadowramp_texture_node.image.alpha_mode = 'CHANNEL_PACKED'



    def execute(self, context):
        select_obj = context.active_object
        mat_directory = context.scene.material_directory
        mmd_root_obj = self.find_mmd_root_object(select_obj)
        if not mmd_root_obj:
            self.report({'ERROR'}, f'请选中一个MMD模型角色')
            return {'CANCELLED'}
        
        if (not mat_directory) or (mat_directory == ''):
            self.report({'ERROR'}, f'请指定要导入角色的材质目录')
            return {'CANCELLED'}

        model_name = f'{mmd_root_obj.mmd_root.name}_{mmd_root_obj.mmd_root.name_e}_'

        try:
            self._meterial_name_map = self.copy_meterial_for_character(model_name)
            self._outline_info = self.read_character_outline_info(mat_directory)
            self.apply_texture_to_material(mat_directory)
        except BobHException as e:
            self.report({'ERROR'}, f'{e}')
            return {'CANCELLED'}

        self.report({'INFO'}, '应用材质到角色成功')
        return {'FINISHED'}