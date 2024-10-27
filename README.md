# MMD模型一键导入Festivities原神风格shader

[English]()

## 已测试版本

Goo Engine 4.1

其他版本待测试

## 支持特性

1. 自动识别并替换原始 MMD 材质

2. 自动设置Festivities Shader内的材质贴图

3. 自动设置Outline颜色

4. 多角色同场景内绑定支持

## 使用方法

下载 [克里斯提亚娜](https://www.bilibili.com/video/BV1wradeKEvN/) 视频简介中修改过的 原神风格渲染 Shader 文件

获得以下三个文件: `HoYoverse - Genshin Impact v3.4.blend`, `HoYoverse - Genshin Impact Outlines v3.blend`, `HoYoverse - Genshin Impact Post-Processing.blend`

安装 [mmd tools插件](https://github.com/UuuNyaa/blender_mmd_tools)

安装本插件

在Blender内，使用 mmd tools 导入一个 pmx 原神模型，然后选中该模型的mesh部分

在3d视图按下键盘N打开侧工具栏，选中"BobH"栏，打开该插件的面板

点击"导入原神Shader预设"，并选择之前下载的 `HoYoverse - Genshin Impact v3.4.blend`文件

点击"导入原神描边预设"，并选择之前下载的 `HoYoverse - Genshin Impact Outlines v3.blend`文件

点击"导入角色材质目录", 并选择对应角色解包的材质目录(你可以在[GI-Assets](https://github.com/zeroruka/GI-Assets)项目获得这些资源)

确保选中角色mesh部分，然后点击"应用材质到选定mmd模型"，随后前往Blender的脚本面板，检查是否有警告未识别的材质，请手动在Blender着色器界面指定这些未识别的材质属于角色的哪个部分(Face, Body 还是Hair?)

完成材质修复后，点击"应用灯光和描边效果"即可完成一键导入

## 特别感谢

[@Festivities](https://github.com/festivities): Shader 作者

[@克里斯提亚娜](https://space.bilibili.com/322607631): 参考其使用Shader绑定材质的过程

[UuuNyaa/blender_mmd_tools](https://github.com/UuuNyaa/blender_mmd_tools): 强有力的BlenderMMD工作流辅助插件