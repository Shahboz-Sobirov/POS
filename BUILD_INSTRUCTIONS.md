# ProfelSavdo - Build Yo'riqnomasi

## O'zgarishlar

### 1. Chek Formati (O'zbek tili)
- ✅ **Yakunlovchi chek**: "Chek raqami", "Telefon", "Mahsulot nomi", "Eni/Bo'yi metr", "UMUMIY SUMMA", "To'lov ma'lumotlari", "Xaridingiz uchun rahmat"
- ✅ **Ro'yxat cheki**: "Ro'yxat cheki (To'lov qilinmagan)" deb belgilangan, to'lov ma'lumotlari ko'rsatilmaydi, ombor rezerv qilinmaydi

### 2. Avtomatik KVM Hisoblash
- ✅ Qoldiq oyna qo'shishda eni va bo'yi **cm** da kiritiladi
- ✅ KVM avtomatik hisoblanadi: `(eni_cm × boyi_cm) ÷ 10000`
- ✅ KVM maydoni readonly (faqat o'qish)
- ✅ Birlik avtomatik "KVM" qilib belgilanadi

### 3. UI Yaxshilashlar
- ✅ Sotuv sahifasida mahsulotlar jadvali kattalashtirildi
- ✅ Yuqoridagi panellar optimallashtirildi
- ✅ Layout nisbatlari yaxshilandi (mahsulotlar ko'proq ko'rinadi)

## Windows Build Qilish

### Talablar
1. **Python 3.9+** o'rnatilgan bo'lishi kerak
2. **Git Bash** yoki **PowerShell**

### 1-Qadam: Dependencies O'rnatish

```bash
# Virtual environment yaratish (tavsiya etiladi)
python -m venv venv
venv\Scripts\activate

# Dependencies o'rnatish
pip install -r profel_savdo/requirements.txt
```

### 2-Qadam: Build

```bash
# ProfelSavdoFinal.spec yordamida build qilish
pyinstaller ProfelSavdoFinal.spec

# Yoki oddiy build
pyinstaller --name="ProfelSavdo" ^
    --onefile ^
    --windowed ^
    --icon="29.ico" ^
    --add-data "29.ico;." ^
    --add-data "Freeform@4x 2.png;." ^
    --hidden-import "PySide6.QtPrintSupport" ^
    --hidden-import "PySide6.QtPdf" ^
    --hidden-import "PySide6.QtPdfWidgets" ^
    --hidden-import "reportlab" ^
    --hidden-import "sqlalchemy.sql.default_comparator" ^
    profel_savdo/main.py
```

### 3-Qadam: Natija

Build muvaffaqiyatli bo'lsa:
- **dist/ProfelSavdo.exe** - Asosiy executable fayl
- **build/** - Build vaqt fayllari (o'chirish mumkin)

### 4-Qadam: Test Qilish

```bash
# Executable ni ishga tushiring
dist\ProfelSavdo.exe
```

## Tarqatish Uchun Tayyorlash

### Desktop uchun
1. `ProfelSavdo.exe` ni Desktop ga ko'chiring
2. Icon avtomatik taskbarda ko'rinadi (29.ico)

### Tarqatish Package
Quyidagi fayllarni folder ga yig'ing:

```
ProfelSavdo-Release/
├── ProfelSavdo.exe
├── README.txt (foydalanish yo'riqnomasi)
└── 29.ico (agar kerak bo'lsa)
```

Keyin ZIP yoki installer yarating.

## Muammolarni Hal Qilish

### Import Xatolari
Agar "Module not found" xatolari chiqsa:
```bash
pip install --upgrade PySide6 reportlab SQLAlchemy openpyxl
```

### Icon Ko'rinmayotgan Bo'lsa
- 29.ico fayli executable bilan bir joyda ekanligini tekshiring
- Icon cache ni yangilang: `ie4uinit.exe -ClearIconCache`

### Database Xatolari
Birinchi ishga tushirishda database avtomatik yaratiladi. Agar muammo bo'lsa:
- `profel_savdo.db` faylini o'chiring
- Dasturni qayta ishga tushiring

## Support

Muammolar yoki savollar uchun:
- Dasturchi bilan bog'laning
- Loglarni tekshiring: `logs/app.log` va `logs/error.log`

---
**Build sanasi**: 2026-05-21
**Versiya**: Final Release
