from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.metal_gauge import MetalGaugeCreate, MetalGaugeUpdate, MetalGaugeResponse
from app.schemas.common import PaginatedResponse
from app.crud.metal_gauge import metal_gauge_crud
from app.models.metal_gauge import GaugeImage
from app.core.deps import PermissionChecker
from app.models.user import User
from app.utils.file_handler import file_handler

router = APIRouter()


@router.get("", response_model=PaginatedResponse[MetalGaugeResponse])
async def list_metal_gauges(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["metal_gauge:read"]))
):
    skip = (page - 1) * page_size
    gauges = await metal_gauge_crud.get_multi(
        db, skip=skip, limit=page_size,
        category_id=category_id, status=status, is_active=is_active
    )
    
    filters = {}
    if category_id is not None:
        filters["category_id"] = category_id
    if status is not None:
        filters["status"] = status
    if is_active is not None:
        filters["is_active"] = is_active
    
    total = await metal_gauge_crud.count(db, filters=filters if filters else None)
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=gauges,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=MetalGaugeResponse, status_code=status.HTTP_201_CREATED)
async def create_metal_gauge(
    gauge_in: MetalGaugeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["metal_gauge:create"]))
):
    gauge = await metal_gauge_crud.get_by_gauge_number(db, gauge_number=gauge_in.gauge_number)
    if gauge:
        raise HTTPException(status_code=400, detail="金属表编号已存在")
    
    return await metal_gauge_crud.create(db, obj_in=gauge_in)


@router.get("/{gauge_id}", response_model=MetalGaugeResponse)
async def get_metal_gauge(
    gauge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["metal_gauge:read"]))
):
    gauge = await metal_gauge_crud.get(db, id=gauge_id)
    if not gauge:
        raise HTTPException(status_code=404, detail="金属表不存在")
    return gauge


@router.put("/{gauge_id}", response_model=MetalGaugeResponse)
async def update_metal_gauge(
    gauge_id: int,
    gauge_in: MetalGaugeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["metal_gauge:update"]))
):
    gauge = await metal_gauge_crud.get(db, id=gauge_id)
    if not gauge:
        raise HTTPException(status_code=404, detail="金属表不存在")
    
    if gauge_in.gauge_number:
        existing = await metal_gauge_crud.get_by_gauge_number(db, gauge_number=gauge_in.gauge_number)
        if existing and existing.id != gauge_id:
            raise HTTPException(status_code=400, detail="金属表编号已存在")
    
    return await metal_gauge_crud.update(db, id=gauge_id, obj_in=gauge_in)


@router.delete("/{gauge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metal_gauge(
    gauge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["metal_gauge:delete"]))
):
    gauge = await metal_gauge_crud.get(db, id=gauge_id)
    if not gauge:
        raise HTTPException(status_code=404, detail="金属表不存在")
    
    for image in gauge.images:
        await file_handler.delete_file(image.file_path)
    
    await metal_gauge_crud.delete(db, id=gauge_id)


@router.post("/{gauge_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_gauge_image(
    gauge_id: int,
    file: UploadFile = File(...),
    is_primary: bool = False,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["metal_gauge:update"]))
):
    gauge = await metal_gauge_crud.get(db, id=gauge_id)
    if not gauge:
        raise HTTPException(status_code=404, detail="金属表不存在")
    
    try:
        filename, file_path, file_size, dimensions = await file_handler.save_image(
            file, subfolder="gauges"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    gauge_image = GaugeImage(
        metal_gauge_id=gauge_id,
        filename=filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        width=dimensions[0] if dimensions else None,
        height=dimensions[1] if dimensions else None,
        is_primary=is_primary,
        description=description
    )
    
    db.add(gauge_image)
    await db.commit()
    await db.refresh(gauge_image)
    
    return {
        "id": gauge_image.id,
        "filename": gauge_image.filename,
        "file_url": file_handler.get_file_url(gauge_image.file_path)
    }


@router.delete("/{gauge_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gauge_image(
    gauge_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["metal_gauge:update"]))
):
    from sqlalchemy import select
    result = await db.execute(
        select(GaugeImage).where(
            GaugeImage.id == image_id,
            GaugeImage.metal_gauge_id == gauge_id
        )
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    
    await file_handler.delete_file(image.file_path)
    await db.delete(image)
    await db.commit()
