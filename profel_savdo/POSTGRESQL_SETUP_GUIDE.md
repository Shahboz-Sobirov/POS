# POSTGRESQL SETUP GUIDE
# PROFEL SAVDO POS - LAN MULTI-PC SYSTEM

**Sana:** 2026-05-16
**Version:** 1.0.0

---

## 📋 TIZIM TALABLARI

### Asosiy Kompyuter (Server):
- Windows 10/11
- PostgreSQL 14+ o'rnatilgan
- 4GB+ RAM
- LAN network adapter
- Static IP address (tavsiya etiladi)

### Ikkinchi Kompyuter (Kassir):
- Windows 10/11
- Profel Savdo dasturi o'rnatilgan
- LAN network adapter
- Asosiy kompyuter bilan bir xil network

---

## 🔧 QADAMMA-QADAM O'RNATISH

### QADAM 1: POSTGRESQL O'RNATISH (Asosiy Kompyuter)

#### 1.1. PostgreSQL yuklab olish

1. Saytga kiring: https://www.postgresql.org/download/windows/
2. "Download the installer" tugmasini bosing
3. Eng yangi versiyani tanlang (PostgreSQL 16 tavsiya etiladi)
4. Windows x86-64 versiyasini yuklab oling

#### 1.2. PostgreSQL o'rnatish

1. Yuklab olingan `.exe` faylni ishga tushiring
2. O'rnatish yo'lini tanlang (default: `C:\Program Files\PostgreSQL\16`)
3. Komponentlarni tanlang:
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4
   - ✅ Command Line Tools
   - ❌ Stack Builder (ixtiyoriy)

4. **MUHIM:** Superuser (postgres) parolini kiriting
   - Parolni eslab qoling! (masalan: `1234` yoki `postgres`)
   - Bu parol keyinchalik kerak bo'ladi

