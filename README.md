# Project CCTV AI - Setup Virtual Environment

Proyek ini memiliki **dua backend terpisah** yang menggunakan **satu virtual environment bersama**:

1. **`backend/`** - FastAPI Backend (REST API)
2. **`ai-worker/`** - AI Worker (Computer Vision dengan YOLO)

## 📁 Struktur Proyek

```
ProjectCCTVAi/
├── venv/             # Virtual environment (satu untuk semua)
├── requirements.txt  # Dependencies gabungan
├── setup_venv.ps1    # Script setup venv
│
├── backend/          # FastAPI Backend
│   ├── app/          # Kode aplikasi FastAPI
│   └── requirements.txt  # (referensi saja)
│
└── ai-worker/        # AI Worker (Computer Vision)
    ├── ai_worker.py  # Kode utama AI worker
    └── requirements.txt  # (referensi saja)
```

## 🚀 Setup Virtual Environment

**Hanya perlu setup sekali di root project!**

### **Opsi 1: Menggunakan Script Otomatis (Recommended)**

```powershell
# Di root project
.\setup_venv.ps1
```

### **Opsi 2: Manual Setup**

```powershell
# Di root project
# 1. Buat virtual environment
python -m venv venv

# 2. Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt
```

**Dependencies yang terinstall:**
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT Authentication
- **AI Worker**: Ultralytics (YOLO v8), OpenCV, NumPy, Supervision
- **Shared**: Requests

## 💡 Menggunakan Kedua Backend

### **Menjalankan Backend (FastAPI)**

```powershell
# Terminal 1 - Pastikan venv aktif di root
.\venv\Scripts\Activate.ps1

# Masuk ke folder backend dan jalankan
cd backend
uvicorn app.main:app --reload
```

Backend akan berjalan di: `http://localhost:8000`

### **Menjalankan AI Worker**

```powershell
# Terminal 2 - Pastikan venv aktif di root
.\venv\Scripts\Activate.ps1

# Masuk ke folder ai-worker dan jalankan
cd ai-worker
python ai_worker.py
```

## ⚠️ Catatan Penting

1. **Hanya ada satu venv di root** - Digunakan bersama oleh backend dan ai-worker
2. **Aktifkan venv di root** sebelum menjalankan backend atau ai-worker
3. **Folder `venv/` jangan di-commit** ke Git (pastikan ada `.gitignore`)

## 🔧 Troubleshooting

### Error: "execution of scripts is disabled"

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "python: command not found"

- Install Python 3.8+ dari [python.org](https://www.python.org/downloads/)
- Pastikan Python ditambahkan ke PATH

### Error: "ModuleNotFoundError"

- Pastikan venv aktif (cek dengan `where python`)
- Install ulang: `pip install -r requirements.txt`

## 📚 Dokumentasi Lebih Detail

- **Backend Setup**: Lihat `backend/SETUP.md`
- **AI Worker**: Lihat `ai-worker/SETUP.md`

