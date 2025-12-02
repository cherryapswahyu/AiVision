# /app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from .core.database import Base
from datetime import datetime
from sqlalchemy.sql import func

# ==========================================
# 1. CORE: BRANCH
# ==========================================

class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    
    # DYNAMIC: JADWAL WARNA SERAGAM
    uniform_schedule = Column(JSON, default=dict) 
    total_seating_capacity = Column(Integer, default=100)
    
    cameras = relationship("Camera", back_populates="branch")
    
# ==========================================
# 2. DEVICE: CAMERA
# ==========================================

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String, nullable=False)
    area_type = Column(String, nullable=False) # ENTRANCE, DINING, etc.
    
    # DYNAMIC: URL STREAM
    rtsp_url = Column(String, nullable=False)
    
    # DYNAMIC: KOORDINAT AREA (ROI)
    roi_settings = Column(JSON, default=dict)
    
    status = Column(String, default='OFFLINE')
    last_heartbeat = Column(DateTime, nullable=True)
    
    branch = relationship("Branch", back_populates="cameras")
    logs = relationship("DetectionLog", back_populates="camera", order_by="DetectionLog.timestamp.desc()")

# ==========================================
# 3. DATA: DETECTION LOG
# ==========================================

class DetectionLog(Base):
    __tablename__ = "detection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # DYNAMIC: DATA ANALITIK
    analytics_data = Column(JSON, default=dict)

    camera = relationship("Camera", back_populates="logs")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

# ==========================================
# 5. SYSTEM ALERT (Opsional: untuk sidebar)
# ==========================================

class SystemAlert(Base):
    __tablename__ = "system_alerts"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    message = Column(String, nullable=False)
    severity = Column(String, default='INFO') # INFO, WARNING, CRITICAL
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)