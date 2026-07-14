from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CameraBase(BaseModel):
    name: str = Field(..., max_length=100)
    camera_id: str = Field(..., max_length=100)
    ip_address: Optional[str] = Field(None, max_length=50)
    port: Optional[int] = None
    rtsp_url: Optional[str] = Field(None, max_length=500)
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=200)
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    resolution: Optional[str] = Field(None, max_length=50)
    fps: Optional[int] = None
    status: str = Field(default="offline", max_length=50)
    is_active: bool = True
    notes: Optional[str] = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    camera_id: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=50)
    port: Optional[int] = None
    rtsp_url: Optional[str] = Field(None, max_length=500)
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=200)
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    resolution: Optional[str] = Field(None, max_length=50)
    fps: Optional[int] = None
    status: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
