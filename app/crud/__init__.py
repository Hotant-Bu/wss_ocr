from app.crud.user import user_crud, role_crud, permission_crud
from app.crud.metal_gauge import metal_gauge_crud, category_crud
from app.crud.camera import camera_crud
from app.crud.config import config_crud
from app.crud.audit_log import audit_log_crud

__all__ = [
    "user_crud",
    "role_crud",
    "permission_crud",
    "metal_gauge_crud",
    "category_crud",
    "camera_crud",
    "config_crud",
    "audit_log_crud",
]
