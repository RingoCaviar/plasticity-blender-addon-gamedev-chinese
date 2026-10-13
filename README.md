<div align="center">

# Plasticity Blender Addon Gamedev

[![Version](https://img.shields.io/badge/version-1.4.0-2ea44f)](#latest-release-140)
[![Blender](https://img.shields.io/badge/Blender-4.3%2B-E87D0D?logo=blender&logoColor=white)](CHANGELOG.md#version-12-updates)
[![License](https://img.shields.io/badge/license-MIT-0969da)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/User129863/plasticity-blender-addon-gamedev?logo=github)](https://github.com/User129863/plasticity-blender-addon-gamedev/stargazers)

<a href="https://buymeacoffee.com/User129863">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" width="180">
</a>

</div>

## GameDev-focused fork of the Plasticity Blender Bridge.

Unofficial fork that regularly incorporates the latest improvements from the official Plasticity Blender add-on, and adds workflow tools / improvements for fast real-time asset prep: topology/edge control, UV workflow utilities, and export-oriented helpers.

<div align="center">

<p>
  <a href="https://www.youtube.com/watch?v=Bk0S0jZEzRM">
    <img src="https://img.youtube.com/vi/Bk0S0jZEzRM/hqdefault.jpg" width="720" alt="Watch on YouTube">
  </a><br>
  Gamepad Model by: <a href="https://www.youtube.com/@Kuechmeister">Kuechmeister Swagger</a>
</p>

<p>
  <a href="https://www.youtube.com/watch?v=2gdkzLUBxUU">
    <img src="https://img.youtube.com/vi/2gdkzLUBxUU/hqdefault.jpg" width="720" alt="Watch on YouTube">
  </a><br>
  Motorcycle Model by: <a href="https://www.youtube.com/@yn2097_">Yann Goument</a>
</p>

</div>

## Latest Release: 1.4.0

- **Preserve UV Seams:** retain CAD-face boundary seams and merged islands when updating meshes through Refresh or Refacet.
- **Preserve UVs:** transfer existing UV layouts when updating meshes from Plasticity, helping textures stay aligned.
- **Live UV Update modes:** choose **Unwrap**, **Box Project**, or **Off** after seam edits. The add-on now manages live UV updates, so you no longer need to enable Blender's **Live Unwrap** separately. Box Project includes an adjustable projection size.
- **Preserve Existing Seams when unwrapping:** unwrap using your current seams without automatically rebuilding CAD-face boundaries, keeping manually merged islands together.
- **Select regions enclosed by seams:** while Live Expand is enabled, **Alt+Click** selects a seam-bound region and **Ctrl+Alt+Click** deselects it.
- **Improved Auto Select Cylinders:** better detection of cylindrical and rounded-slot walls, with improved exclusion of caps and transition fillets. Cylinder selection is no longer marked experimental.
- **Seam Toward Camera:** steer automatic cylinder seam placement by rotating your view so the desired side faces you. The add-on favors an edge path on that side, giving you approximate control over the seam's position. Replaces the previous Occluded Only option.
- **Simplified cylinder seam controls:** removed the separate Cylinder Seam Mode and Partial Wrap Angle settings.
- **Improved Sphere Cap / Opening workflow:** dedicated UV projection for spherical caps and openings, with adjustable cap size and cap-and-band layouts for deeper shapes.
- **New UV packing modes:** **Aligned** preserves island orientation, **Cardinal** allows 90° rotations, and **Maximum Coverage** allows free rotation and tighter packing.
- **Toggle Checker Texture:** a single button applies or removes the checker texture and restores previous material assignments.
- **Tools available while disconnected:** access UV tools, mesh tools, and other local utilities without an active Plasticity connection.
- **Expanded Refacet ranges:** minimum tolerance reduced from **0.0001 to 0.000001**, and minimum angle reduced from **0.1 to 0.01**, across controls and presets.

[View older releases](CHANGELOG.md)

## Installation

Requires **Blender 4.3 or newer**.

1. Download the add-on **ZIP file** from the [Releases page](https://github.com/User129863/plasticity-blender-addon-gamedev/releases). Leave the ZIP file compressed.
2. If you have a previous Plasticity bridge add-on installed, remove it in **Edit > Preferences > Add-ons** before installing this version.
3. In **Edit > Preferences > Add-ons**, open the menu in the upper-right corner and choose **Install from Disk**.
4. Select the downloaded ZIP file and confirm the installation.
5. Search for **Plasticity Blender Addon Gamedev** and enable its checkbox.
6. Restart Blender, then press **N** in the 3D Viewport and open the **Plasticity GameDev** sidebar tab.

**Connect to Plasticity**

Open your model in Plasticity and enable its Blender bridge server. In Blender, keep the server address set to `localhost:8980` when both applications run on the same computer, then click **Connect**. Use **Refresh** in the Main tab to bring your model into Blender, or enable **Live link** for ongoing updates.
