from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import PermissionCreate, PermissionResponse
from app.schemas.common import PaginatedResponse
from app.crud.user import permission_crud
from app.core.deps import PermissionChecker
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[PermissionResponse])
async def list_permissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["permission:read"]))
):
    skip = (page - 1) * page_size
    permissions = await permission_crud.get_multi(db, skip=skip, limit=page_size)
    total = await permission_crud.count(db)
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=permissions,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_in: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["permission:create"]))
):
    permission = await permission_crud.get_by_name(db, name=permission_in.name)
    if permission:
        raise HTTPException(status_code=400, detail="权限名称已存在")
    return await permission_crud.create(db, obj_in=permission_in)


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["permission:read"]))
):
    permission = await permission_crud.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return permission


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["permission:delete"]))
):
    permission = await permission_crud.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    await permission_crud.delete(db, id=permission_id)
