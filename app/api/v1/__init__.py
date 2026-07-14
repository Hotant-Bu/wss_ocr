from fastapi import APIRouter
from app.api.v1 import auth, users, roles, permissions, categories, metal_gauges, cameras, configs, audit_logs, files

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["权限管理"])
api_router.include_router(categories.router, prefix="/categories", tags=["分类管理"])
api_router.include_router(metal_gauges.router, prefix="/metal-gauges", tags=["金属表管理"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["摄像头管理"])
api_router.include_router(configs.router, prefix="/configs", tags=["配置管理"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["操作日志"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])
