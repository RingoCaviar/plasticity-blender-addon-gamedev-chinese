<a href="https://buymeacoffee.com/User129863">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="请作者喝杯咖啡" width="200">
</a>

# plasticity-blender-addon-gamedev 中文版

## 最新版本：1.4.1

- 修复 Alt+单击可能选中目标缝合区域之外面的问题。

## 1.4 版本更新

- 保留 CAD 面边界缝合边、已合并岛和现有 UV 布局。
- 新增实时 UV 更新模式：展开、盒投影或关闭，并支持调整投影尺寸。
- 展开时保留现有缝合边，避免自动重建 CAD 面边界。
- 实时扩展开启时，Alt+单击选择缝合边围成的区域，Ctrl+Alt+单击取消选择。
- 改进圆柱与圆角槽壁的自动选择、圆柱缝合边朝向相机控制和球形帽/开口 UV 投影。
- 新增对齐、基数和最大覆盖率 UV 打包模式。
- 新增切换检查纹理按钮；断开 Plasticity 时也可使用本地 UV、网格工具。
- 扩大重新细分容差和角度范围。

<p>
  <a href="https://www.youtube.com/watch?v=Bk0S0jZEzRM">
    <img src="https://img.youtube.com/vi/Bk0S0jZEzRM/hqdefault.jpg" alt="在 YouTube 观看">
  </a><br>
  手柄模型作者：<a href="https://www.youtube.com/@Kuechmeister">Kuechmeister Swagger</a>
</p>

<p>
  <a href="https://www.youtube.com/watch?v=2gdkzLUBxUU)">
    <img src="https://img.youtube.com/vi/2gdkzLUBxUU/hqdefault.jpg" alt="在 YouTube 观看">
  </a><br>
  摩托车模型作者：<a href="https://www.youtube.com/@yn2097_">Yann Goument</a>
</p>

## 面向游戏开发的 Plasticity Blender Bridge 分支

这是一个非官方分支，定期合并官方 Plasticity Blender 插件的最新改进，并针对快速实时资产准备增加工作流工具：拓扑/边控制、UV 工具和导出辅助功能。

## 已合并到官方插件工作流的功能

以下功能最初在本分支开发，后来已合并到官方 Plasticity Blender 插件工作流：

- AutoMarkEdgesOperator：将“标记锐边”和“在边界标记锐边”整合为一个操作符，可将选择标记为硬边（锐边）或 UV 缝合边。
- 智能边标记（锐边/缝合边）：对整个网格选择生效，并使用与 Plasticity 组分割法线标记相同的边界逻辑。
- 任意组多边形边界标记（锐边/缝合边）。
- 从任意组选择合并 UV 缝合边。
- Plasticity 组边选择工具。

本分支还继续提供面向游戏开发的实时资产准备功能。

## 版本 1.0 功能

- 选择 Plasticity 面时支持圆角感知选择与相邻圆角扩展。
- 用于游戏就绪拓扑控制的重新细分预设。
- 重新细分界面改进：预设保存 Tri/Ngon，常用容差与角度始终可见。
- 刷新筛选：仅 Blender 选中对象、仅 Plasticity 可见对象。
- 紧凑的可折叠界面布局。
- 相似几何体选择、合并/拆分对象、选择含多边面的网格、镜像、移除/应用修改器与顶点组。
- 合并不重叠网格、UV 工作流工具及 FBX/OBJ 导入导出。

## 版本 1.1 更新

本次更新聚焦多对象 UV 工具、叠加显示和检查纹理工作流。

- 实时扩展选择（多对象）与实时 3D 展开。
- 合并 UV 缝合边、松弛 UV 均支持多对象。
- Plasticity 边高亮支持活动视图、遮挡、粗细与颜色控制。
- UV 编辑器打开/关闭不会再强制全选。
- 内置检查纹理库、预览网格和自定义文件选择。

## 版本 1.2 更新

主要界面重构：由单一密集面板改为标签式工作流：
- 固定
- 主界面
- 重新细分
- 实用工具
- UV / 材质 / 纹理工具
- 网格工具
- 偏好设置

新增固定工作流，可快速访问常用控制项与操作符。

自动合并 / 重置选择缝合边已重新命名并更新行为：单击重置目标 Plasticity 面的缝合边；拖动选择时持续合并/重置。

选择驱动的缝合边自动化不再依赖实时扩展；多对象缝合边、松弛 UV 与打包 UV 岛工作流均已改进。

偏好设置标签页提供全局选项，包括“选择时自动分配检查纹理”。插件最低支持 Blender 4.3+。

## 版本 1.2.2 更新

- 改进实时重新细分与 Live Link 工作流。
- 新增实时绘制 Plasticity 面控制、颜色属性和预览材质模式。
- 修复 Blender 5.x 下的多项 UV、缝合边与松弛 UV 稳定性问题。

## 版本 1.2.3 更新

- 新增（实验性）实时扩展“自动选择圆柱面”和圆柱最小包裹角设置。
- 实时扩展开启时，使用圆形、自动圆形或框选并按住 Ctrl 可取消选择 Plasticity 表面。
- 常规错误修复与稳定性改进。

https://github.com/user-attachments/assets/2dd4efb0-cb47-4379-9c01-1dccc4edc275

## 版本 1.2.4 更新

- 偏好设置新增 Better FBX Importer & Exporter 导入/导出选项。
- 修复多对象选择时的合并缝合边问题。
- 常规错误修复与稳定性改进。

## 版本 1.3 更新

- 网格工具新增 Plasticity 对象变换控制。
- 设为 Blender 后，可在重新细分/刷新时保留本地编辑的枢轴、位置和旋转，便于装配工作。
- 常规错误修复与稳定性改进。
- 模型作者：Yann Goument。

https://github.com/user-attachments/assets/bed96ba8-e440-4f40-ba1c-5b3c95cbf68b

<img width="332" height="616" alt="界面截图" src="https://github.com/user-attachments/assets/17993347-a8d1-4f6f-85d6-de8c33d2bd8e" />

## 版本 1.3.1 更新

- 刷新增加“仅 Plasticity 中的新对象”。
- 启用后仅导入 Blender 场景中尚不存在的 Plasticity 对象，避免刷新已导入对象。

## 版本 1.3.2 更新

- 新增 Blender 到 Plasticity 的 PolySpline 工作流，并在主标签页增加“发送到 Plasticity”按钮。
- 注意：通过此工作流发送的网格必须带有 Sub-D 修改器。
- 支持发送前自动创建 Sub-D 修改器。
- Blender 中公开 PolySpline 选项：圆角、合并曲面片和精确插值边界。
- 支持多对象发送和发送时自动分离松散部件。

https://github.com/user-attachments/assets/6e29f8ec-b462-414b-9091-e373f7d5f232

https://github.com/user-attachments/assets/e524569c-2892-42ee-a86b-ee753772e68e`r`n`r`n# Release packaging

Run this from the repository root:

```powershell
python tools/package_release.py
```

The generated archive is written to `dist/` and is ready for Blender's **Install...** command. The ZIP contains one top-level directory (`plasticity_blender_addon_gamedev_chinese/`); `__init__.py` is directly inside that directory, as required for a Blender add-on package.

Use `--output` to choose another ZIP path or `--package-name` to change the installed directory name.


