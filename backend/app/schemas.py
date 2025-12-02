# /app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# --- CAMERA CONFIG (OUTPUT KE AI WORKER) ---

class CameraConfig(BaseModel):
    id: int
    branch_id: int
    name: str
    area_type: str
    rtsp_url: str
    roi_settings: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True

# --- BRANCH CONFIG (OUTPUT KE AI WORKER) ---
class BranchConfig(BaseModel):
    id: int
    name: str
    uniform_schedule: Dict[str, Any] = Field(default_factory=dict)
    total_seating_capacity: int
    
    class Config:
        from_attributes = True

# --- LOGGING DARI AI WORKER (INPUT) ---
class DetectionLogCreate(BaseModel):
    """Schema yang diterima dari POST AI Worker."""
    camera_id: int = Field(alias='camera') 
    analytics_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        
# --- DATA UNTUK DASHBOARD (OUTPUT KE FRONTEND) ---
class CameraDashboard(CameraConfig):
    status: str
    latest_log: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        # /app/schemas.py (Tambahkan ini di bagian bawah)

# --- AUTHENTICATION SCHEMAS ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # 🚨 PENTING: Kirim refresh token ke AI Worker
    refresh_token: Optional[str] = None 

class TokenData(BaseModel):
    username: Optional[str] = None

# --- CAMERA UPDATE SCHEMA ---
class CameraUpdate(BaseModel):
    """Schema untuk update konfigurasi kamera."""
    rtsp_url: Optional[str] = None
    roi_settings: Optional[Dict[str, Any]] = None