5. Port: `5432` (default, o'zgartirmang)

6. Locale: `Default locale`

7. O'rnatishni boshlang va tugashini kuting

#### 1.3. PostgreSQL xizmatini tekshirish

1. `Win + R` bosing
2. `services.msc` yozing va Enter bosing
3. `postgresql-x64-16` xizmatini toping
4. Status: **Running** bo'lishi kerak
5. Agar to'xtagan bo'lsa, o'ng tugma → Start

---

### QADAM 2: DATABASE YARATISH

#### 2.1. pgAdmin 4 ni ochish

1. Start Menu → PostgreSQL 16 → pgAdmin 4
2. Master parolni kiriting (o'rnatishda yaratgan parol)

#### 2.2. Database yaratish

1. Chap panelda: Servers → PostgreSQL 16 → Databases
2. Databases ustiga o'ng tugma → Create → Database
3. Database nomi: `profel_savdo`
4. Owner: `postgres`
5. Save tugmasini bosing

#### 2.3. Database tekshirish

1. Databases → profel_savdo → Schemas → public → Tables
2. Hozircha bo'sh bo'ladi (dastur birinchi ishga tushganda table'lar yaratiladi)

---

### QADAM 3: LAN ULANISHNI SOZLASH

#### 3.1. PostgreSQL konfiguratsiyasini o'zgartirish

**postgresql.conf faylini tahrirlash:**

1. Fayl joylashuvi:
   ```
   C:\Program Files\PostgreSQL\16\data\postgresql.conf
   ```

2. Faylni Notepad++ yoki Notepad bilan oching (Administrator sifatida)

3. Quyidagi qatorni toping:
   ```
   #listen_addresses = 'localhost'
   ```

4. Uni quyidagicha o'zgartiring:
   ```
   listen_addresses = '*'
   ```
   (# belgisini olib tashlang va localhost o'rniga * qo'ying)

5. Faylni saqlang

**pg_hba.conf faylini tahrirlash:**

1. Fayl joylashuvi:
   ```
   C:\Program Files\PostgreSQL\16\data\pg_hba.conf
   ```

2. Faylni Notepad++ yoki Notepad bilan oching (Administrator sifatida)

3. Faylning oxiriga quyidagi qatorni qo'shing:
   ```
   # Allow LAN connections
   host    all             all             192.168.0.0/16          md5
   ```

4. Agar sizning network 10.x.x.x bo'lsa:
   ```
   host    all             all             10.0.0.0/8              md5
   ```

5. Faylni saqlang

#### 3.2. PostgreSQL xizmatini qayta ishga tushirish

1. `Win + R` → `services.msc`
2. `postgresql-x64-16` xizmatini toping
3. O'ng tugma → Restart

---

### QADAM 4: FIREWALL SOZLAMALARI

#### 4.1. Windows Firewall qoidasini qo'shish

1. `Win + R` → `wf.msc` (Windows Defender Firewall)
2. Chap panelda: **Inbound Rules**
3. O'ng panelda: **New Rule...**
4. Rule Type: **Port** → Next
5. Protocol: **TCP**
6. Specific local ports: `5432` → Next
7. Action: **Allow the connection** → Next
8. Profile: ✅ Domain, ✅ Private, ✅ Public → Next
9. Name: `PostgreSQL Server` → Finish

#### 4.2. Firewall qoidasini tekshirish

1. Inbound Rules ro'yxatida `PostgreSQL Server` qoidasini toping
2. Status: **Enabled** bo'lishi kerak
3. Action: **Allow** bo'lishi kerak

---

### QADAM 5: IP MANZILNI ANIQLASH

#### 5.1. Asosiy kompyuterning IP manzilini topish

1. `Win + R` → `cmd`
2. Quyidagi buyruqni yozing:
   ```
   ipconfig
   ```
3. **IPv4 Address** ni toping, masalan:
   ```
   IPv4 Address: 192.168.1.100
   ```
4. Bu IP manzilni yozib qo'ying!

#### 5.2. Static IP o'rnatish (tavsiya etiladi)

1. Control Panel → Network and Sharing Center
2. Change adapter settings
3. Network adapter ustiga o'ng tugma → Properties
4. Internet Protocol Version 4 (TCP/IPv4) → Properties
5. **Use the following IP address:**
   - IP address: `192.168.1.100` (sizning IP)
   - Subnet mask: `255.255.255.0`
   - Default gateway: `192.168.1.1` (router IP)
   - Preferred DNS: `8.8.8.8`
6. OK → OK

---

### QADAM 6: ULANISHNI TEKSHIRISH

#### 6.1. Ikkinchi kompyuterdan ping qilish

1. Ikkinchi kompyuterda `Win + R` → `cmd`
2. Quyidagi buyruqni yozing:
   ```
   ping 192.168.1.100
   ```
   (192.168.1.100 o'rniga asosiy kompyuterning IP manzilini yozing)

3. Natija:
   ```
   Reply from 192.168.1.100: bytes=32 time<1ms TTL=128
   ```
   ✅ Agar shunday chiqsa - network ishlayapti!

4. Agar "Request timed out" chiqsa:
   - ❌ Firewall yopiq
   - ❌ IP manzil noto'g'ri
   - ❌ Network kabeli ulanmagan

#### 6.2. PostgreSQL portini tekshirish

1. Ikkinchi kompyuterda `Win + R` → `cmd`
2. Quyidagi buyruqni yozing:
   ```
   telnet 192.168.1.100 5432
   ```

3. Agar qora ekran chiqsa - ✅ Port ochiq!
4. Agar "Could not open connection" chiqsa:
   - ❌ PostgreSQL ishlamayapti
   - ❌ Firewall 5432 portni bloklayapti
   - ❌ postgresql.conf noto'g'ri sozlangan

---

### QADAM 7: PROFEL SAVDO DASTURINI SOZLASH

#### 7.1. Asosiy kompyuterda (Server)

1. Profel Savdo dasturini ishga tushiring
2. `F7` tugmasini bosing (Sozlamalar)
3. Quyidagi ma'lumotlarni kiriting:
   - **IP Manzil:** `localhost` yoki `127.0.0.1`
   - **Port:** `5432`
   - **Database:** `profel_savdo`
   - **Foydalanuvchi:** `postgres`
   - **Parol:** (o'rnatishda yaratgan parol)

4. **"Ulanishni Tekshirish"** tugmasini bosing
5. Agar muvaffaqiyatli bo'lsa: **"Saqlash"** tugmasini bosing
6. Dasturni yoping va qayta oching

#### 7.2. Ikkinchi kompyuterda (Kassir)

1. Profel Savdo dasturini ishga tushiring
2. `F7` tugmasini bosing (Sozlamalar)
3. Quyidagi ma'lumotlarni kiriting:
   - **IP Manzil:** `192.168.1.100` (asosiy kompyuterning IP)
   - **Port:** `5432`
   - **Database:** `profel_savdo`
   - **Foydalanuvchi:** `postgres`
   - **Parol:** (asosiy kompyuterdagi PostgreSQL paroli)

4. **"Ulanishni Tekshirish"** tugmasini bosing
5. Agar muvaffaqiyatli bo'lsa: **"Saqlash"** tugmasini bosing
6. Dasturni yoping va qayta oching

---

## ✅ TEKSHIRISH VA TEST

### Test 1: Mahsulot qo'shish

1. **Asosiy kompyuterda:**
   - F2 → Mahsulotlar
   - Yangi mahsulot qo'shing: "Test Mahsulot"

2. **Ikkinchi kompyuterda:**
   - F2 → Mahsulotlar
   - "Test Mahsulot" ko'rinishi kerak!

### Test 2: Savdo qilish

1. **Ikkinchi kompyuterda:**
   - F1 → Sotuv
   - Mahsulot qo'shing va savdo qiling

2. **Asosiy kompyuterda:**
   - F4 → Hisobot
   - Yangi savdo ko'rinishi kerak!

### Test 3: Qarz to'lash

1. **Asosiy kompyuterda:**
   - Mijoz yarating va qarzga savdo qiling

2. **Ikkinchi kompyuterda:**
   - F5 → Qarz To'lash
   - Mijoz qarzini ko'rish va to'lash mumkin bo'lishi kerak

---

## 🔧 MUAMMOLARNI HAL QILISH

### Muammo 1: "Server bilan aloqa yo'q"

**Sabablari:**
- PostgreSQL ishlamayapti
- IP manzil noto'g'ri
- Firewall bloklayapti
- Network kabeli ulanmagan

**Yechim:**
1. PostgreSQL xizmatini tekshiring (services.msc)
2. IP manzilni qayta tekshiring (ipconfig)
3. Firewall qoidasini tekshiring
4. Ping qiling: `ping 192.168.1.100`

### Muammo 2: "Parol noto'g'ri"

**Yechim:**
1. PostgreSQL parolini to'g'ri kiritganingizni tekshiring
2. pgAdmin 4 da ulanib ko'ring
3. Agar parolni unutgan bo'lsangiz, PostgreSQL ni qayta o'rnating

### Muammo 3: "Database topilmadi"

**Yechim:**
1. pgAdmin 4 ni oching
2. Databases ro'yxatida `profel_savdo` borligini tekshiring
3. Agar yo'q bo'lsa, qayta yarating (QADAM 2)

### Muammo 4: Sekin ishlayapti

**Yechim:**
1. Network tezligini tekshiring
2. Switch/Router ni qayta ishga tushiring
3. Antivirus PostgreSQL ni bloklayotganini tekshiring
4. PostgreSQL konfiguratsiyasini optimize qiling

### Muammo 5: Ma'lumotlar sinxronlanmayapti

**Yechim:**
1. Ikkala kompyuterda ham bir xil database ga ulanganini tekshiring
2. F7 → Sozlamalar → IP manzil va database nomini tekshiring
3. Dasturni qayta ishga tushiring

---

## 📊 NETWORK ARXITEKTURASI

```
┌─────────────────────────────────────────┐
│         ASOSIY KOMPYUTER (SERVER)       │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     PostgreSQL Database           │ │
│  │     Port: 5432                    │ │
│  │     IP: 192.168.1.100             │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     Profel Savdo Client           │ │
│  │     (Admin)                       │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
                    │ LAN Network
                    │ (Switch/Router)
                    │
┌─────────────────────────────────────────┐
│      IKKINCHI KOMPYUTER (KASSIR)        │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     Profel Savdo Client           │ │
│  │     Connects to: 192.168.1.100    │ │
│  │     (Kassir)                      │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🔒 XAVFSIZLIK TAVSIYALARI

1. **Kuchli parol ishlating:**
   - Kamida 8 belgi
   - Harflar, raqamlar, belgilar

2. **Faqat LAN network:**
   - Internet orqali ulanishni yoqmang
   - Faqat mahalliy network ishlatilsin

3. **Firewall:**
   - Faqat 5432 portni oching
   - Boshqa portlarni yoping

4. **Backup:**
   - Har kuni database backup oling
   - Backup ni boshqa diskda saqlang

5. **Antivirus:**
   - PostgreSQL papkasini antivirus exception ga qo'shing
   - Real-time scanning sekinlashtirishi mumkin

---

## 📝 BACKUP VA RESTORE

### Backup olish (Har kuni!)

1. pgAdmin 4 ni oching
2. Databases → profel_savdo → o'ng tugma → Backup
3. Filename: `profel_savdo_2026-05-16.backup`
4. Format: **Custom**
5. Backup tugmasini bosing
6. Faylni boshqa diskka nusxalang

### Restore qilish

1. pgAdmin 4 ni oching
2. Databases → profel_savdo → o'ng tugma → Restore
3. Backup faylini tanlang
4. Restore tugmasini bosing

---

## 📞 YORDAM

Agar muammolar hal bo'lmasa:

1. Error logni tekshiring: `logs/error.log`
2. PostgreSQL logni tekshiring: `C:\Program Files\PostgreSQL\16\data\log\`
3. Network administratorga murojaat qiling

---

**Tayyorlagan:** Profel Savdo Development Team
**Sana:** 2026-05-16
**Version:** 1.0.0
