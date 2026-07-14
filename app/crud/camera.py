from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


class CRUDCamera(CRUDBase[Camera, CameraCreate, CameraUpdate]):
    async def get_by_camera_id(self, db: AsyncSession, camera_id: str) -> Optional[Camera]:
        result = await db.execute(select(Camera).where(Camera.camera_id == camera_id))
        return result.scalar_one_or_none()
    
    async def get_active(self, db: AsyncSession) -> List[Camera]:
        result = await db.execute(
            select(Camera)
            .where(Camera.is_active == True)
            .order_by(Camera.name)
        )
        return result.scalars().all()
    
    async def get_by_status(self, db: AsyncSession, status: str) -> List[Camera]:
        result = await db.execute(
            select(Camera)
            .where(Camera.status == status)
            .order_by(Camera.name)
        )
        return result.scalars().all()


camera_crud = CRUDCamera(Camera)
