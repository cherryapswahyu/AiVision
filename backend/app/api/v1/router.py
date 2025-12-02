from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from starlette.responses import StreamingResponse
import io
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models
from ..core.database import get_db
from ..schemas import CameraConfig
from ..core.config import settings

router = APIRouter(prefix="/api/v1", tags=["AI Worker & Dashboard"])

# --- HELPER FUNCTIONS FOR AUTH ---
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

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

@router.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint Login untuk mendapatkan Access dan Refresh Token."""
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/auth/refresh", response_model=schemas.Token, tags=["Auth"])
def refresh_token(token_data: schemas.TokenData, db: Session = Depends(get_db)):
    """Endpoint untuk menukar Refresh Token dengan Access Token baru."""
    # Logic: Decode token_data.username dari refresh token
    username = token_data.username # Asumsi token decoding sudah dilakukan
    user = crud.get_user_by_username(db, username=username)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": None} # Refresh Token tidak berubah

# --- NEW ENDPOINT: CAMERA SNAPSHOT ---

@router.get("/cameras/{camera_id}/snapshot", tags=["Camera Control"])
def get_camera_snapshot(camera_id: int, db: Session = Depends(get_db)):
    """Mengambil snapshot (gambar diam JPEG) dari RTSP stream."""
    image_bytes = crud.get_camera_snapshot_data(db, camera_id)
    
    if image_bytes is None:
        raise HTTPException(status_code=503, detail="Could not retrieve snapshot (Camera offline or not accessible)")
    
    # Menggunakan StreamingResponse untuk mengirim byte gambar
    return StreamingResponse(
        io.BytesIO(image_bytes),
        media_type="image/jpeg"
    )

# --- ENDPOINT UPDATE CAMERA SETTINGS ---

@router.put("/cameras/{camera_id}", response_model=schemas.CameraConfig, tags=["Camera Control"])
def update_camera_settings(
    camera_id: int,
    camera_update: schemas.CameraUpdate,
    db: Session = Depends(get_db)
):
    """Update konfigurasi kamera (rtsp_url dan roi_settings)."""
    db_camera = crud.update_camera(db, camera_id=camera_id, camera_update=camera_update)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {
        **db_camera.__dict__,
        "branch_id": db_camera.branch_id
    }