import bpy
import os
import json
from ..bobh_exception import BobHException

class BOBH_OT_apply_shader_to_mmd_model(bpy.types.Operator):
    bl_label = '将Shader材质应用到角色'
    bl_idname = 'bobh.apply_shader_to_mmd_model'

    # 定义需要导入的资源列表
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

    def try_rename_node_group(self, group_name, import_name):
        if group_name in bpy.data.node_groups:
            imported_group = bpy.data.node_groups[group_name]
            imported_group.name = import_name
            imported_group.use_fake_user = True  # 防止被自动清理
            return True
        else:
            raise BobHException(f'无法导入节点组{group_name}, 检查blend文件路径是否正确')

    def try_rename_material(self, origin_name, import_name):
        if origin_name in bpy.data.materials:
            imported_material = bpy.data.materials[origin_name]
            imported_material.name = import_name
            imported_material.use_fake_user = True  # 防止被自动清理
            return True
        else:
            raise BobHException(f'无法导入材质{origin_name}, 检查blend文件路径是否正确')
    
    def try_rename_and_hide_objects(self, origin_name, import_name, hide=True):
        if origin_name in bpy.data.objects:
            imported_object = bpy.data.objects[origin_name]
            imported_object.name = import_name
            imported_object.hide_viewport = hide
            imported_object.hide_render = hide
            imported_object.parent = None
            for collection in imported_object.users_collection:
                collection.objects.unlink(imported_object)
            bpy.context.scene.collection.objects.link(imported_object)
            # 对象不需要fake user，因为会被场景引用
        else:
            raise BobHException(f'无法导入物体{origin_name}, 检查blend文件路径是否正确')

    def import_shader_preset(self):
        # 获取插件目录
        addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        blend_file = os.path.join(addon_dir, "Data", "Genshin Impact v3.4.blend")
        
        if not os.path.exists(blend_file):
            raise BobHException('Shader预设文件未找到，请检查插件安装是否完整')
        
        try:
            # 先检查是否已有预设资源，避免重复导入
            if self.guard_shader_exist():
                return
                
            # 导入blend文件中的资源
            with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
                # 准备要导入的资源名称列表
                desire_mat_name = [item[0] for item in self.MAT_LIST]
                desire_obj_name = [item[0] for item in self.OBJECT_LIST]
                desire_ng_name = [item[0] for item in self.NODE_GROUP_LIST]
                
                # 筛选出需要导入的资源
                data_to.materials = [name for name in data_from.materials if name in desire_mat_name]
                data_to.objects = [name for name in data_from.objects if name in desire_obj_name]
                data_to.node_groups = [name for name in data_from.node_groups if name in desire_ng_name]
            
            # 重命名导入的资源并设置保护
            for mat_name, import_name in self.MAT_LIST:
                self.try_rename_material(mat_name, import_name)
                
            for obj_name, import_name in self.OBJECT_LIST:
                self.try_rename_and_hide_objects(obj_name, import_name)
                
            for ng_name, import_name in self.NODE_GROUP_LIST:
                self.try_rename_node_group(ng_name, import_name)
            
            # 双重检查确保资源已正确导入
            if not self.guard_shader_exist():
                raise BobHException('Shader预设导入后验证失败')
            
        except Exception as e:
            raise BobHException(f'导入Shader预设时发生错误: {str(e)}')

    def find_mmd_root_object(self, obj: bpy.types.Object):
        while obj is not None and obj.mmd_type != 'ROOT':
            obj = obj.parent
        return obj

    def guard_shader_exist(self):
        # 检查所有必需的材质
        required_materials = ['GI_Body', 'GI_Face', 'GI_Hair', 'GI_Outlines']
        for mat_name in required_materials:
            mat = bpy.data.materials.get(mat_name)
            if not mat:
                return False
            # 确保材质不会被自动清理
            mat.use_fake_user = True
        
        # 检查必需的节点组
        required_node_groups = ['Light Vectors']
        for ng_name in required_node_groups:
            ng = bpy.data.node_groups.get(ng_name)
            if not ng:
                return False
            # 确保节点组不会被自动清理
            ng.use_fake_user = True
        
        # 检查必需的对象
        required_objects = ['Light Direction Template']
        for obj_name in required_objects:
            if obj_name not in bpy.data.objects:
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
        
        # 如果Shader预设不存在，则自动导入
        if not self.guard_shader_exist():
            self.import_shader_preset()
        
        # Body mat
        ref_material = bpy.data.materials['GI_Body']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Body_Mat_Name']
        char_material.use_fake_user = False  # 角色材质不需要fake user

        # Hair mat
        ref_material = bpy.data.materials['GI_Hair']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Hair_Mat_Name']
        char_material.use_fake_user = False

        # Face mat
        ref_material = bpy.data.materials['GI_Face']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Face_Mat_Name']
        char_material.use_fake_user = False

        # Outline mat
        ref_material = bpy.data.materials['GI_Outlines']
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Face_Outline_Mat_Name']
        char_material.use_fake_user = False
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Hair_Outline_Mat_Name']
        char_material.use_fake_user = False
        char_material = ref_material.copy()         
        char_material.name = meterial_name_map['Body_Outline_Mat_Name']
        char_material.use_fake_user = False

        return meterial_name_map
    
    def read_character_outline_info(self, mat_directory):
        directory = os.path.join(mat_directory, 'Materials')
        outline_info = {}
        
        # 必需的文件类型
        required_files = {
            'BodyOutline': '_Mat_Body.json',
            'FaceOutline': '_Mat_Face.json',
            'HairOutline': '_Mat_Hair.json'
        }
        
        # 可选的文件类型（_Mat_Dress.json 和 _Mat_Leather.json 是等效的）
        optional_files = {
            'DressOutline': ['_Mat_Dress.json', '_Mat_Leather.json']  # 修改为列表形式
        }

        # 处理必需文件
        for outline_type, file_suffix in required_files.items():
            file_path = None
            for file in os.listdir(directory):
                if file.endswith(file_suffix):
                    file_path = os.path.join(directory, file)
                    break
            
            if not file_path:
                raise BobHException(f'无法找到必需的描边文件: {file_suffix}')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_obj = json.load(file)
                outline_info[outline_type] = {
                    'Color1': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor'],
                    'Color2': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor2'],
                    'Color3': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor3'],
                    'Color4': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor4'],
                    'Color5': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor5'],
                }
            except Exception as e:
                raise BobHException(f'读取描边文件失败: {file_path} - {str(e)}')

        # 处理可选文件（现在检查多个可能的文件名）
        for outline_type, file_suffixes in optional_files.items():
            file_path = None
            found_file = None
            
            # 检查所有可能的文件名
            for suffix in file_suffixes:
                for file in os.listdir(directory):
                    if file.endswith(suffix):
                        file_path = os.path.join(directory, file)
                        found_file = file
                        break
                if file_path:
                    break
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        json_obj = json.load(file)
                    outline_info[outline_type] = {
                        'Color1': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor'],
                        'Color2': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor2'],
                        'Color3': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor3'],
                        'Color4': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor4'],
                        'Color5': json_obj['m_SavedProperties']['m_Colors']['_OutlineColor5'],
                    }
                    self.report({'INFO'}, f'使用描边文件: {found_file}')
                except Exception as e:
                    self.report({'INFO'}, f'读取可选描边文件失败: {found_file} - {str(e)}，将使用身体描边设置')
                    outline_info[outline_type] = outline_info['BodyOutline'].copy()
            else:
                self.report({'INFO'}, f'未找到可选描边文件(任何其一即可): {", ".join(file_suffixes)}，将使用身体描边设置')
                outline_info[outline_type] = outline_info['BodyOutline'].copy()
        
        return outline_info

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
        # Face material
        face_mat_name = self._meterial_name_map['Face_Mat_Name']
        face_mat = bpy.data.materials[face_mat_name]
        assert face_mat.use_nodes, '材质节点一定使用了节点'
        
        # Find and setup face diffuse node
        diffuse_texture_node = self.find_material_node('Face_Diffuse', face_mat.node_tree.nodes)
        assert diffuse_texture_node is not None, '找不到Diffuse节点'
        
        face_diffuse_file = self.find_texture_file_path('_Face_Diffuse.png', mat_directory)
        assert face_diffuse_file != '', '找不到脸部Diffuse贴图文件'
        
        image_data = bpy.data.images.load(face_diffuse_file)
        self._face_diffuse_image_data = image_data
        diffuse_texture_node.image = image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'

        # Hair material
        hair_mat_name = self._meterial_name_map['Hair_Mat_Name']
        hair_mat = bpy.data.materials[hair_mat_name]
        assert hair_mat.use_nodes, '材质节点一定使用了节点'
        
        hair_diffuse_file = self.find_texture_file_path('_Hair_Diffuse.png', mat_directory)
        hair_lightmap_file = self.find_texture_file_path('_Hair_Lightmap.png', mat_directory)
        hair_shadowramp_file = self.find_texture_file_path('_Hair_Shadow_Ramp.png', mat_directory)
        
        assert hair_diffuse_file != '', '找不到头发Diffuse贴图文件'
        assert hair_lightmap_file != '', '找不到头发Lightmap贴图文件'
        assert hair_shadowramp_file != '', '找不到头发Shadowramp贴图文件'
        
        diffuse_texture_node = self.find_material_node('Body_Diffuse_UV0', hair_mat.node_tree.nodes)
        lightmap_texture_node = self.find_material_node('Body_Lightmap_UV0', hair_mat.node_tree.nodes)
        shadowramp_group_node = self.find_material_node('Shadow Ramp', hair_mat.node_tree.nodes)
        
        assert shadowramp_group_node is not None, '找不到Shadowramp组'
        shadowramp_texture_node = self.find_material_node('Hair_Shadow_Ramp', shadowramp_group_node.node_tree.nodes)
        
        assert diffuse_texture_node is not None, '找不到DiffuseUV0节点'
        assert lightmap_texture_node is not None, '找不到LightmapUV0节点'
        assert shadowramp_texture_node is not None, '找不到Shadowramp节点'
        
        # Load hair diffuse
        image_data = bpy.data.images.load(hair_diffuse_file)
        self._hair_diffuse_image_data = image_data
        diffuse_texture_node.image = image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        # Load hair lightmap
        image_data = bpy.data.images.load(hair_lightmap_file)
        self._hair_lightmap_image_data = image_data
        lightmap_texture_node.image = image_data
        lightmap_texture_node.image.colorspace_settings.name = 'Non-Color'
        lightmap_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        # Load hair shadowramp
        image_data = bpy.data.images.load(hair_shadowramp_file)
        shadowramp_texture_node.image = image_data
        shadowramp_texture_node.image.colorspace_settings.name = 'sRGB'
        shadowramp_texture_node.image.alpha_mode = 'CHANNEL_PACKED'

        # Body material
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
        lightmap_texture_node = self.find_material_node('Body_Lightmap_UV0', body_mat.node_tree.nodes)
        shadowramp_group_node = self.find_material_node('Shadow Ramp', body_mat.node_tree.nodes)
        
        assert shadowramp_group_node is not None, '找不到Shadowramp组'
        shadowramp_texture_node = self.find_material_node('Body_Shadow_Ramp', shadowramp_group_node.node_tree.nodes)
        
        assert diffuse_texture_node is not None, '找不到DiffuseUV0节点'
        assert lightmap_texture_node is not None, '找不到LightmapUV0节点'
        assert shadowramp_texture_node is not None, '找不到Shadowramp节点'
        
        # Load body diffuse
        image_data = bpy.data.images.load(body_diffuse_file)
        self._body_diffuse_image_data = image_data
        diffuse_texture_node.image = image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        # Load body lightmap
        image_data = bpy.data.images.load(body_lightmap_file)
        self._body_lightmap_image_data = image_data
        lightmap_texture_node.image = image_data
        lightmap_texture_node.image.colorspace_settings.name = 'Non-Color'
        lightmap_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        # Load body shadowramp
        image_data = bpy.data.images.load(body_shadowramp_file)
        shadowramp_texture_node.image = image_data
        shadowramp_texture_node.image.colorspace_settings.name = 'sRGB'
        shadowramp_texture_node.image.alpha_mode = 'CHANNEL_PACKED'

    def apply_outline_color_to_material(self, mat_directory):
        # Face outlines
        face_outline_mat_name = self._meterial_name_map['Face_Outline_Mat_Name']
        face_outline_mat = bpy.data.materials[face_outline_mat_name]
        assert face_outline_mat.use_nodes
        
        diffuse_texture_node = self.find_material_node('Outline_Diffuse', face_outline_mat.node_tree.nodes)
        outline_group_node = self.find_material_node('Outlines', face_outline_mat.node_tree.nodes)
        
        assert diffuse_texture_node is not None, '找不到OutlineDiffuse节点'
        assert outline_group_node is not None, '找不到Outlines节点'
        
        diffuse_texture_node.image = self._face_diffuse_image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        for i in range(1, 6):
            color_input = outline_group_node.inputs[f'Outline Color {i}']
            outline_color_obj = self._outline_info['FaceOutline'][f'Color{i}']
            color_input.default_value = (
                outline_color_obj['r'],
                outline_color_obj['g'],
                outline_color_obj['b'],
                outline_color_obj['a']
            )

        # Hair outlines
        hair_outline_mat_name = self._meterial_name_map['Hair_Outline_Mat_Name']
        hair_outline_mat = bpy.data.materials[hair_outline_mat_name]
        assert hair_outline_mat.use_nodes
        
        diffuse_texture_node = self.find_material_node('Outline_Diffuse', hair_outline_mat.node_tree.nodes)
        lightmap_texture_node = self.find_material_node('Outline_Lightmap', hair_outline_mat.node_tree.nodes)
        outline_group_node = self.find_material_node('Outlines', hair_outline_mat.node_tree.nodes)
        
        assert diffuse_texture_node is not None, '找不到OutlineDiffuse节点'
        assert lightmap_texture_node is not None, '找不到OutlineLightmap节点'
        assert outline_group_node is not None, '找不到Outlines节点'
        
        diffuse_texture_node.image = self._hair_diffuse_image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        lightmap_texture_node.image = self._hair_lightmap_image_data
        lightmap_texture_node.image.colorspace_settings.name = 'Non-Color'
        lightmap_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        for i in range(1, 6):
            color_input = outline_group_node.inputs[f'Outline Color {i}']
            outline_color_obj = self._outline_info['HairOutline'][f'Color{i}']
            color_input.default_value = (
                outline_color_obj['r'],
                outline_color_obj['g'],
                outline_color_obj['b'],
                outline_color_obj['a']
            )

        # Body outlines
        body_outline_mat_name = self._meterial_name_map['Body_Outline_Mat_Name']
        body_outline_mat = bpy.data.materials[body_outline_mat_name]
        assert body_outline_mat.use_nodes
        
        diffuse_texture_node = self.find_material_node('Outline_Diffuse', body_outline_mat.node_tree.nodes)
        lightmap_texture_node = self.find_material_node('Outline_Lightmap', body_outline_mat.node_tree.nodes)
        outline_group_node = self.find_material_node('Outlines', body_outline_mat.node_tree.nodes)
        
        assert diffuse_texture_node is not None, '找不到OutlineDiffuse节点'
        assert lightmap_texture_node is not None, '找不到OutlineLightmap节点'
        assert outline_group_node is not None, '找不到Outlines节点'
        
        diffuse_texture_node.image = self._body_diffuse_image_data
        diffuse_texture_node.image.colorspace_settings.name = 'sRGB'
        diffuse_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        lightmap_texture_node.image = self._body_lightmap_image_data
        lightmap_texture_node.image.colorspace_settings.name = 'Non-Color'
        lightmap_texture_node.image.alpha_mode = 'CHANNEL_PACKED'
        
        for i in range(1, 6):
            color_input = outline_group_node.inputs[f'Outline Color {i}']
            outline_color_obj = self._outline_info['BodyOutline'][f'Color{i}']
            color_input.default_value = (
                outline_color_obj['r'],
                outline_color_obj['g'],
                outline_color_obj['b'],
                outline_color_obj['a']
            )

    def replace_slot_material(self, mesh_obj, old_material_name, new_material_name):
        new_material = bpy.data.materials.get(new_material_name)
        if new_material is None:
            raise BobHException(f"Material '{new_material_name}' not found.")
        for slot in mesh_obj.material_slots:
            if slot.material and slot.material.name == old_material_name:
                slot.material = new_material
                print(f"Replaced material '{old_material_name}' with '{new_material_name}'.")

    def replace_mmd_material_with_shader(self, mesh_obj: bpy.types.Object):
        face_detect_keywords = ['面', '颜', 'face', 'Face']
        hair_detect_keywords = ['发', '髪', '髮', 'hair', 'Hair']
        # 更精确的身体材质关键词
        body_detect_keywords = ['体', '肌', 'skin', 'Skin']
        dress_detect_keywords = ['服', '衣', 'dress', 'Dress', '裙', '裤']
        eye_detect_keywords = ['目', 'eye', 'Eye']
        # 排除的材质名称关键词
        exclude_keywords = ['面具', 'mask', 'Mask', '舌', 'teeth', 'Teeth', '歯']

        materials = [slot.material for slot in mesh_obj.material_slots if slot.material]
        for mat in materials:
            # 检查是否是被排除的材质
            if any(ex_kw in mat.name for ex_kw in exclude_keywords):
                continue
            
            mmd_base_tex_node = self.find_material_node('mmd_base_tex', mat.node_tree.nodes)
            if mmd_base_tex_node is None or mmd_base_tex_node.image is None:
                self.report({'WARNING'}, f'无法识别mesh的材质: {mat.name}，请手动绑定这个材质')
                continue
    
            tex_image_name = mmd_base_tex_node.image.name.lower()  # 转换为小写便于比较
    
            # 更精确的匹配逻辑
            use_face_shader = any(kw.lower() in tex_image_name for kw in face_detect_keywords)
            use_hair_shader = any(kw.lower() in tex_image_name for kw in hair_detect_keywords)
            use_body_shader = any(kw.lower() in tex_image_name for kw in body_detect_keywords)
            use_dress_shader = any(kw.lower() in tex_image_name for kw in dress_detect_keywords)
            use_eye_shader = any(kw.lower() in tex_image_name for kw in eye_detect_keywords)
    
            # 特殊处理"spa_h.png"这种情况
            if 'spa_h' in tex_image_name:
                use_hair_shader = True
    
            if use_face_shader:
                self.replace_slot_material(mesh_obj, mat.name, self._meterial_name_map['Face_Mat_Name'])
            elif use_hair_shader:
                self.replace_slot_material(mesh_obj, mat.name, self._meterial_name_map['Hair_Mat_Name'])
            elif use_body_shader:
                self.replace_slot_material(mesh_obj, mat.name, self._meterial_name_map['Body_Mat_Name'])
            elif use_dress_shader or use_eye_shader:
                # 服装和眼睛也使用身体材质，但可以单独处理
                self.replace_slot_material(mesh_obj, mat.name, self._meterial_name_map['Body_Mat_Name'])
            else:
                self.report({'WARNING'}, f'无法识别mesh的材质: {mat.name} (图片名: {tex_image_name})，请手动绑定这个材质')

    def add_object_and_children_to_collection(self, obj, collection_name):
        new_collection = bpy.data.collections.get(collection_name)
        if not new_collection:
            new_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(new_collection)
        
        def add_to_collection_recursive(obj, collection):
            if obj.name not in collection.objects:
                collection.objects.link(obj)
            for original_collection in obj.users_collection:
                if original_collection != collection:
                    original_collection.objects.unlink(obj)
            for child in obj.children:
                add_to_collection_recursive(child, collection)
        
        add_to_collection_recursive(obj, new_collection)

    def location_add(self, x, y):
        return tuple(a + b for a, b in zip(x, y))

    def get_head_origin_position(self, mesh_location):
        return self.location_add((0, -0.0113, 1.3269), mesh_location)

    def get_head_forward_position(self, mesh_location):
        return self.location_add((0, 3.11949, 1.3269), mesh_location)
    
    def get_head_up_position(self, mesh_location):
        return self.location_add((0, -0.0113, -0.826729), mesh_location)

    def create_light_dir_and_head_empty(self, model_name, collection_name, mesh_location):
        # Light Direction
        light_template_object = bpy.data.objects.get('Light Direction Template')
        if light_template_object is None:
            raise BobHException('请先导入Shader预设')
        
        model_light_object = light_template_object.copy()
        model_light_object.location = mesh_location
        model_light_object.name = f'{model_name}Light Direction'
        model_light_object.hide_render = False
        model_light_object.hide_viewport = False
        
        collection = bpy.data.collections.get(collection_name)
        collection.objects.link(model_light_object)

        # Head binding
        head_origin_object = bpy.data.objects.new(f'{model_name}Head Origin', None)
        head_origin_object.empty_display_type = 'PLAIN_AXES'
        head_origin_object.empty_display_size = 0.2
        head_origin_object.delta_scale = (2.14208, 2.14208, 2.14208)
        head_origin_object.location = self.get_head_origin_position(mesh_location)
        self.add_object_and_children_to_collection(head_origin_object, collection_name)

        head_forward_object = bpy.data.objects.new(f'{model_name}Head Forward', None)
        head_forward_object.empty_display_type = 'CUBE'
        head_forward_object.empty_display_size = 0.2
        head_forward_object.delta_location = (0, -3.91348, 0)
        head_forward_object.delta_scale = (0.657891, 0.657891, 0.657891)
        head_forward_object.location = self.get_head_forward_position(mesh_location)
        self.add_object_and_children_to_collection(head_forward_object, collection_name)

        head_up_object = bpy.data.objects.new(f'{model_name}Head Up', None)
        head_up_object.empty_display_type = 'CUBE'
        head_up_object.empty_display_size = 0.2
        head_up_object.delta_location = (0, 0, 2.69204)
        head_up_object.delta_scale = (0.620684, 0.620684, 0.620684)
        head_up_object.location = self.get_head_up_position(mesh_location)
        self.add_object_and_children_to_collection(head_up_object, collection_name)

    def execute(self, context):
        context.scene.view_settings.view_transform = 'Standard'
        select_obj = context.active_object
        
        if select_obj.type != 'MESH':
            self.report({'ERROR'}, '请选中一个MMD模型角色的mesh')
            return {'CANCELLED'}
            
        mat_directory = context.scene.material_directory
        mmd_root_obj = self.find_mmd_root_object(select_obj)
        
        if not mmd_root_obj:
            self.report({'ERROR'}, '请选中一个MMD模型角色')
            return {'CANCELLED'}
        
        if not mat_directory or mat_directory == '':
            self.report({'ERROR'}, '请指定要导入角色的材质目录')
            return {'CANCELLED'}
        
        mesh_location = select_obj.matrix_world.to_translation()
        model_name = f'{mmd_root_obj.mmd_root.name}_{mmd_root_obj.mmd_root.name_e}_'
        collection_name = f'{model_name}_Collection'

        try:
            # 确保预设存在，必要时重新导入
            if not self.guard_shader_exist():
                self.import_shader_preset()
                # 导入后再次检查
                if not self.guard_shader_exist():
                    raise BobHException('Shader预设导入失败，请检查插件安装')
                
            self._meterial_name_map = self.copy_meterial_for_character(model_name)
            self._outline_info = self.read_character_outline_info(mat_directory)
            self.apply_texture_to_material(mat_directory)
            self.apply_outline_color_to_material(mat_directory)
            self.replace_mmd_material_with_shader(select_obj)
            self.add_object_and_children_to_collection(mmd_root_obj, collection_name)
            self.create_light_dir_and_head_empty(model_name, collection_name, mesh_location)
            
            # 确保操作完成后预设资源仍然存在
            if not self.guard_shader_exist():
                raise BobHException('操作过程中Shader预设被意外移除')
                
        except BobHException as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f'发生未知错误: {str(e)}')
            return {'CANCELLED'}

        self.report({'INFO'}, '应用材质到角色成功')
        return {'FINISHED'}
