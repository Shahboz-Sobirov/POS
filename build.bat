@echo off
REM ProfelSavdo Build Script for Windows
REM Bu skript Windows da .exe yasaydi

echo ========================================
echo ProfelSavdo Build Script
echo ========================================
echo.

REM Python versiyasini tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python topilmadi!
    echo Python 3.9+ o'rnatilgan ekanligini tekshiring.
    pause
    exit /b 1
)

echo [1/4] Python topildi!
python --version

REM Virtual environment mavjudligini tekshirish
if not exist "venv\" (
    echo.
    echo [2/4] Virtual environment yaratilmoqda...
    python -m venv venv
    if errorlevel 1 (
        echo [XATO] Virtual environment yaratilmadi!
        pause
        exit /b 1
    )
    echo Virtual environment yaratildi!
) else (
    echo [2/4] Virtual environment allaqachon mavjud
)

REM Virtual environment aktivlashtirish
call venv\Scripts\activate.bat

REM Dependencies o'rnatish
echo.
echo [3/4] Dependencies o'rnatilmoqda...
pip install --upgrade pip
pip install -r profel_savdo\requirements.txt
if errorlevel 1 (
    echo [XATO] Dependencies o'rnatilmadi!
    pause
    exit /b 1
)
echo Dependencies o'rnatildi!

REM PyInstaller bilan build qilish
echo.
echo [4/4] Executable yaratilmoqda...
pyinstaller ProfelSavdoFinal.spec --clean
if errorlevel 1 (
    echo [XATO] Build xatosi!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD MUVAFFAQIYATLI!
echo ========================================
echo.
echo Executable fayl: dist\ProfelSavdo.exe
echo.
echo Desktop ga ko'chirish uchun:
echo   copy dist\ProfelSavdo.exe %USERPROFILE%\Desktop\
echo.

REM Desktop ga avtomatik ko'chirish (opsional)
set /p COPY_TO_DESKTOP="Desktop ga ko'chirish? (Y/N): "
if /i "%COPY_TO_DESKTOP%"=="Y" (
    copy dist\ProfelSavdo.exe %USERPROFILE%\Desktop\
    echo ProfelSavdo.exe Desktop ga ko'chirildi!
)

echo.
echo Tarqatish folder yaratish uchun:
echo   mkdir ProfelSavdo-Release
echo   copy dist\ProfelSavdo.exe ProfelSavdo-Release\
echo   copy 29.ico ProfelSavdo-Release\
echo.

pause
