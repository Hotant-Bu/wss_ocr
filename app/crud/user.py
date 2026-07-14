from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.schemas.user import UserCreate, UserUpdate, RoleCreate, RoleUpdate, PermissionCreate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        obj_in_data = obj_in.model_dump(exclude={"password", "role_ids"})
        db_obj = User(
            **obj_in_data,
            hashed_password=get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        await db.flush()
        
        if obj_in.role_ids:
            for role_id in obj_in.role_ids:
                user_role = UserRole(user_id=db_obj.id, role_id=role_id)
                db.add(user_role)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(self, db: AsyncSession, id: int, obj_in: UserUpdate) -> Optional[User]:
        db_obj = await self.get(db, id)
        if not db_obj:
            return None
        
        obj_data = obj_in.model_dump(exclude_unset=True, exclude={"password", "role_ids"})
        
        if obj_in.password:
            obj_data["hashed_password"] = get_password_hash(obj_in.password)
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        if obj_in.role_ids is not None:
            await db.execute(
                select(UserRole).where(UserRole.user_id == id)
            )
            result = await db.execute(select(UserRole).where(UserRole.user_id == id))
            existing_roles = result.scalars().all()
            for ur in existing_roles:
                await db.delete(ur)
            
            for role_id in obj_in.role_ids:
                user_role = UserRole(user_id=id, role_id=role_id)
                db.add(user_role)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def authenticate(
        self, db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Role]:
        result = await db.execute(
            select(Role)
            .where(Role.name == name)
            .options(selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, obj_in: RoleCreate) -> Role:
        obj_in_data = obj_in.model_dump(exclude={"permission_ids"})
        db_obj = Role(**obj_in_data)
        db.add(db_obj)
        await db.flush()
        
        if obj_in.permission_ids:
            for permission_id in obj_in.permission_ids:
                role_permission = RolePermission(role_id=db_obj.id, permission_id=permission_id)
                db.add(role_permission)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(self, db: AsyncSession, id: int, obj_in: RoleUpdate) -> Optional[Role]:
        db_obj = await self.get(db, id)
        if not db_obj:
            return None
        
        obj_data = obj_in.model_dump(exclude_unset=True, exclude={"permission_ids"})
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        if obj_in.permission_ids is not None:
            result = await db.execute(select(RolePermission).where(RolePermission.role_id == id))
            existing_perms = result.scalars().all()
            for rp in existing_perms:
                await db.delete(rp)
            
            for permission_id in obj_in.permission_ids:
                role_permission = RolePermission(role_id=id, permission_id=permission_id)
                db.add(role_permission)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionCreate]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Permission]:
        result = await db.execute(select(Permission).where(Permission.name == name))
        return result.scalar_one_or_none()


user_crud = CRUDUser(User)
role_crud = CRUDRole(Role)
permission_crud = CRUDPermission(Permission)
