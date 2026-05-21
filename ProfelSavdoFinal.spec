# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['profel_savdo/main.py'],
    pathex=['profel_savdo'],
    binaries=[],
    datas=[
        ('29.ico', '.'),
        ('Freeform@4x 2.png', '.'),
    ],
    hiddenimports=[
        'PySide6.QtPrintSupport',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'sqlalchemy.sql.default_comparator',
    ],
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
    name='ProfelSavdo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Console yashirish
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='29.ico',  # 29.ico ni ishlatamiz
)
