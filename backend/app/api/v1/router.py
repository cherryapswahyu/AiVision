# /app/api/v1/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models
from ..core.database import get_db
from ..schemas import CameraConfig

router = APIRouter(prefix="/api/v1", tags=["AI Worker & Dashboard"])

# --- ENDPOINT KONFIGURASI UNTUK AI WORKER ---

@router.get("/branches/{branch_id}", response_model=schemas.BranchConfig)
def read_branch_config(branch_id: int, db: Session = Depends(get_db)):
    """Mengambil konfigurasi Cabang (Jadwal Seragam) untuk AI Worker."""
    db_branch = crud.get_branch(db, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return db_branch

@router.get("/cameras/{camera_id}", response_model=schemas.CameraConfig)
def read_camera_config(camera_id: int, db: Session = Depends(get_db)):
    """Mengambil konfigurasi Kamera (RTSP, ROI) beserta branch_id untuk AI Worker."""
    db_camera = crud.get_camera(db, camera_id=camera_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Mengembalikan data dengan field branch_id yang dihitung dari relasi
    return {
        **db_camera.__dict__,
        "branch_id": db_camera.branch_id
    }

# --- ENDPOINT LOGGING DARI AI WORKER ---

@router.post("/logs/", status_code=201)
def create_log(log: schemas.DetectionLogCreate, db: Session = Depends(get_db)):
    """Endpoint untuk AI Worker mengirim hasil deteksi (log & heartbeat)."""
    crud.create_detection_log(db, log=log)
    return {"message": "Log received and heartbeat updated"}

# --- ENDPOINT DASHBOARD FRONTEND ---

@router.get("/dashboard/cameras/", response_model=List[schemas.CameraDashboard])
def get_dashboard_data(db: Session = Depends(get_db)):
    """Mengambil semua data kamera beserta log terbarunya untuk dashboard."""
    # Logic untuk Dashboard di CRUD bisa lebih kompleks (misal: agregasi)
    cameras = db.query(models.Camera).all()
    dashboard_data = []
    
    for cam in cameras:
        latest_log = cam.logs[0].analytics_data if cam.logs else None
        cam_schema = schemas.CameraDashboard.from_orm(cam)
        cam_schema.latest_log = latest_log
        dashboard_data.append(cam_schema)
        
    return dashboard_data
@router.get("/branches/{branch_id}/cameras", response_model=List[schemas.CameraConfig])
def read_branch_cameras(branch_id: int, db: Session = Depends(get_db)):
    """Mengambil semua daftar kamera milik satu cabang."""
    cameras = crud.get_cameras_by_branch(db, branch_id=branch_id)
    if not cameras:
        raise HTTPException(status_code=404, detail="No cameras found for this branch")
    return cameras