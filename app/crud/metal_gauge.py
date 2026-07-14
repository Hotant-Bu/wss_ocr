from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.metal_gauge import MetalGauge, Category, GaugeImage
from app.schemas.metal_gauge import MetalGaugeCreate, MetalGaugeUpdate, CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Category]:
        result = await db.execute(select(Category).where(Category.code == code))
        return result.scalar_one_or_none()
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Category]:
        result = await db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()
    
    async def get_active(self, db: AsyncSession) -> List[Category]:
        result = await db.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.sort_order, Category.name)
        )
        return result.scalars().all()


class CRUDMetalGauge(CRUDBase[MetalGauge, MetalGaugeCreate, MetalGaugeUpdate]):
    async def get(self, db: AsyncSession, id: int) -> Optional[MetalGauge]:
        result = await db.execute(
            select(MetalGauge)
            .where(MetalGauge.id == id)
            .options(
                selectinload(MetalGauge.category),
                selectinload(MetalGauge.images)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_gauge_number(
        self, db: AsyncSession, gauge_number: str
    ) -> Optional[MetalGauge]:
        result = await db.execute(
            select(MetalGauge)
            .where(MetalGauge.gauge_number == gauge_number)
            .options(
                selectinload(MetalGauge.category),
                selectinload(MetalGauge.images)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[MetalGauge]:
        query = select(MetalGauge).options(
            selectinload(MetalGauge.category),
            selectinload(MetalGauge.images)
        )
        
        if category_id is not None:
            query = query.where(MetalGauge.category_id == category_id)
        if status is not None:
            query = query.where(MetalGauge.status == status)
        if is_active is not None:
            query = query.where(MetalGauge.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


category_crud = CRUDCategory(Category)
metal_gauge_crud = CRUDMetalGauge(MetalGauge)
