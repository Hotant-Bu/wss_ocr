from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from app.database import Base


class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    camera_id = Column(String(100), unique=True, nullable=False, index=True)
    ip_address = Column(String(50))
    port = Column(Integer)
    rtsp_url = Column(String(500))
    username = Column(String(100))
    password = Column(String(255))
    location = Column(String(200))
    manufacturer = Column(String(100))
    model = Column(String(100))
    resolution = Column(String(50))
    fps = Column(Integer)
    status = Column(String(50), default="offline")
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
