from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.common import PaginatedResponse
from app.crud.user import role_crud
from app.core.deps import PermissionChecker
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[RoleResponse])
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["role:read"]))
):
    skip = (page - 1) * page_size
    roles = await role_crud.get_multi(db, skip=skip, limit=page_size)
    total = await role_crud.count(db)
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=roles,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["role:create"]))
):
    role = await role_crud.get_by_name(db, name=role_in.name)
    if role:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    return await role_crud.create(db, obj_in=role_in)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["role:read"]))
):
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["role:update"]))
):
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if role_in.name:
        existing_role = await role_crud.get_by_name(db, name=role_in.name)
        if existing_role and existing_role.id != role_id:
            raise HTTPException(status_code=400, detail="角色名称已存在")
    
    return await role_crud.update(db, id=role_id, obj_in=role_in)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["role:delete"]))
):
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    await role_crud.delete(db, id=role_id)
