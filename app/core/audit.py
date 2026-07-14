from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.models.user import User


async def create_audit_log(
    db: AsyncSession,
    user: Optional[User],
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    method: Optional[str] = None,
    endpoint: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_data: Optional[Dict[str, Any]] = None,
    response_status: Optional[int] = None,
    error_message: Optional[str] = None
):
    audit_log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource=resource,
        resource_id=resource_id,
        method=method,
        endpoint=endpoint,
        ip_address=ip_address,
        user_agent=user_agent,
        request_data=request_data,
        response_status=response_status,
        error_message=error_message
    )
    db.add(audit_log)
    await db.commit()
    return audit_log
