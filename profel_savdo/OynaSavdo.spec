# -*- mode: python ; coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════
#  OYNA SAVDO — PyInstaller spec fayli
#  Ishlatish: profel_savdo/ papkasida
#             pyinstaller OynaSavdo.spec --noconfirm
#  Natija:    dist/OYNA SAVDO.exe
# ═══════════════════════════════════════════════════════════════

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config',          'config'),
        ('oyna_savdo.ico',  '.'),
        ('icon.ico',        '.'),
    ],
    hiddenimports=[
        # Qt
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        # ReportLab
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.units',
        'reportlab.lib.colors',
        'reportlab.lib.styles',
        'reportlab.platypus',
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.dialects.sqlite',
        # openpyxl
        'openpyxl',
        'openpyxl.workbook',
        'openpyxl.styles',
        # App
        'utils.receipt_printer',
        'reports.pdf_generator',
    ],
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
    name='OYNA SAVDO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                   # Terminal oynasi ko'rinmaydi
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['oyna_savdo.ico'],          # OYNA SAVDO ikona
)
