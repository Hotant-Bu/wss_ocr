from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.crud.base import CRUDBase
from app.models.audit_log import AuditLog
from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    pass


class CRUDAuditLog(CRUDBase[AuditLog, AuditLogCreate, AuditLogCreate]):
    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_resource(
        self,
        db: AsyncSession,
        resource: str,
        resource_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        query = select(AuditLog).where(AuditLog.resource == resource)
        
        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)
        
        query = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_recent(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        result = await db.execute(
            select(AuditLog)
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


audit_log_crud = CRUDAuditLog(AuditLog)
