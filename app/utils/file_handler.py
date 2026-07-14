import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
from PIL import Image
from app.config import settings


class FileHandler:
    def __init__(self):
        self.storage_path = Path(settings.OSS_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def save_image(
        self,
        file: UploadFile,
        subfolder: str = "gauges"
    ) -> Tuple[str, str, int, Optional[Tuple[int, int]]]:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            raise ValueError("不支持的图片格式")
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        folder_path = self.storage_path / subfolder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        file_path = folder_path / unique_filename
        
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        file_size = len(content)
        
        try:
            with Image.open(file_path) as img:
                dimensions = img.size
        except Exception:
            dimensions = None
        
        relative_path = f"{subfolder}/{unique_filename}"
        
        return unique_filename, relative_path, file_size, dimensions
    
    async def delete_file(self, file_path: str) -> bool:
        try:
            full_path = self.storage_path / file_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_url(self, file_path: str) -> str:
        return f"{settings.OSS_BASE_URL}/{file_path}"


file_handler = FileHandler()
