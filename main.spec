# -*- mode: python ; coding: utf-8 -*-


import glob
import os

cache_dirs = [
    os.path.expanduser("~/.cache/babeldoc/tiktoken"),
    os.path.expanduser("~/.cache/babeldoc/models"),
    os.path.expanduser("~/.cache/babeldoc/fonts"),
]
datas = []
for cache_dir in cache_dirs:
    if os.path.exists(cache_dir):
        for root, dirs, files in os.walk(cache_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, cache_dir)
                # Use a unique top-level folder for each asset type
                if "tiktoken" in cache_dir:
                    datas.append((full_path, os.path.join("babeldoc_cache", rel_path)))
                elif "models" in cache_dir:
                    datas.append((full_path, os.path.join("babeldoc_models", rel_path)))
                elif "fonts" in cache_dir:
                    datas.append((full_path, os.path.join("babeldoc_fonts", rel_path)))

a = Analysis(
    ['src/main.py'],
    icon='icons/app_icon.icns',
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['tiktoken_ext.openai_public', 'AppKit'],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icons/app_icon.icns'],
)
app = BUNDLE(
    exe,
    name='main.app',
    icon='icons/app_icon.icns',
    bundle_identifier=None,
)
