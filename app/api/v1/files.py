from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.config import settings

router = APIRouter()


@router.get("/{file_path:path}")
async def get_file(file_path: str):
    """
    重定向到rustfile文件服务
    """
    rustfile_url = f"{settings.RUSTFILE_URL}{settings.RUSTFILE_DOWNLOAD_PATH}/{file_path}"
    return RedirectResponse(url=rustfile_url)
