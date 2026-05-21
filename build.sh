#!/bin/bash
# ProfelSavdo Build Script for Linux/Mac
# Bu skript Linux/Mac da executable yasaydi

set -e

echo "========================================"
echo "ProfelSavdo Build Script"
echo "========================================"
echo ""

# Python versiyasini tekshirish
if ! command -v python3 &> /dev/null; then
    echo "[XATO] Python3 topilmadi!"
    echo "Python 3.9+ o'rnatilgan ekanligini tekshiring."
    exit 1
fi

echo "[1/4] Python topildi!"
python3 --version

# Virtual environment yaratish
if [ ! -d "venv" ]; then
    echo ""
    echo "[2/4] Virtual environment yaratilmoqda..."
    python3 -m venv venv
    echo "Virtual environment yaratildi!"
else
    echo "[2/4] Virtual environment allaqachon mavjud"
fi

# Virtual environment aktivlashtirish
source venv/bin/activate

# Dependencies o'rnatish
echo ""
echo "[3/4] Dependencies o'rnatilmoqda..."
pip install --upgrade pip
pip install -r profel_savdo/requirements.txt
echo "Dependencies o'rnatildi!"

# PyInstaller bilan build qilish
echo ""
echo "[4/4] Executable yaratilmoqda..."
pyinstaller ProfelSavdoFinal.spec --clean

echo ""
echo "========================================"
echo "BUILD MUVAFFAQIYATLI!"
echo "========================================"
echo ""
echo "Executable fayl: dist/ProfelSavdo"
echo ""

# Desktop ga ko'chirish (opsional)
read -p "Desktop ga ko'chirish? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp dist/ProfelSavdo ~/Desktop/
    echo "ProfelSavdo Desktop ga ko'chirildi!"
fi

echo ""
echo "Tarqatish folder yaratish uchun:"
echo "  mkdir ProfelSavdo-Release"
echo "  cp dist/ProfelSavdo ProfelSavdo-Release/"
echo "  cp 29.ico ProfelSavdo-Release/"
echo ""
