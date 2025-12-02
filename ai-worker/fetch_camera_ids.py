import sys
import requests
import json

# --- PENGATURAN API ---
# 🚨 GANTI DENGAN ALAMAT FASTAPI ANDA
API_URL_ROOT = "http://localhost:8000/api/v1/" 
# 🚨 GANTI DENGAN JWT ACCESS TOKEN YANG VALID
ACCESS_TOKEN = "YOUR_FASTAPI_JWT_TOKEN" 

def fetch_camera_ids(branch_id: int):
    """
    Mengambil daftar semua ID kamera yang terdaftar di database untuk cabang tertentu 
    melalui endpoint FastAPI.
    """
    try:
        # Endpoint yang telah kita buat di FastAPI: /api/v1/branches/{branch_id}/cameras
        url = f"{API_URL_ROOT}branches/{branch_id}/cameras"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Mengaktifkan pengecualian untuk status kode 4xx atau 5xx
        
        data = response.json()
        
        # Ambil semua 'id' kamera dari respons JSON
        # Output: [15, 16, 17, ...]
        camera_ids = [str(cam.get('id')) for cam in data if cam.get('id') is not None]
        
        # Cetak ID ke standard output, dipisahkan spasi. 
        # Shell script akan menangkap output ini.
        print(" ".join(camera_ids))
        
    except requests.exceptions.HTTPError as e:
        # Menangani jika cabang tidak ditemukan atau tidak ada kamera
        if response.status_code == 404:
            print(f"ERROR 404: Tidak ada kamera ditemukan untuk Cabang ID {branch_id}.", file=sys.stderr)
        else:
            print(f"ERROR HTTP {response.status_code}: Gagal mengambil ID kamera: {e}", file=sys.stderr)
        sys.exit(1)
        
    except requests.exceptions.RequestException as e:
        # Menangani kegagalan koneksi (misal server down)
        print(f"ERROR KONEKSI: Gagal terhubung ke FastAPI di {API_URL_ROOT}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: python fetch_camera_ids.py [BRANCH_ID]", file=sys.stderr)
        sys.exit(1)
        
    # Ambil ID Cabang dari argumen command line
    branch_id = int(sys.argv[1])
    
    fetch_camera_ids(branch_id)