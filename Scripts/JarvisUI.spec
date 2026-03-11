# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'httptools', 'httptools.parser', 'httptools.parser.parser', 'dotenv', 'pystray._win32', 'ollama', 'httpx', 'qdrant_client', 'mcp', 'structlog', 'tenacity', 'pydantic_settings', 'PyQt6']
hiddenimports += collect_submodules('Server')
hiddenimports += collect_submodules('Core')
hiddenimports += collect_submodules('Brain')
hiddenimports += collect_submodules('Skills')
hiddenimports += collect_submodules('Integrations')
hiddenimports += collect_submodules('MCP')
hiddenimports += collect_submodules('Utils')
hiddenimports += collect_submodules('UI')
hiddenimports += collect_submodules('PyQt6')


a = Analysis(
    ['C:\\Users\\boran\\Desktop\\Jarvis_Aİ\\jarvis_ui.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\boran\\Desktop\\Jarvis_Aİ\\.env', '.'), ('C:\\Users\\boran\\Desktop\\Jarvis_Aİ\\Config', 'Config'), ('C:\\Users\\boran\\Desktop\\Jarvis_Aİ\\assets', 'assets')],
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
    [],
    exclude_binaries=True,
    name='JarvisUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\boran\\Desktop\\Jarvis_Aİ\\assets\\jarvis.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JarvisUI',
)
