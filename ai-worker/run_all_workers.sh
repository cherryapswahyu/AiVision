#!/bin/bash

# --- 1. KONFIGURASI CABANG ---
# 🚨 GANTI ID CABANG INI (Harus sesuai dengan ID di DB FastAPI)
BRANCH_ID=3 
FASTAPI_HOST="http://localhost:8000" # Ganti jika FastAPI ada di server lain

# Nama skrip Python untuk mengambil ID dari API
FETCHER_SCRIPT="fetch_camera_ids.py" 
# Skrip utama AI Worker
WORKER_SCRIPT="ai_worker.py" 

echo "================================================="
echo "Memulai Worker Kamera AI Cabang ID $BRANCH_ID"
echo "================================================="

# --- 2. AKTIVASI LINGKUNGAN VIRTUAL (OPSIONAL TAPI SANGAT DISARANKAN) ---
# Jika Anda menggunakan virtual environment, hapus komentar di baris di bawah ini:
# source /path/to/your/venv/bin/activate 


# --- 3. MENGAMBIL DAFTAR ID KAMERA DARI FASTAPI API ---
echo "Memuat daftar ID Kamera untuk Cabang ID $BRANCH_ID dari FastAPI..."

# Panggil skrip Python fetcher untuk mendapatkan daftar ID kamera
# Output akan berupa string spasi-terpisah, cth: "15 16 17 18"
# Jika fetcher script ada di folder yang berbeda, ubah path-nya.
CAMERA_IDS=$(python $FETCHER_SCRIPT $BRANCH_ID)

if [ -z "$CAMERA_IDS" ]; then
    echo "❌ ERROR: Tidak ada ID Kamera yang didapatkan. Pastikan API running dan koneksi benar."
    exit 1
fi

echo "✅ Daftar ID yang ditemukan: $CAMERA_IDS"
echo "Jumlah Worker yang akan diluncurkan: $(echo $CAMERA_IDS | wc -w) kamera."
echo "-------------------------------------------------"

# --- 4. MENJALANKAN SETIAP WORKER DI BACKGROUND (MENGGUNAKAN screen) ---

for CAMERA_ID in $CAMERA_IDS; do
    # Buat nama sesi screen unik untuk worker ini (penting untuk monitoring)
    SESSION_NAME="cam_${CAMERA_ID}_b${BRANCH_ID}"
    LOG_FILE="log_cam_${CAMERA_ID}.txt"
    
    echo "  -> Meluncurkan Worker ID $CAMERA_ID dalam sesi: $SESSION_NAME"
    
    # Perintah: screen -d -m -S [NAMA SESI] [PERINTAH UTAMA]
    # -d -m: Jalankan di background (mode detached)
    # -S: Beri nama sesi
    # bash -c "...": Jalankan perintah di shell baru dan redirect output ke file log
    
    # Perintah Utama: python ai_worker.py [CAMERA_ID] [BRANCH_ID]
    screen -dmS "$SESSION_NAME" bash -c "python $WORKER_SCRIPT $CAMERA_ID $BRANCH_ID > $LOG_FILE 2>&1" &
    
    # Beri jeda sebentar antar peluncuran (mengurangi beban startup)
    sleep 1
done

echo "================================================="
echo "✅ Semua Worker telah diluncurkan di background."
echo "Untuk memonitor: ketik 'screen -ls'"
echo "Untuk masuk ke sesi: ketik 'screen -r cam_15_b3'"
echo "================================================="