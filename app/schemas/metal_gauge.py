from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GaugeImageResponse(BaseModel):
    id: int
    filename: str
    original_filename: Optional[str]
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    width: Optional[int]
    height: Optional[int]
    is_primary: bool
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MetalGaugeBase(BaseModel):
    gauge_number: str = Field(..., max_length=100)
    gauge_type: str = Field(..., max_length=100)
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    range_unit: Optional[str] = Field(None, max_length=20)
    installation_location: Optional[str] = None
    manufacturer: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    status: str = Field(default="active", max_length=50)
    calibration_date: Optional[datetime] = None
    next_calibration_date: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: bool = True


class MetalGaugeCreate(MetalGaugeBase):
    pass


class MetalGaugeUpdate(BaseModel):
    gauge_number: Optional[str] = Field(None, max_length=100)
    gauge_type: Optional[str] = Field(None, max_length=100)
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    range_unit: Optional[str] = Field(None, max_length=20)
    installation_location: Optional[str] = None
    manufacturer: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    status: Optional[str] = Field(None, max_length=50)
    calibration_date: Optional[datetime] = None
    next_calibration_date: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class MetalGaugeResponse(MetalGaugeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    images: List[GaugeImageResponse] = []
    
    class Config:
        from_attributes = True
