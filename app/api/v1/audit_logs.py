from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.audit_log import AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.crud.audit_log import audit_log_crud
from app.core.deps import PermissionChecker
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    resource: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["audit_log:read"]))
):
    skip = (page - 1) * page_size
    
    if user_id:
        logs = await audit_log_crud.get_by_user(db, user_id=user_id, skip=skip, limit=page_size)
        total = await audit_log_crud.count(db, filters={"user_id": user_id})
    elif resource:
        logs = await audit_log_crud.get_by_resource(db, resource=resource, skip=skip, limit=page_size)
        total = await audit_log_crud.count(db, filters={"resource": resource})
    else:
        logs = await audit_log_crud.get_recent(db, skip=skip, limit=page_size)
        total = await audit_log_crud.count(db)
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=logs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["audit_log:read"]))
):
    log = await audit_log_crud.get(db, id=log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return log
