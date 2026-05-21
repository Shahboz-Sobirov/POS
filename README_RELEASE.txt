=====================================
   PROFEL SAVDO - POS TIZIMI
=====================================

Versiya: Final Release
Sana: 2026-05-21

=====================================
   YANGI XUSUSIYATLAR
=====================================

1. TO'LIQ O'ZBEK TILIDA CHEKLAR
   - Yakunlovchi chek: to'liq to'lov ma'lumotlari bilan
   - Ro'yxat cheki: to'lovsiz, ombor rezervsiz preview

2. AVTOMATIK KVM HISOBLASH
   - Qoldiq oynalarda eni va bo'yi cm da kiritiladi
   - KVM avtomatik hisoblanadi
   - Manual kiritish imkoni yo'q

3. YAXSHILANGAN INTERFEYS
   - Sotuv sahifasida mahsulotlar yaxshi ko'rinadi
   - Optimallashtirilgan layout
   - Qulay ishlash uchun dizayn

=====================================
   O'RNATISH
=====================================

1. ProfelSavdo.exe faylini istalgan joyga ko'chiring
   (Masalan: Desktop yoki C:\Program Files\ProfelSavdo\)

2. Dasturni ishga tushiring (double-click)

3. Birinchi ishga tushirishda:
   - Lock panel ochiladi (Default parol: 1234)
   - Database avtomatik yaratiladi

=====================================
   FOYDALANISH
=====================================

KLAVIATURA YORLIQLAR:
  F1  - Sotuv sahifasi
  F2  - Mahsulotlar
  F3  - Mijozlar
  F4  - Omborxona
  F5  - Hisobotlar
  F6  - Kategoriyalar
  F7  - Sozlamalar
  F8  - Ro'yxat cheki (to'lovsiz)
  F9  - Savatni tozalash
  F12 - Savdoni yakunlash

QOLDIQ OYNA QO'SHISH:
  1. Mahsulotlar → "Qoldiq oynalar"
  2. "Yangi qoldiq" tugmasini bosing
  3. Eni va bo'yi cm da kiriting
  4. KVM avtomatik hisoblanadi
  5. Saqlang

SOTUV JARAYONI:
  1. F1 - Sotuv sahifasi
  2. Mahsulot tanlang va savatga qo'shing
  3. To'lov ma'lumotlarini kiriting
  4. F8 - Ro'yxat cheki (tekshirish uchun)
  5. F12 - Savdoni yakunlash (real chek)

=====================================
   TEXNIK MA'LUMOTLAR
=====================================

- Python 3.9+
- PySide6 (Qt6)
- SQLAlchemy
- ReportLab (PDF generation)

Database: SQLite (profel_savdo.db)
Loglar: logs/ papkasi

=====================================
   MUAMMOLARNI HAL QILISH
=====================================

DASTUR ISHLAMAYAPTI:
  - Windows Defender ni tekshiring
  - Administrator sifatida ishga tushiring
  - Antivirus ni vaqtincha o'chiring

DATABASE XATOLARI:
  - profel_savdo.db faylini o'chiring
  - Dasturni qayta ishga tushiring

CHEK CHIQMAYAPTI:
  - Printer ulangan va yoqiq ekanligini tekshiring
  - Default printer o'rnatilganligini tekshiring
  - PDF preview funksiyasidan foydalaning

=====================================
   SUPPORT
=====================================

Texnik yordam yoki savol-javoblar uchun:
- Dasturchi bilan bog'laning
- Loglarni tekshiring: logs/error.log

=====================================
   LITSENZIYA
=====================================

© 2024-2026 ProfelSavdo
Barcha huquqlar himoyalangan.

=====================================

Dasturdan foydalanganingiz uchun rahmat!
