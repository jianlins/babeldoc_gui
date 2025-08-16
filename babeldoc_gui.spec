# -*- mode: python ; coding: utf-8 -*-

import sys
import os

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
IS_LIN = sys.platform.startswith("linux")

# --------- Optional: cache assets under unique folders in the bundle ----------
cache_dirs = [
    os.path.expanduser("~/.cache/babeldoc/tiktoken"),
    os.path.expanduser("~/.cache/babeldoc/models"),
    os.path.expanduser("~/.cache/babeldoc/fonts"),
]

datas = []
for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        for root, _, files in os.walk(cache_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, cache_dir)
                if "tiktoken" in cache_dir:
                    target = os.path.join("babeldoc_cache", rel_path)
                elif "models" in cache_dir:
                    target = os.path.join("babeldoc_models", rel_path)
                elif "fonts" in cache_dir:
                    target = os.path.join("babeldoc_fonts", rel_path)
                else:
                    target = rel_path
                datas.append((full_path, target))

# --------- Icons per-OS ----------
icon_path = None
if IS_MAC:
    icon_path = "icons/app_icon.icns"
elif IS_WIN:
    icon_path = "icons/app_icon.ico"

# --------- Hidden imports per-OS ----------
hiddenimports = [
    "tiktoken_ext.openai_public",  # tiktoken plugin discovery
]
if IS_MAC:
    hiddenimports.append("AppKit")

# --------- Analysis / Build ----------
a = Analysis(
    ["src/main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="babeldoc_gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,             # GUI app; set True if you want console
    disable_windowed_traceback=False,
    argv_emulation=False,      # set True only for macOS drag&drop argv emulation
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,            # string path; per-OS above
    onefile=True,              # << IMPORTANT for single-file builds
)

# On macOS, wrap the EXE in an .app bundle; other OSes: just produce the EXE
if IS_MAC:
    app = BUNDLE(
        exe,
        name="babeldoc_gui.app",
        icon=icon_path,
        bundle_identifier=None,
    )
