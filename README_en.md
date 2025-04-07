# One-Click MMD Model Import for Festivities' Genshin Impact-Style Shader

## Tested Version

Goo Engine 4.1

Blender 3.6

Blender 4.2

Blender 4.4

Other versions have not been tested yet.

## Features Supported

1. Automatic recognition and replacement of original MMD materials
2. Automatic setup of material textures in the Festivities Shader
3. Automatic configuration of outline colors
4. Support for multiple characters within the same scene

## Instructions for Use

1. Install the [mmd tools plugin](https://github.com/UuuNyaa/blender_mmd_tools).

2. Install this plugin.

3. In Blender, use mmd tools to import a Genshin Impact model in pmx format, then select the mesh portion of the model.

4. In the 3D View, press the "N" key to open the side toolbar, select the "BobHTool" tab, and open this plugin’s panel.

5. Click "导入角色材质目录"(Import Character Material Directory), and select the material directory of the unpacked character (these resources can be obtained from the [GI-Assets](https://github.com/zeroruka/GI-Assets) project).

6. Ensure the character's mesh portion is selected, then click "应用材质到选定mmd模型"(Apply Materials to Selected MMD Model) Next, go to the Blender scripting panel and check for any warnings about unrecognized materials. Manually assign these unrecognized materials to the relevant parts of the character (Face, Body, or Hair) in Blender's Shader Editor.

7. After fixing the materials, click "应用灯光和描边效果"(Apply Lighting and Outline Effects) to complete the one-click import.

## Special Thanks

[@Festivities](https://github.com/festivities): Shader author

[@Christiana](https://space.bilibili.com/322607631): For the reference on using shaders to bind materials

[UuuNyaa/blender_mmd_tools](https://github.com/UuuNyaa/blender_mmd_tools): Powerful plugin for Blender MMD workflow
