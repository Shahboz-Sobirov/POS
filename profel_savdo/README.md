# Profel Savdo

Modern warehouse POS system for Profel products.

## Features

- ✅ Sales management (F1)
- ✅ Product management (F2)
- ✅ Customer management (F3)
- ✅ Reports (F4)
- ✅ Debt payment tracking (F5)
- ✅ Category management (F6)
- ✅ Invoice printing (F8 preview, F12 real)
- ✅ Keyboard-first UX
- ✅ Auto-calculated profit
- ✅ Anti-fraud security
- ✅ Audit logging

## Tech Stack

- Python 3.12+
- PySide6 (Qt)
- SQLAlchemy
- SQLite
- ReportLab (PDF)

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Build EXE

```bash
build.bat
```

EXE will be in `dist/ProfelSavdo.exe`

## Keyboard Shortcuts

- **F1** - Sotuv (Sales)
- **F2** - Mahsulotlar (Products)
- **F3** - Mijozlar (Customers)
- **F4** - Hisobot (Reports)
- **F5** - Qarz To'lash (Debt Payment)
- **F6** - Kategoriyalar (Categories)
- **F8** - Hisob-Chek (Invoice Preview)
- **F9** - Savatni Tozalash (Clear Cart)
- **F12** - Savdoni Yakunlash (Complete Sale)
- **Ctrl+F** - Qidirish (Search)
- **Ctrl+P** - Chop Etish (Print)
- **Ctrl+E** - Excel Export
- **Delete** - O'chirish (Delete)
- **Enter** - Tasdiqlash (Confirm)
- **Esc** - Bekor qilish (Cancel)

## Database

SQLite database: `profel_savdo.db`

Auto-created on first run with default categories:
- Profil
- Ruchka
- Qulf
- Setka
- Boshqa

## Security

- NO manual report editing
- NO manual profit editing
- NO manual sales history editing
- All actions logged in audit_logs table
- Profit auto-calculated: `sale_price - cost_price`

## Default Page

App opens to **SOTUV (Sales)** page, not dashboard.

## Payment Validation

`Naqd + Karta + Click + Qarz = Total`

Must balance before completing sale.

## Debt System

Sorted by **debt age** (oldest first), not amount.

Debt payments added to today's cashflow.

## Reports

- Daily (default)
- Weekly
- Monthly
- Yearly
- Custom range

Payment breakdown shown (NO "Mixed" label):
- Naqd: X
- Karta: Y
- Click: Z
- Qarz: W

## License

Proprietary - Profel Savdo
