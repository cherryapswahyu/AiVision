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
        orm_mode = True

# --- BRANCH CONFIG (OUTPUT KE AI WORKER) ---
class BranchConfig(BaseModel):
    id: int
    name: str
    uniform_schedule: Dict[str, Any] = Field(default_factory=dict)
    total_seating_capacity: int
    
    class Config:
        orm_mode = True

# --- LOGGING DARI AI WORKER (INPUT) ---
class DetectionLogCreate(BaseModel):
    """Schema yang diterima dari POST AI Worker."""
    camera_id: int = Field(alias='camera') 
    analytics_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_population_by_field_name = True
        
# --- DATA UNTUK DASHBOARD (OUTPUT KE FRONTEND) ---
class CameraDashboard(CameraConfig):
    status: str
    latest_log: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True