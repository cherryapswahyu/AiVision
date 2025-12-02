# /app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

# --- CRUD BRANCH (CONFIG UNTUK AI WORKER) ---

def get_branch(db: Session, branch_id: int):
    return db.query(models.Branch).filter(models.Branch.id == branch_id).first()

# --- CRUD CAMERA (CONFIG UNTUK AI WORKER/FRONTEND) ---

def get_camera(db: Session, camera_id: int):
    # Mengambil kamera berdasarkan ID
    return db.query(models.Camera).filter(models.Camera.id == camera_id).first()

# --- CRUD LOG (DARI AI WORKER) ---

def create_detection_log(db: Session, log: schemas.DetectionLogCreate):
    # 1. Buat log baru
    db_log = models.DetectionLog(
        camera_id=log.camera_id, 
        analytics_data=log.analytics_data
    )
    db.add(db_log)
    
    # 2. Update Heartbeat & Status kamera
    db.query(models.Camera).filter(models.Camera.id == log.camera_id).update({
        models.Camera.status: 'ONLINE',
        models.Camera.last_heartbeat: datetime.utcnow()
    })
    
    db.commit()
    return db_log

def get_cameras_by_branch(db: Session, branch_id: int):
    """Mengambil semua kamera yang terdaftar di satu cabang."""
    return db.query(models.Camera).filter(models.Camera.branch_id == branch_id).all()