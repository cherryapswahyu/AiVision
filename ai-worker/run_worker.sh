#!/bin/bash

# ====================================================================
# SCRIPT UTAMA UNTUK MENJALANKAN SEMUA AI WORKER DI SATU CABANG
# Mengambil daftar ID kamera secara dinamis dari FastAPI
# ====================================================================

# --- 1. KONFIGURASI CABANG & FASTAPI ---
# 🚨 GANTI ID CABANG INI (Harus sesuai dengan ID di DB FastAPI)
BRANCH_ID=3 
# Ganti jika FastAPI tidak berjalan di localhost:8000
# FASTAPI_HOST="http://localhost:8000" 

# Nama skrip Python untuk mengambil ID dari API
FETCHER_SCRIPT="fetch_camera_ids.py" 
# Skrip utama AI Worker
WORKER_SCRIPT="ai_worker.py" 

echo "================================================="
echo "Memulai Worker Kamera AI Cabang ID $BRANCH_ID"
echo "Tanggal: $(date)"
echo "================================================="

# --- 2. AKTIVASI LINGKUNGAN VIRTUAL (OPSIONAL) ---
# Jika Anda menggunakan virtual environment, hapus komentar pada baris ini:
# source /path/to/your/venv/bin/activate 

# --- 3. MENGAMBIL DAFTAR ID KAMERA DARI FASTAPI API ---
echo "Memuat daftar ID Kamera untuk Cabang ID $BRANCH_ID dari FastAPI..."

# 🚨 LANGKAH KRUSIAL: Menangkap output dari fetch_camera_ids.py
# Variabel CAMERA_IDS akan berisi string spasi-terpisah, cth: "15 16 17 18"
CAMERA_IDS=$(python $FETCHER_SCRIPT $BRANCH_ID)

if [ -z "$CAMERA_IDS" ]; then
    echo "❌ ERROR: Tidak ada ID Kamera yang didapatkan. Periksa koneksi API atau log fetcher.py."
    exit 1
fi

COUNT_WORKERS=$(echo $CAMERA_IDS | wc -w)
echo "✅ Daftar ID yang ditemukan: $CAMERA_IDS"
echo "Jumlah Worker yang akan diluncurkan: $COUNT_WORKERS kamera."
echo "-------------------------------------------------"

# --- 4. MENJALANKAN SETIAP WORKER DI BACKGROUND (MENGGUNAKAN SCREEN) ---

for CAMERA_ID in $CAMERA_IDS; do
    # Buat nama sesi screen unik untuk worker ini (penting untuk monitoring)
    SESSION_NAME="cam_${CAMERA_ID}_b${BRANCH_ID}"
    LOG_FILE="log_cam_${CAMERA_ID}.txt"
    
    echo "  -> Meluncurkan Worker ID $CAMERA_ID dalam sesi: $SESSION_NAME"
    
    # Perintah: screen -d -m -S [NAMA SESI] [PERINTAH UTAMA]
    # 'screen -d -m' menjalankan sesi di background (detached)
    # 'bash -c "...": Jalankan perintah Python di shell baru
    
    # Perintah Utama: python ai_worker.py [CAMERA_ID] [BRANCH_ID]
    screen -dmS "$SESSION_NAME" bash -c "python $WORKER_SCRIPT $CAMERA_ID $BRANCH_ID > $LOG_FILE 2>&1" &
    
    # Beri jeda sebentar antar peluncuran (mengurangi beban startup CPU)
    sleep 1
done

echo "================================================="
echo "✅ Semua $COUNT_WORKERS Worker telah diluncurkan di background."
echo "Untuk melihat sesi: ketik 'screen -ls'"
echo "Untuk melihat log: ketik 'tail -f log_cam_15.txt'"
echo "================================================="