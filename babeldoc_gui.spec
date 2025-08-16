# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

BASE_DIR = os.getcwd()
runtime_hooks = [os.path.join(BASE_DIR, "pyi_rth_tiktoken_o200k.py")]


IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
IS_LIN = sys.platform.startswith("linux")

# --------- SciPy / NumPy ----------
scipy_hidden = collect_submodules("scipy")
scipy_datas  = collect_data_files("scipy")

numpy_hidden = []
numpy_hidden += collect_submodules("numpy.fft")
numpy_hidden += collect_submodules("numpy.linalg")
numpy_hidden += collect_submodules("numpy.random")
# optional,再保险：
# numpy_hidden += collect_submodules("numpy.array_api")

# --------- tiktoken plugin (critical) ----------
tke_hidden = collect_submodules("tiktoken_ext")                 # include subpackages incl. openai_public
tke_datas  = collect_data_files("tiktoken_ext.openai_public")   # include encoding JSONs/data

# --------- Optional: 把缓存打包进应用（可留空） ----------
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

# merge third-party data
datas += scipy_datas
datas += tke_datas

# --------- hiddenimports ----------
hiddenimports = [
    "tiktoken_ext.openai_public",  # 插件发现
]
if IS_MAC:
    hiddenimports.append("AppKit")

hiddenimports += scipy_hidden
hiddenimports += numpy_hidden
hiddenimports += tke_hidden

# --------- icons ----------
icon_path = None
if IS_MAC:
    icon_path = "icons/app_icon.icns"
elif IS_WIN:
    icon_path = "icons/app_icon.ico"

# --------- runtime hook ----------

a = Analysis(
    ["src/main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks,
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
    console=False,             # GUI app; 设置 True 可调试
    disable_windowed_traceback=False,
    argv_emulation=False,      # macOS 下 drag&drop 参数传递才需要 True
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    onefile=True,              # 单文件模式
)

if IS_MAC:
    app = BUNDLE(
        exe,
        name="babeldoc_gui.app",
        icon=icon_path,
        bundle_identifier=None,
    )
