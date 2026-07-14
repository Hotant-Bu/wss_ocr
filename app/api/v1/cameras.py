from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.schemas.common import PaginatedResponse
from app.crud.camera import camera_crud
from app.core.deps import PermissionChecker
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CameraResponse])
async def list_cameras(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["camera:read"]))
):
    skip = (page - 1) * page_size
    cameras = await camera_crud.get_multi(db, skip=skip, limit=page_size)
    total = await camera_crud.count(db)
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=cameras,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/active", response_model=List[CameraResponse])
async def list_active_cameras(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["camera:read"]))
):
    return await camera_crud.get_active(db)


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_in: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["camera:create"]))
):
    camera = await camera_crud.get_by_camera_id(db, camera_id=camera_in.camera_id)
    if camera:
        raise HTTPException(status_code=400, detail="摄像头ID已存在")
    
    return await camera_crud.create(db, obj_in=camera_in)


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["camera:read"]))
):
    camera = await camera_crud.get(db, id=camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: int,
    camera_in: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["camera:update"]))
):
    camera = await camera_crud.get(db, id=camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    if camera_in.camera_id:
        existing = await camera_crud.get_by_camera_id(db, camera_id=camera_in.camera_id)
        if existing and existing.id != camera_id:
            raise HTTPException(status_code=400, detail="摄像头ID已存在")
    
    return await camera_crud.update(db, id=camera_id, obj_in=camera_in)


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["camera:delete"]))
):
    camera = await camera_crud.get(db, id=camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="摄像头不存在")
    
    await camera_crud.delete(db, id=camera_id)
