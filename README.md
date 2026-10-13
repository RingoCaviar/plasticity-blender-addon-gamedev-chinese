<div align="center">

# Plasticity Blender Addon Gamedev

[![Version](https://img.shields.io/badge/version-1.4.1-2ea44f)](#latest-release-141)
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

## Latest Release: 1.4.1

- Fixed: Alt+Click could select faces outside the region enclosed by UV seams. Seam-region selection now respects existing boundaries and prevents Live Expand from adding neighboring surfaces.

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
