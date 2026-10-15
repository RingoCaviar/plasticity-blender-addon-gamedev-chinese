"""Build a Blender-installable release archive.

The archive contains one top-level directory. Blender expects the add-on's
``__init__.py`` to live at the root of that directory.
"""
from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = "plasticity_blender_addon_gamedev_chinese"
INCLUDE_FILES = {
    "__init__.py",
    "client.py",
    "handler.py",
    "hierarchy.py",
    "LICENSE",
    "operators.py",
    "preferences.py",
    "README.md",
    "translations.py",
    "ui.py",
    "uv_preserve.py",
}
INCLUDE_DIRS = {"libs", "images"}


def version_from_init() -> str:
    text = (ROOT / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'"version"\s*:\s*\(([^)]*)\)', text)
    if not match:
        raise RuntimeError("Could not find bl_info version in __init__.py")
    return ".".join(part.strip() for part in match.group(1).split(",") if part.strip())


def build(output: Path, package_name: str, version: str) -> Path:
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(INCLUDE_FILES):
            source = ROOT / name
            if not source.is_file():
                raise FileNotFoundError(source)
            archive.write(source, f"{package_name}/{name}")
        for directory in sorted(INCLUDE_DIRS):
            source_dir = ROOT / directory
            for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
                archive.write(source, f"{package_name}/{source.relative_to(ROOT).as_posix()}")

    expected_prefix = package_name + "/"
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        if not names or any(not name.startswith(expected_prefix) for name in names):
            raise RuntimeError("Release archive must contain exactly one top-level add-on directory")
        if f"{package_name}/__init__.py" not in names:
            raise RuntimeError("Release archive is missing the add-on __init__.py")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Output ZIP path (default: dist/<package>-<version>.zip)")
    parser.add_argument("--package-name", default=DEFAULT_PACKAGE, help="Top-level directory inside the ZIP")
    args = parser.parse_args()
    version = version_from_init()
    output = args.output or ROOT / "dist" / f"{args.package_name}-{version}.zip"
    result = build(output, args.package_name, version)
    print(result)


if __name__ == "__main__":
    main()
