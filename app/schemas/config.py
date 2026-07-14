from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConfigBase(BaseModel):
    key: str = Field(..., max_length=100)
    value: Optional[str] = None
    data_type: str = Field(default="string", max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_system: bool = False
    is_active: bool = True


class ConfigCreate(ConfigBase):
    pass


class ConfigUpdate(BaseModel):
    value: Optional[str] = None
    data_type: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ConfigResponse(ConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
