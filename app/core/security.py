from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from app.core.redis import redis_manager
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def store_token_in_redis(username: str, access_token: str, refresh_token: str):
    token_id = str(uuid.uuid4())
    
    access_key = f"access_token:{username}:{token_id}"
    refresh_key = f"refresh_token:{username}:{token_id}"
    user_tokens_key = f"user_tokens:{username}"
    
    access_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_expire = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    
    await redis_manager.set(access_key, access_token, expire=access_expire)
    await redis_manager.set(refresh_key, refresh_token, expire=refresh_expire)
    
    await redis_manager.redis.sadd(user_tokens_key, token_id)
    await redis_manager.expire(user_tokens_key, refresh_expire)
    
    return token_id


async def verify_token_in_redis(username: str, token: str) -> bool:
    user_tokens_key = f"user_tokens:{username}"
    token_ids = await redis_manager.redis.smembers(user_tokens_key)
    
    for token_id in token_ids:
        access_key = f"access_token:{username}:{token_id}"
        stored_token = await redis_manager.get(access_key)
        if stored_token == token:
            return True
    
    return False


async def revoke_token(username: str, token_id: str):
    access_key = f"access_token:{username}:{token_id}"
    refresh_key = f"refresh_token:{username}:{token_id}"
    user_tokens_key = f"user_tokens:{username}"
    
    await redis_manager.delete(access_key)
    await redis_manager.delete(refresh_key)
    await redis_manager.redis.srem(user_tokens_key, token_id)


async def revoke_all_user_tokens(username: str):
    user_tokens_key = f"user_tokens:{username}"
    token_ids = await redis_manager.redis.smembers(user_tokens_key)
    
    for token_id in token_ids:
        await revoke_token(username, token_id)
    
    await redis_manager.delete(user_tokens_key)


async def get_refresh_token(username: str, token_id: str) -> Optional[str]:
    refresh_key = f"refresh_token:{username}:{token_id}"
    return await redis_manager.get(refresh_key)
