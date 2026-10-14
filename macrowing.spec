# -*- mode: python ; coding: utf-8 -*-
# MacroWing PyInstaller spec file (Windows e Linux)
import sys

block_cipher = None

_is_windows = sys.platform == "win32"

hiddenimports = [
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
]

# Backend de input do pynput depende da plataforma.
if _is_windows:
    hiddenimports += [
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
    ]
else:
    hiddenimports += [
        'pynput.keyboard._xorg',
        'pynput.mouse._xorg',
    ]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MacroWing',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = sem janela de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    **({'uac_admin': True} if _is_windows else {}),
)