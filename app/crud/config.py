from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.config import Config
from app.schemas.config import ConfigCreate, ConfigUpdate


class CRUDConfig(CRUDBase[Config, ConfigCreate, ConfigUpdate]):
    async def get_by_key(self, db: AsyncSession, key: str) -> Optional[Config]:
        result = await db.execute(select(Config).where(Config.key == key))
        return result.scalar_one_or_none()
    
    async def get_by_category(self, db: AsyncSession, category: str) -> List[Config]:
        result = await db.execute(
            select(Config)
            .where(Config.category == category, Config.is_active == True)
            .order_by(Config.key)
        )
        return result.scalars().all()
    
    async def get_active(self, db: AsyncSession) -> List[Config]:
        result = await db.execute(
            select(Config)
            .where(Config.is_active == True)
            .order_by(Config.category, Config.key)
        )
        return result.scalars().all()


config_crud = CRUDConfig(Config)
