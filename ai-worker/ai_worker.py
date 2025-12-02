import sys
import time
import requests
import datetime
import numpy as np
import cv2
import supervision as sv
from ultralytics import YOLO
import os

API_URL_ROOT = os.environ.get("FASTAPI_API_URL", "http://localhost:8000/api/v1/") 
ACCESS_TOKEN = os.environ.get("JWT_ACCESS_TOKEN", "fallback_token")

# Global State: Menyimpan status antar frame (diperlukan untuk state machine)
QUEUE_ENTRY_TIMES = {} # {tracker_id: timestamp_masuk}
TABLE_STATES = {}      # {table_id: 'DIRTY' / 'AVAILABLE' / 'OCCUPIED' / 'CLEANING'}
LAST_CHECKED_DAY = None # Untuk logika pergantian jadwal seragam

# --- FUNGSI HELPER API & KONFIGURASI ---

def load_config_from_api(camera_id, branch_id):
    """Mengambil semua konfigurasi dinamis (RTSP, ROI, Jadwal) dari FastAPI."""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    try:
        # Ambil konfigurasi Kamera (termasuk ROI)
        cam_res = requests.get(f"{API_URL_ROOT}cameras/{camera_id}", headers=headers, timeout=5).json()
        
        # Ambil Jadwal Seragam dari Cabang
        branch_res = requests.get(f"{API_URL_ROOT}branches/{branch_id}", headers=headers, timeout=5).json()
        
        config = cam_res
        config['uniform_schedule'] = branch_res.get('uniform_schedule', {})
        config['total_seating_capacity'] = branch_res.get('total_seating_capacity', 100)
        
        print(f"✅ Konfigurasi Kamera {camera_id} dimuat sukses.")
        return config
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Gagal memuat konfigurasi dari API: {e}")
        return None

