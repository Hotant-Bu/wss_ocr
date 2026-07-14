from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.metal_gauge import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import PaginatedResponse
from app.crud.metal_gauge import category_crud
from app.core.deps import PermissionChecker
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CategoryResponse])
async def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["category:read"]))
):
    skip = (page - 1) * page_size
    categories = await category_crud.get_multi(db, skip=skip, limit=page_size)
    total = await category_crud.count(db)
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=categories,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/active", response_model=List[CategoryResponse])
async def list_active_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["category:read"]))
):
    return await category_crud.get_active(db)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["category:create"]))
):
    category = await category_crud.get_by_code(db, code=category_in.code)
    if category:
        raise HTTPException(status_code=400, detail="分类代码已存在")
    
    category = await category_crud.get_by_name(db, name=category_in.name)
    if category:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    
    return await category_crud.create(db, obj_in=category_in)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["category:read"]))
):
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["category:update"]))
):
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    if category_in.code:
        existing = await category_crud.get_by_code(db, code=category_in.code)
        if existing and existing.id != category_id:
            raise HTTPException(status_code=400, detail="分类代码已存在")
    
    if category_in.name:
        existing = await category_crud.get_by_name(db, name=category_in.name)
        if existing and existing.id != category_id:
            raise HTTPException(status_code=400, detail="分类名称已存在")
    
    return await category_crud.update(db, id=category_id, obj_in=category_in)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["category:delete"]))
):
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    await category_crud.delete(db, id=category_id)
