from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    parent = relationship("Category", remote_side=[id], backref="children")
    metal_gauges = relationship("MetalGauge", back_populates="category")


class MetalGauge(Base):
    __tablename__ = "metal_gauges"
    
    id = Column(Integer, primary_key=True, index=True)
    gauge_number = Column(String(100), unique=True, nullable=False, index=True)
    gauge_type = Column(String(100), nullable=False)
    range_min = Column(Float)
    range_max = Column(Float)
    range_unit = Column(String(20))
    installation_location = Column(Text)
    manufacturer = Column(String(200))
    model = Column(String(100))
    serial_number = Column(String(100))
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    status = Column(String(50), default="active")
    calibration_date = Column(DateTime)
    next_calibration_date = Column(DateTime)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="metal_gauges")
    images = relationship("GaugeImage", back_populates="metal_gauge", cascade="all, delete-orphan")


class GaugeImage(Base):
    __tablename__ = "gauge_images"
    
    id = Column(Integer, primary_key=True, index=True)
    metal_gauge_id = Column(Integer, ForeignKey("metal_gauges.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    width = Column(Integer)
    height = Column(Integer)
    is_primary = Column(Boolean, default=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    metal_gauge = relationship("MetalGauge", back_populates="images")
