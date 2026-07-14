from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.config import ConfigCreate, ConfigUpdate, ConfigResponse
from app.schemas.common import PaginatedResponse
from app.crud.config import config_crud
from app.core.deps import PermissionChecker
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ConfigResponse])
async def list_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["config:read"]))
):
    skip = (page - 1) * page_size
    
    filters = {}
    if category:
        filters["category"] = category
    
    configs = await config_crud.get_multi(
        db, skip=skip, limit=page_size, filters=filters if filters else None
    )
    total = await config_crud.count(db, filters=filters if filters else None)
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=configs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/active", response_model=List[ConfigResponse])
async def list_active_configs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["config:read"]))
):
    return await config_crud.get_active(db)


@router.post("", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    config_in: ConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["config:create"]))
):
    config = await config_crud.get_by_key(db, key=config_in.key)
    if config:
        raise HTTPException(status_code=400, detail="配置键已存在")
    
    return await config_crud.create(db, obj_in=config_in)


@router.get("/{config_id}", response_model=ConfigResponse)
async def get_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["config:read"]))
):
    config = await config_crud.get(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


@router.get("/key/{key}", response_model=ConfigResponse)
async def get_config_by_key(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["config:read"]))
):
    config = await config_crud.get_by_key(db, key=key)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


@router.put("/{config_id}", response_model=ConfigResponse)
async def update_config(
    config_id: int,
    config_in: ConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["config:update"]))
):
    config = await config_crud.get(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    if config.is_system:
        raise HTTPException(status_code=403, detail="系统配置不可修改")
    
    return await config_crud.update(db, id=config_id, obj_in=config_in)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["config:delete"]))
):
    config = await config_crud.get(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    if config.is_system:
        raise HTTPException(status_code=403, detail="系统配置不可删除")
    
    await config_crud.delete(db, id=config_id)
