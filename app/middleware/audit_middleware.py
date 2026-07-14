import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import AsyncSessionLocal
from app.core.audit import create_audit_log
from app.core.deps import decode_access_token
from sqlalchemy import select
from app.models.user import User


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        user = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            if payload:
                username = payload.get("sub")
                if username:
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(
                            select(User).where(User.username == username)
                        )
                        user = result.scalar_one_or_none()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            async with AsyncSessionLocal() as db:
                action_map = {
                    "POST": "create",
                    "PUT": "update",
                    "PATCH": "update",
                    "DELETE": "delete"
                }
                
                action = action_map.get(request.method, "unknown")
                resource = request.url.path.split("/")[-1] if request.url.path else "unknown"
                
                await create_audit_log(
                    db=db,
                    user=user,
                    action=action,
                    resource=resource,
                    method=request.method,
                    endpoint=str(request.url.path),
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    response_status=response.status_code
                )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
