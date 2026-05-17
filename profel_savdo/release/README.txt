# PROFIL SAVDO - POS TIZIMI
# Versiya: 1.0.0 (PostgreSQL Edition)

═══════════════════════════════════════════════════════════
ISHGA TUSHIRISH
═══════════════════════════════════════════════════════════

1. ProfilSavdo.exe ni ikki marta bosing
2. Dastur avtomatik ishga tushadi
3. Birinchi ishga tushganda SQLite (lokal) rejimida ishlaydi

═══════════════════════════════════════════════════════════
KLAVIATURA YORLIQLARI
═══════════════════════════════════════════════════════════

F1  - Sotuv sahifasi
F2  - Mahsulotlar
F3  - Mijozlar
F4  - Hisobotlar
F5  - Qarz to'lash
F6  - Kategoriyalar
F7  - Sozlamalar (PostgreSQL)
F8  - Chek ko'rish
F9  - Savatni tozalash
F12 - Savdoni yakunlash

═══════════════════════════════════════════════════════════
POSTGRESQL SOZLASH (2 KOMPYUTER UCHUN)
═══════════════════════════════════════════════════════════

ASOSIY KOMPYUTER (SERVER):

1. PostgreSQL 14+ o'rnating
2. Database yarating: profel_savdo
3. LAN ulanishni yoqing:
   - postgresql.conf: listen_addresses = '*'
   - pg_hba.conf: host all all 192.168.0.0/16 md5
4. Firewall: 5432 portni oching
5. ProfilSavdo.exe ni ishga tushiring
6. F7 bosing → Sozlamalar
7. Kiriting:
   - IP: localhost
   - Port: 5432
   - Database: profel_savdo
   - Username: postgres
   - Password: (sizning parolingiz)
8. "Ulanishni Tekshirish" → "Saqlash"
9. Dasturni yoping va qayta oching

IKKINCHI KOMPYUTER (KASSIR):

1. ProfilSavdo.exe ni nusxalang
2. Ishga tushiring
3. F7 bosing → Sozlamalar
4. Kiriting:
   - IP: 192.168.1.100 (server IP)
   - Port: 5432
   - Database: profel_savdo
   - Username: postgres
   - Password: (server paroli)
5. "Ulanishni Tekshirish" → "Saqlash"
6. Dasturni yoping va qayta oching

TEKSHIRISH:

- Asosiy kompyuterda mahsulot qo'shing
- Ikkinchi kompyuterda F2 bosing
- Mahsulot ko'rinishi kerak!

═══════════════════════════════════════════════════════════
OFFLINE ISHLATISH
═══════════════════════════════════════════════════════════

Dastur INTERNET TALAB QILMAYDI.

Faqat lokal network (LAN) kerak.

Agar PostgreSQL server yo'q bo'lsa:
- Avtomatik SQLite rejimiga o'tadi
- Bitta kompyuterda ishlaydi
- Ma'lumotlar lokal saqlanadi

═══════════════════════════════════════════════════════════
BACKUP (ZAXIRA NUSXA)
═══════════════════════════════════════════════════════════

POSTGRESQL UCHUN:

1. pgAdmin 4 ni oching
2. Databases → profel_savdo → o'ng tugma → Backup
3. Format: Custom
4. Fayl nomi: profel_savdo_2026-05-16.backup
5. Backup tugmasini bosing
6. Faylni boshqa diskka nusxalang

SQLITE UCHUN:

1. profel_savdo.db faylini nusxalang
2. Boshqa diskka saqlang
3. Har kuni yangi nusxa oling

═══════════════════════════════════════════════════════════
MUAMMOLARNI HAL QILISH
═══════════════════════════════════════════════════════════

MUAMMO: "Server bilan aloqa yo'q"

YECHIM:
1. PostgreSQL ishga tushganini tekshiring
2. IP manzilni to'g'ri kiritganingizni tekshiring
3. Firewall 5432 portni ochganini tekshiring
4. ping 192.168.1.100 buyrug'i bilan tekshiring

MUAMMO: Dastur ochilmayapti

YECHIM:
1. ProfilSavdo.exe ni o'ng tugma → Administrator sifatida ishga tushiring
2. Antivirus dasturni bloklayotganini tekshiring
3. logs/error.log faylini oching va xatoni ko'ring

MUAMMO: Ma'lumotlar sinxronlanmayapti

YECHIM:
1. Ikkala kompyuter ham bir xil database ga ulanganini tekshiring
2. F7 → Sozlamalar → IP va database nomini tekshiring
3. Dasturni qayta ishga tushiring

═══════════════════════════════════════════════════════════
TEXNIK YORDAM
═══════════════════════════════════════════════════════════

Qo'shimcha yordam uchun:

1. POSTGRESQL_SETUP_GUIDE.md ni o'qing (to'liq qo'llanma)
2. logs/error.log faylini tekshiring
3. F7 → "Ulanishni Tekshirish" tugmasini bosing

═══════════════════════════════════════════════════════════
TIZIM TALABLARI
═══════════════════════════════════════════════════════════

- Windows 10/11
- 4GB RAM (tavsiya etiladi)
- 500MB bo'sh joy
- LAN network adapter (2 kompyuter uchun)
- PostgreSQL 14+ (server kompyuterda)

═══════════════════════════════════════════════════════════
VERSIYA MA'LUMOTI
═══════════════════════════════════════════════════════════

Versiya: 1.0.0 (PostgreSQL Edition)
Sana: 2026-05-16
Til: O'zbek
Database: PostgreSQL + SQLite fallback

YANGI XUSUSIYATLAR:
✅ PostgreSQL multi-PC support
✅ LAN realtime synchronization
✅ Offline operation
✅ SQLite fallback
✅ Settings UI (F7)
✅ Professional error handling
✅ Modern UI/UX
✅ Custom alert system
✅ Keyboard shortcuts

═══════════════════════════════════════════════════════════

Muvaffaqiyatli savdo qiling!

Profil Savdo Development Team
2026
