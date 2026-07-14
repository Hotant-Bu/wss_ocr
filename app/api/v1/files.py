from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.config import settings

router = APIRouter()


@router.get("/{subfolder}/{filename}")
async def get_file(subfolder: str, filename: str):
    file_path = Path(settings.OSS_STORAGE_PATH) / subfolder / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="无效的文件路径")
    
    return FileResponse(file_path)
