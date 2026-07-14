import os
import httpx
from typing import Optional, Tuple
from fastapi import UploadFile
from app.config import settings


class FileHandler:
    def __init__(self):
        self.rustfile_url = settings.RUSTFILE_URL
        self.upload_path = settings.RUSTFILE_UPLOAD_PATH
        self.download_path = settings.RUSTFILE_DOWNLOAD_PATH
    
    async def save_image(
        self,
        file: UploadFile,
        subfolder: str = "gauges"
    ) -> Tuple[str, str, int, Optional[Tuple[int, int]]]:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            raise ValueError("不支持的图片格式")
        
        content = await file.read()
        file_size = len(content)
        
        await file.seek(0)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {
                'file': (file.filename, content, file.content_type)
            }
            
            data = {
                'path': subfolder
            }
            
            response = await client.post(
                f"{self.rustfile_url}{self.upload_path}",
                files=files,
                data=data
            )
            
            if response.status_code != 200:
                raise Exception(f"上传到rustfile失败: {response.text}")
            
            result = response.json()
            
            file_path = result.get('path') or result.get('file_path') or result.get('url', '')
            filename = os.path.basename(file_path)
            
            return filename, file_path, file_size, None
    
    async def delete_file(self, file_path: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.rustfile_url}{self.download_path}/{file_path}"
                )
                return response.status_code == 200
        except Exception:
            return False
    
    def get_file_url(self, file_path: str) -> str:
        if file_path.startswith('http'):
            return file_path
        return f"{self.rustfile_url}{self.download_path}/{file_path}"


file_handler = FileHandler()
