import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.database import Base
from app.models import *
from app.core.security import get_password_hash
from sqlalchemy import text


async def init_database():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("数据库表创建成功！")
    
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        from app.models.user import Permission, Role, User, RolePermission, UserRole
        
        permissions_data = [
            {"name": "用户查看", "resource": "user", "action": "read", "description": "查看用户信息"},
            {"name": "用户创建", "resource": "user", "action": "create", "description": "创建新用户"},
            {"name": "用户更新", "resource": "user", "action": "update", "description": "更新用户信息"},
            {"name": "用户删除", "resource": "user", "action": "delete", "description": "删除用户"},
            
            {"name": "角色查看", "resource": "role", "action": "read", "description": "查看角色信息"},
            {"name": "角色创建", "resource": "role", "action": "create", "description": "创建新角色"},
            {"name": "角色更新", "resource": "role", "action": "update", "description": "更新角色信息"},
            {"name": "角色删除", "resource": "role", "action": "delete", "description": "删除角色"},
            
            {"name": "权限查看", "resource": "permission", "action": "read", "description": "查看权限信息"},
            {"name": "权限创建", "resource": "permission", "action": "create", "description": "创建新权限"},
            {"name": "权限删除", "resource": "permission", "action": "delete", "description": "删除权限"},
            
            {"name": "分类查看", "resource": "category", "action": "read", "description": "查看分类信息"},
            {"name": "分类创建", "resource": "category", "action": "create", "description": "创建新分类"},
            {"name": "分类更新", "resource": "category", "action": "update", "description": "更新分类信息"},
            {"name": "分类删除", "resource": "category", "action": "delete", "description": "删除分类"},
            
            {"name": "金属表查看", "resource": "metal_gauge", "action": "read", "description": "查看金属表信息"},
            {"name": "金属表创建", "resource": "metal_gauge", "action": "create", "description": "创建新金属表"},
            {"name": "金属表更新", "resource": "metal_gauge", "action": "update", "description": "更新金属表信息"},
            {"name": "金属表删除", "resource": "metal_gauge", "action": "delete", "description": "删除金属表"},
            
            {"name": "摄像头查看", "resource": "camera", "action": "read", "description": "查看摄像头信息"},
            {"name": "摄像头创建", "resource": "camera", "action": "create", "description": "创建新摄像头"},
            {"name": "摄像头更新", "resource": "camera", "action": "update", "description": "更新摄像头信息"},
            {"name": "摄像头删除", "resource": "camera", "action": "delete", "description": "删除摄像头"},
            
            {"name": "配置查看", "resource": "config", "action": "read", "description": "查看配置信息"},
            {"name": "配置创建", "resource": "config", "action": "create", "description": "创建新配置"},
            {"name": "配置更新", "resource": "config", "action": "update", "description": "更新配置信息"},
            {"name": "配置删除", "resource": "config", "action": "delete", "description": "删除配置"},
            
            {"name": "日志查看", "resource": "audit_log", "action": "read", "description": "查看操作日志"},
        ]
        
        permissions = []
        for perm_data in permissions_data:
            permission = Permission(**perm_data)
            session.add(permission)
            permissions.append(permission)
        
        await session.flush()
        
        admin_role = Role(
            name="管理员",
            description="系统管理员，拥有所有权限",
            is_active=True
        )
        session.add(admin_role)
        await session.flush()
        
        for permission in permissions:
            role_permission = RolePermission(
                role_id=admin_role.id,
                permission_id=permission.id
            )
            session.add(role_permission)
        
        operator_role = Role(
            name="操作员",
            description="系统操作员，拥有查看和更新权限",
            is_active=True
        )
        session.add(operator_role)
        await session.flush()
        
        operator_permissions = [p for p in permissions if p.action in ["read", "create", "update"]]
        for permission in operator_permissions:
            role_permission = RolePermission(
                role_id=operator_role.id,
                permission_id=permission.id
            )
            session.add(role_permission)
        
        guest_role = Role(
            name="访客",
            description="访客用户，只有查看权限",
            is_active=True
        )
        session.add(guest_role)
        await session.flush()
        
        guest_permissions = [p for p in permissions if p.action == "read"]
        for permission in guest_permissions:
            role_permission = RolePermission(
                role_id=guest_role.id,
                permission_id=permission.id
            )
            session.add(role_permission)
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="系统管理员",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        session.add(admin_user)
        await session.flush()
        
        user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        session.add(user_role)
        
        operator_user = User(
            username="operator",
            email="operator@example.com",
            full_name="系统操作员",
            hashed_password=get_password_hash("operator123"),
            is_active=True,
            is_superuser=False
        )
        session.add(operator_user)
        await session.flush()
        
        user_role = UserRole(user_id=operator_user.id, role_id=operator_role.id)
        session.add(user_role)
        
        guest_user = User(
            username="guest",
            email="guest@example.com",
            full_name="访客用户",
            hashed_password=get_password_hash("guest123"),
            is_active=True,
            is_superuser=False
        )
        session.add(guest_user)
        await session.flush()
        
        user_role = UserRole(user_id=guest_user.id, role_id=guest_role.id)
        session.add(user_role)
        
        from app.models.metal_gauge import Category
        categories_data = [
            {"name": "压力表", "code": "PRESSURE", "description": "用于测量压力的金属表", "sort_order": 1},
            {"name": "温度表", "code": "TEMPERATURE", "description": "用于测量温度的金属表", "sort_order": 2},
            {"name": "流量表", "code": "FLOW", "description": "用于测量流量的金属表", "sort_order": 3},
            {"name": "液位表", "code": "LEVEL", "description": "用于测量液位的金属表", "sort_order": 4},
        ]
        
        for cat_data in categories_data:
            category = Category(**cat_data)
            session.add(category)
        
        await session.commit()
        
        print("初始数据创建成功！")
        print("\n默认用户账号：")
        print("1. 管理员 - 用户名: admin, 密码: admin123")
        print("2. 操作员 - 用户名: operator, 密码: operator123")
        print("3. 访客 - 用户名: guest, 密码: guest123")
    
    await engine.dispose()


if __name__ == "__main__":
    print("开始初始化数据库...")
    asyncio.run(init_database())
    print("数据库初始化完成！")
