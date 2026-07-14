# Redis Token管理设计文档

## 概述

本系统使用Redis作为Token存储后端，实现了安全的JWT Token管理机制，支持Token刷新、多设备登录管理和安全登出功能。

## 设计目标

1. **安全性**：Token存储在Redis中，可以随时撤销
2. **可扩展性**：支持多设备登录，每个设备有独立的token_id
3. **性能**：利用Redis的高性能特性，快速验证Token
4. **灵活性**：支持Token刷新，提升用户体验

## Redis数据结构

### 1. Access Token存储

**键格式**：`access_token:{username}:{token_id}`  
**值**：JWT access token字符串  
**过期时间**：ACCESS_TOKEN_EXPIRE_MINUTES（默认30分钟）

```
access_token:admin:uuid-1234 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. Refresh Token存储

**键格式**：`refresh_token:{username}:{token_id}`  
**值**：JWT refresh token字符串  
**过期时间**：REFRESH_TOKEN_EXPIRE_DAYS（默认7天）

```
refresh_token:admin:uuid-1234 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. 用户Token集合

**键格式**：`user_tokens:{username}`  
**类型**：Set  
**值**：该用户所有有效的token_id集合  
**过期时间**：与refresh token相同

```
user_tokens:admin = {uuid-1234, uuid-5678, uuid-9012}
```

## Token生命周期

### 1. 登录流程

```
用户登录
  ↓
验证用户名密码
  ↓
生成access_token和refresh_token
  ↓
生成唯一token_id (UUID)
  ↓
存储到Redis:
  - access_token:{username}:{token_id}
  - refresh_token:{username}:{token_id}
  - user_tokens:{username} (添加token_id)
  ↓
返回tokens给客户端
```

### 2. Token验证流程

```
客户端请求 (携带access_token)
  ↓
解析JWT获取username
  ↓
从user_tokens:{username}获取所有token_id
  ↓
遍历检查access_token:{username}:{token_id}
  ↓
找到匹配的token → 验证通过
未找到 → 验证失败
```

### 3. Token刷新流程

```
客户端发送refresh_token
  ↓
验证refresh_token有效性
  ↓
提取username
  ↓
生成新的access_token和refresh_token
  ↓
生成新的token_id
  ↓
存储新tokens到Redis
  ↓
返回新tokens给客户端
```

### 4. 登出流程

```
用户登出
  ↓
获取username
  ↓
从user_tokens:{username}获取所有token_id
  ↓
删除所有相关的Redis键:
  - access_token:{username}:{token_id}
  - refresh_token:{username}:{token_id}
  ↓
删除user_tokens:{username}
  ↓
登出成功
```

## API接口

### 1. 登录接口

**端点**：`POST /api/v1/auth/login`

**请求**：
```
username=admin&password=admin123
```

**响应**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "token_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. 刷新Token接口

**端点**：`POST /api/v1/auth/refresh`

**请求**：
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "token_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

### 3. 登出接口

**端点**：`POST /api/v1/auth/logout`

**请求头**：
```
Authorization: Bearer {access_token}
```

**响应**：
```json
{
  "message": "登出成功"
}
```

## 核心函数说明

### 1. store_token_in_redis()

存储Token到Redis，返回token_id。

```python
async def store_token_in_redis(username: str, access_token: str, refresh_token: str) -> str
```

### 2. verify_token_in_redis()

验证Token是否在Redis中存在且有效。

```python
async def verify_token_in_redis(username: str, token: str) -> bool
```

### 3. revoke_token()

撤销单个Token。

```python
async def revoke_token(username: str, token_id: str)
```

### 4. revoke_all_user_tokens()

撤销用户的所有Token（用于登出）。

```python
async def revoke_all_user_tokens(username: str)
```

## 安全特性

### 1. Token撤销

- 用户登出时，所有Token立即失效
- 管理员可以强制撤销特定用户的Token
- Token存储在Redis中，可以随时删除

### 2. 多设备管理

- 每个设备登录生成独立的token_id
- 可以查看和管理所有登录设备
- 支持单独撤销某个设备的Token

### 3. 过期控制

- Access Token短期有效（30分钟）
- Refresh Token长期有效（7天）
- Redis自动清理过期的Token

### 4. 防止Token重放

- 每次刷新生成新的token_id
- 旧Token在刷新后不会立即失效（可选配置）

## 配置参数

```env
# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_DECODE_RESPONSES=True

# Token过期时间
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 性能优化

### 1. 连接池

使用Redis连接池，避免频繁创建连接。

### 2. 批量操作

使用Redis Pipeline进行批量操作，减少网络往返。

### 3. 缓存策略

- Token验证结果可以短暂缓存
- 减少Redis查询频率

## 监控建议

### 1. Redis监控指标

- 连接数
- 内存使用
- 命令执行时间
- 键空间统计

### 2. Token统计

- 活跃Token数量
- Token刷新频率
- 登录/登出频率

### 3. 异常监控

- Token验证失败次数
- Redis连接失败
- Token过期异常

## 故障处理

### 1. Redis不可用

- 降级策略：仅验证JWT签名（不检查Redis）
- 告警通知
- 自动重连机制

### 2. Token泄露

- 立即撤销所有Token
- 强制用户重新登录
- 记录安全日志

### 3. 性能问题

- 增加Redis实例
- 使用Redis Cluster
- 优化Token验证逻辑

## 未来扩展

### 1. 单点登录（SSO）

- 跨系统Token共享
- 统一认证中心

### 2. Token黑名单

- 记录被撤销的Token
- 防止已撤销Token被重用

### 3. 设备管理

- 记录设备信息
- 设备指纹识别
- 异常登录检测

### 4. Token限流

- 限制Token刷新频率
- 防止暴力破解
- IP限制

## 总结

本系统通过Redis实现了完整的Token管理机制，提供了安全、高效、可扩展的认证解决方案。通过合理的数据结构设计和完善的API接口，满足了生产环境的各种需求。