def send_analytics_data(camera_id, analytics_data):
    """Mengirim hasil deteksi ke FastAPI."""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"camera": camera_id, "analytics_data": analytics_data}
    
    try:
        # Endpoint POST /api/v1/logs/ yang juga mentrigger heartbeat
        response = requests.post(f"{API_URL_ROOT}logs/", json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        # Menangani error koneksi jika FastAPI down
        return False

# --- FUNGSI LOGIKA DETEKSI PERAN (STAFF vs PELANGGAN) ---

def is_staff(frame, box, schedule):
    """Menentukan Staff berdasarkan Jadwal Warna dinamis."""
    global LAST_CHECKED_DAY
    
    current_day = datetime.datetime.now().strftime('%A').upper()
    color_config = schedule.get(current_day)
    
    if not color_config or 'lower' not in color_config or 'upper' not in color_config:
        return False
        
    lower_hsv = np.array(color_config['lower'])
    upper_hsv = np.array(color_config['upper'])
    
    x1, y1, x2, y2 = map(int, box)
    
    # Cek warna di area torso (badan)
    try:
        # Ambil bagian tengah tubuh 
        torso_img = frame[int(y1*0.2):int(y2*0.6), int(x1*0.2):int(x2*0.8)]
    except IndexError:
        return False

    if torso_img.size == 0: return False
    
    # Konversi ke HSV dan hitung mask
    hsv = cv2.cvtColor(torso_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    ratio = cv2.countNonZero(mask) / (torso_img.shape[0] * torso_img.shape[1] + 1e-6)
    
    return ratio > 0.3 # Threshold 30% area torso cocok dengan warna seragam

# --- FUNGSI LOGIKA PER HITUNGAN AREA (4 TIPE KAMERA) ---

def process_entrance_camera(detections, active_zone, tracker):
    """Pintu Masuk: Line Crossing Counter"""
    detections = tracker.update_with_detections(detections)
    active_zone.trigger(detections)
    
    return {
        "people_in": active_zone.in_count,
        "people_out": active_zone.out_count,
    }

def process_dining_camera(frame, detections, roi_settings, schedule):
    """Area Makan: Multi-Polygon Meja & Status Kotor/Bersih (State Machine)"""
    global TABLE_STATES 
    
    total_customers = 0
    tables_data = []

    for zone_cfg in roi_settings.get('zones', []):
        points = np.array(zone_cfg['points'])
        table_zone = sv.PolygonZone(polygon=points, frame_resolution_wh=(1280, 720))
        
        people_in_zone = detections[table_zone.trigger(detections)]
        staff_count = 0
        customer_count = 0
        
        # Bedakan Staff/Customer
        for box in people_in_zone.xyxy:
            if is_staff(frame, box, schedule):
                staff_count += 1
            else:
                customer_count += 1
                
        table_id = zone_cfg['id']
        current_status = TABLE_STATES.get(table_id, 'AVAILABLE')
        
        # LOGIKA PERUBAHAN STATUS MEJA
        new_status = current_status
        if customer_count > 0:
            new_status = 'OCCUPIED'
        elif staff_count > 0 and current_status == 'DIRTY':
            new_status = 'CLEANING'
        elif staff_count == 0 and current_status == 'CLEANING':
             new_status = 'AVAILABLE'
        elif customer_count == 0 and current_status == 'OCCUPIED':
            new_status = 'DIRTY'

        TABLE_STATES[table_id] = new_status
        total_customers += customer_count
        
        tables_data.append({
            "id": table_id, "status": new_status, "people_count": customer_count, 
            "capacity": zone_cfg.get('capacity', 4)
        })

    return {"total_customers": total_customers, "tables": tables_data}

def process_cashier_camera(detections, roi_settings, tracker):
    """Kasir: Antrian & Waktu Tunggu (Tracking ID)"""
    global QUEUE_ENTRY_TIMES
    
    points = np.array(roi_settings.get('points'))
    if points.ndim != 2: return {"queue_length": 0, "wait_time_avg": 0}
        
    queue_zone = sv.PolygonZone(polygon=points, frame_resolution_wh=(1280, 720))
    detections = tracker.update_with_detections(detections)
    people_in_queue = detections[queue_zone.trigger(detections)]
    
    current_time = time.time()
    total_wait_time = 0
    
    for track_id in people_in_queue.tracker_id:
        if track_id not in QUEUE_ENTRY_TIMES:
            QUEUE_ENTRY_TIMES[track_id] = current_time
        total_wait_time += (current_time - QUEUE_ENTRY_TIMES[track_id])
        
    active_ids = set(people_in_queue.tracker_id)
    QUEUE_ENTRY_TIMES = {k: v for k, v in QUEUE_ENTRY_TIMES.items() if k in active_ids}
    
    queue_length = len(people_in_queue)
    avg_wait = int(total_wait_time / queue_length) if queue_length > 0 else 0

    return {"queue_length": queue_length, "wait_time_avg": avg_wait}

def process_kitchen_camera(frame, detections, roi_settings, schedule):
    """Dapur: Deteksi Staf Aktif di Area Kerja"""
    points = np.array(roi_settings.get('points'))
    if points.ndim != 2: return {"staff_active_count": 0, "staff_total_scheduled": 6}
        
    kitchen_zone = sv.PolygonZone(polygon=points, frame_resolution_wh=(1280, 720))
    people_in_zone = detections[kitchen_zone.trigger(detections)]
    
    active_staff_count = 0
    for box in people_in_zone.xyxy:
        if is_staff(frame, box, schedule):
            active_staff_count += 1
            
    total_scheduled = roi_settings.get('total_staff', 6)
    
    return {"staff_active_count": active_staff_count, "staff_total_scheduled": total_scheduled}

# --- FUNGSI UTAMA WORKER ---

def run_worker(camera_id, branch_id):
    """Fungsi utama yang menjalankan loop deteksi."""
    config = load_config_from_api(camera_id, branch_id)
    if not config: return

    rtsp_url = config['rtsp_url']
    area_type = config['area_type']
    roi_settings = config['roi_settings']
    uniform_schedule = config['uniform_schedule']
    
    # INISIALISASI AI TOOLS
    model = YOLO('yolov8n.pt') 
    tracker = sv.ByteTrack()
    
    # INISIALISASI ZONE/LINE DINAMIS
    active_zone = None
    if area_type == 'ENTRANCE' and roi_settings.get('type') == 'LINE':
        start = sv.Point(*roi_settings['start'])
        end = sv.Point(*roi_settings['end'])
        active_zone = sv.LineZone(start=start, end=end)
    
    cap = cv2.VideoCapture(rtsp_url)
    last_data_send = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret: 
            # Auto-reconnect logic
            time.sleep(5)
            cap = cv2.VideoCapture(rtsp_url)
            continue
        
        # Standarisasi Resolusi (Penting untuk konsistensi koordinat ROI)
        frame = cv2.resize(frame, (1280, 720)) 
        
        # DETEKSI YOLO
        results = model(frame, classes=[0], verbose=False)[0] # Hanya deteksi 'person'
        detections = sv.Detections.from_ultralytics(results)

        # PROSES ANALISIS SESUAI TIPE AREA
        analytics_data = {}
        if area_type == 'ENTRANCE' and active_zone:
            analytics_data = process_entrance_camera(detections, roi_settings, active_zone, tracker)
        elif area_type == 'DINING':
            analytics_data = process_dining_camera(frame, detections, roi_settings, uniform_schedule)
        elif area_type == 'CASHIER':
            analytics_data = process_cashier_camera(detections, roi_settings, tracker)
        elif area_type == 'KITCHEN':
            analytics_data = process_kitchen_camera(frame, detections, roi_settings, uniform_schedule)
        
        # KIRIM DATA KE FASTAPI
        if time.time() - last_data_send > 5: # Kirim setiap 5 detik
            send_analytics_data(camera_id, analytics_data)
            last_data_send = time.time()
        
        # cv2.imshow(f"Kamera {camera_id}", frame) # Hapus saat deployment
        if cv2.waitKey(1) == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Penggunaan: python ai_worker.py [CAMERA_ID] [BRANCH_ID]")
        sys.exit(1)
    
    # Ambil ID dari argumen command line
    camera_id = int(sys.argv[1])
    branch_id = int(sys.argv[2])
    
    run_worker(camera_id, branch_id)