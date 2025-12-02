# Setup Guide - AI Restaurant Backend

## 📦 Virtual Environment (venv)

### **Satu Venv untuk Semua**

Proyek ini menggunakan **satu virtual environment** di root project (`ProjectCCTVAi/venv/`) yang digunakan bersama oleh:

- Backend FastAPI
- AI Worker

**Setup venv dilakukan di root project, bukan di folder backend!**

---

## 🚀 Cara Setup (Windows PowerShell)

### **Setup di Root Project**

```powershell
# Kembali ke root project
cd ..

# Jalankan script setup
.\setup_venv.ps1
```

Atau manual:

```powershell
# Di root project
# 1. Buat virtual environment
python -m venv venv

# 2. Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies (dari root)
pip install -r requirements.txt
```

---

## ✅ Verifikasi Setup

Setelah setup, pastikan venv aktif (akan muncul `(venv)` di prompt):

```powershell
# Cek Python path (harus menunjuk ke venv)
python --version
where python  # Harus menunjuk ke .\venv\Scripts\python.exe

# Cek packages terinstall
pip list
```

---

## 🏃 Menjalankan Aplikasi

### **Cara 1: Menggunakan Script (Paling Mudah)**

```powershell
# Pastikan venv aktif di root project
cd ..  # Kembali ke root
.\venv\Scripts\Activate.ps1

# Masuk ke folder backend
cd backend

# Jalankan dengan script PowerShell
.\run.ps1
```

Atau dengan Python:

```powershell
python run.py
```

### **Cara 2: Menggunakan Uvicorn Langsung**

```powershell
# Pastikan venv aktif dan berada di folder backend
cd backend
.\..\venv\Scripts\Activate.ps1  # Aktifkan venv dari root

# Jalankan server
uvicorn app.main:app --reload
```

**PENTING:** Pastikan Anda berada di folder `backend` saat menjalankan uvicorn, bukan di root project!

Aplikasi akan berjalan di: `http://localhost:8000`

- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/`

---

## 📝 Catatan Penting

1. **Aktifkan venv setiap kali membuka terminal baru**

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Deactivate venv** (jika perlu)

   ```powershell
   deactivate
   ```

3. **Jika ada error "execution of scripts is disabled"**

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Folder `venv/` jangan di-commit ke Git**
   - Pastikan ada `.gitignore` dengan isi: `venv/`

---

## 🔧 Troubleshooting

### Error: "python: command not found"

- Install Python 3.8+ dari [python.org](https://www.python.org/downloads/)
- Pastikan Python ditambahkan ke PATH

### Error: "pip: command not found"

- Gunakan: `python -m pip` instead of `pip`

### Error: "ModuleNotFoundError"

- Pastikan venv aktif
- Install ulang: `pip install -r requirements.txt`
