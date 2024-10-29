# One-Click MMD Model Import for Festivities' Genshin Impact-Style Shader

[中文](./README.md)

## Tested Versions

Goo Engine 4.1

Goo Engine 3.6

Other versions pending test

## Supported Features

1. Automatic recognition and replacement of original MMD materials
2. Automatic setting of material textures in Festivities Shader
3. Automatic setting of outline colors
4. Support for binding multiple characters within the same scene

## Instructions for Use

1. Download the Genshin Impact-style rendering shader files modified in the video description by [Christiana](https://www.bilibili.com/video/BV1wradeKEvN/).

   You will obtain the following three files: `HoYoverse - Genshin Impact v3.4.blend`, `HoYoverse - Genshin Impact Outlines v3.blend`, `HoYoverse - Genshin Impact Post-Processing.blend`.

2. Install the [mmd tools plugin](https://github.com/UuuNyaa/blender_mmd_tools).

3. Install this plugin.

4. In Blender, use mmd tools to import a Genshin Impact model in pmx format, then select the mesh part of the model.

5. Press the "N" key in the 3D view to open the side toolbar, select the "BobHTool" tab, and open the panel of this plugin.

6. Click "导入原神Shader预设" (Import Genshin Shader Preset) and choose the previously downloaded `HoYoverse - Genshin Impact v3.4.blend` file.

7. Click "导入原神描边预设" (Import Genshin Outline Preset) and choose the previously downloaded `HoYoverse - Genshin Impact Outlines v3.blend` file.

8. Click "导入角色材质目录" (Import Character Material Directory), and choose the material directory of the unpacked character (you can obtain these resources from the [GI-Assets](https://github.com/zeroruka/GI-Assets) project).

9. Ensure the character's mesh part is selected, then click "应用材质到选定mmd模型" (Apply Materials to Selected MMD Model). Afterwards, go to Blender's script panel and check for any warnings about unrecognized materials. Manually specify these unrecognized materials in Blender's shader editor, determining which part of the character they belong to (Face, Body, or Hair).

10. After material correction, click "应用灯光和描边效果" (Apply Lighting and Outline Effects) to complete the one-click import.

11. If you wish to add post-processing nodes, click "导入并应用后处理" (Import and Apply Post-Processing). Then, in Blender's "Compositing" panel, you can view the already imported and applied post-processing nodes.

## Special Thanks

[@Festivities](https://github.com/festivities): Shader author

[@Christiana](https://space.bilibili.com/322607631): For the reference process of using shaders to bind materials

[UuuNyaa/blender_mmd_tools](https://github.com/UuuNyaa/blender_mmd_tools): Powerful BlenderMMD workflow support plugin