@echo off
echo ========================================
echo Building OYNA SAVDO EXE
echo ========================================

cd /d "%~dp0"

echo Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building executable...
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "OYNA SAVDO" ^
    --icon="oyna_savdo.ico" ^
    --add-data "config;config" ^
    --add-data "assets;assets" ^
    --add-data "oyna_savdo.ico;." ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "sqlalchemy" ^
    --hidden-import "sqlalchemy.ext.declarative" ^
    main.py

echo ========================================
echo Build complete!
echo EXE location: dist\OYNA SAVDO.exe
echo ========================================
pause
