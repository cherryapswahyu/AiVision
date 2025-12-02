# Script PowerShell untuk Setup Virtual Environment
# Jalankan dengan: .\setup_venv.ps1

Write-Host "=== Setup Virtual Environment untuk AI Restaurant Backend ===" -ForegroundColor Green

# 1. Cek apakah Python sudah terinstall
Write-Host "`n[1/4] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python tidak ditemukan! Silakan install Python 3.8+ terlebih dahulu." -ForegroundColor Red
    exit 1
}
Write-Host "Python ditemukan: $pythonVersion" -ForegroundColor Green

# 2. Buat virtual environment
Write-Host "`n[2/4] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment sudah ada. Menghapus yang lama..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Gagal membuat virtual environment!" -ForegroundColor Red
    exit 1
}
Write-Host "Virtual environment berhasil dibuat di folder 'venv'" -ForegroundColor Green

# 3. Aktifkan virtual environment
Write-Host "`n[3/4] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Gagal mengaktifkan venv secara otomatis." -ForegroundColor Yellow
    Write-Host "Silakan jalankan manual: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}

# 4. Upgrade pip
Write-Host "`n[4/4] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 5. Install dependencies
Write-Host "`n[5/5] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Gagal install dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Setup Selesai! ===" -ForegroundColor Green
Write-Host "`nUntuk mengaktifkan virtual environment di sesi berikutnya, jalankan:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "`nUntuk menjalankan aplikasi:" -ForegroundColor Cyan
Write-Host "  uvicorn app.main:app --reload" -ForegroundColor White

