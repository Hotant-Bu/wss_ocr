# WSS全金属表管理系统

一个基于FastAPI和MySQL的全功能金属表管理系统，支持金属表信息管理、图片存储、摄像头管理、配置管理和完整的RBAC权限控制。

## 功能特性

### 核心功能
- **金属表管理**：完整的金属表信息管理，包括编号、类型、量程、安装位置、制造厂商等
- **分类管理**：支持金属表分类（压力表、温度表等），支持层级结构
- **图片管理**：金属表图片上传和管理，本地OSS存储
- **摄像头管理**：拍照摄像头的配置和管理
- **配置参数管理**：系统配置参数的统一管理
- **操作日志**：完整的操作审计日志记录

### 权限管理
- **RBAC权限系统**：基于角色的访问控制
- **默认角色**：
  - 管理员：拥有所有权限
  - 操作员：拥有查看、创建和更新权限
  - 访客：只有查看权限
- **细粒度权限控制**：资源级别的权限管理

### 技术特性
- RESTful API设计规范
- JWT身份认证 + Redis Token管理
- Token刷新机制
- 安全的登出功能
- 异步数据库操作
- 自动API文档生成
- 操作日志中间件
- CORS跨域支持

## 技术栈

- **后端框架**：FastAPI 0.115.5
- **数据库**：MySQL（通过aiomysql异步驱动）
- **缓存/Token存储**：Redis 5.2.0（异步）
- **ORM**：SQLAlchemy 2.0.36（异步）
- **数据库迁移**：Alembic 1.14.0
- **认证**：JWT（python-jose）
- **密码加密**：Bcrypt（passlib）
- **文件存储**：Rustfile（独立文件服务）
- **ASGI服务器**：Uvicorn 0.32.1

## 项目结构

```
wss_ocr/
├── app/
│   ├── api/
│   │   └── v1/              # API路由
│   │       ├── auth.py      # 认证接口
│   │       ├── users.py     # 用户管理
│   │       ├── roles.py     # 角色管理
│   │       ├── permissions.py # 权限管理
│   │       ├── categories.py  # 分类管理
│   │       ├── metal_gauges.py # 金属表管理
│   │       ├── cameras.py   # 摄像头管理
│   │       ├── configs.py   # 配置管理
│   │       ├── audit_logs.py # 日志查询
│   │       └── files.py     # 文件访问
│   ├── core/
│   │   ├── security.py      # 安全相关（JWT、密码）
│   │   ├── deps.py          # 依赖注入
│   │   └── audit.py         # 审计日志
│   ├── crud/                # 数据库操作层
│   ├── models/              # 数据库模型
│   ├── schemas/             # Pydantic模型
│   ├── middleware/          # 中间件
│   ├── utils/               # 工具函数
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   └── main.py              # 应用入口
├── scripts/
│   └── init_db.py           # 数据库初始化脚本
├── alembic/                 # 数据库迁移
├── storage/                 # 文件存储目录
├── logs/                    # 日志目录
├── .env                     # 环境变量配置
├── requirements.txt         # Python依赖
└── README.md

```

## 快速开始

### 1. 环境要求

- Python 3.10+
- MySQL 8.0+
- Redis 6.0+
- pip

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库和Redis连接等信息：

```env
# 数据库配置
DATABASE_URL=mysql+aiomysql://root:your_password@localhost:3306/wss_metal_gauge
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=wss_metal_gauge

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_DECODE_RESPONSES=True

# JWT配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rustfile文件存储配置
RUSTFILE_URL=http://localhost:3001
RUSTFILE_UPLOAD_PATH=/upload
RUSTFILE_DOWNLOAD_PATH=/files

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 4. 启动Redis

确保Redis服务已启动：

```bash
# Windows：
redis-server

# Linux/Mac：
sudo systemctl start redis
# 或
redis-server
```

### 5. 启动Rustfile文件服务

使用Docker启动Rustfile（推荐）：

```bash
docker run -d \
  --name rustfile \
  -p 3001:3001 \
  -v $(pwd)/storage:/app/storage \
  rustfile/rustfile:latest
```

或者使用二进制文件：

```bash
# 下载并运行rustfile
./rustfile --port 3001 --storage-path ./storage
```

详细配置请参考 [RUSTFILE_SETUP.md](RUSTFILE_SETUP.md)

### 6. 创建数据库

在MySQL中创建数据库：

```sql
CREATE DATABASE wss_metal_gauge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 7. 初始化数据库

运行初始化脚本创建表结构和初始数据：

```bash
python scripts/init_db.py
```

初始化脚本会创建：
- 所有数据库表
- 默认权限
- 三个默认角色（管理员、操作员、访客）
- 三个默认用户账号
- 基础分类数据（压力表、温度表、流量表、液位表）

### 8. 启动服务

```bash
# 开发模式（自动重载）
python app/main.py

# 或使用uvicorn直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 9. 访问API文档

启动后访问以下地址：

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/health

## 默认账号

系统初始化后会创建以下默认账号：

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 所有权限 |
| 操作员 | operator | operator123 | 查看、创建、更新权限 |
| 访客 | guest | guest123 | 仅查看权限 |

**⚠️ 生产环境请务必修改默认密码！**

## API使用示例

### 1. 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "token_id": "uuid-string"
}
```

### 2. 刷新Token

当access_token过期时，使用refresh_token获取新的token：

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### 3. 用户登出

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

登出后，该用户的所有token将从Redis中删除，无法再使用。

### 4. 获取当前用户信息

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. 创建金属表

```bash
curl -X POST "http://localhost:8000/api/v1/metal-gauges" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gauge_number": "MG-001",
    "gauge_type": "压力表",
    "range_min": 0,
    "range_max": 100,
    "range_unit": "MPa",
    "installation_location": "车间A-1号位置",
    "manufacturer": "某某仪表厂",
    "category_id": 1
  }'
```

### 6. 上传金属表图片

```bash
curl -X POST "http://localhost:8000/api/v1/metal-gauges/1/images" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "is_primary=true" \
  -F "description=金属表正面照片"
```

### 7. 查询金属表列表

```bash
curl -X GET "http://localhost:8000/api/v1/metal-gauges?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 数据库迁移

使用Alembic进行数据库版本管理：

```bash
# 创建新的迁移
alembic revision --autogenerate -m "描述信息"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

## 开发指南

### 添加新的API端点

1. 在 `app/models/` 中定义数据模型
2. 在 `app/schemas/` 中定义Pydantic模型
3. 在 `app/crud/` 中实现CRUD操作
4. 在 `app/api/v1/` 中创建路由
5. 在 `app/api/v1/__init__.py` 中注册路由

### 添加新的权限

在数据库初始化脚本中添加权限定义，或通过API创建：

```python
{
    "name": "资源操作",
    "resource": "resource_name",
    "action": "action_name",
    "description": "权限描述"
}
```

## 生产部署

### 1. 环境变量配置

生产环境需要修改以下配置：

```env
DEBUG=False
SECRET_KEY=生成一个强随机密钥
CORS_ORIGINS=["https://your-domain.com"]
```

### 2. 使用Gunicorn部署

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### 3. 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /storage {
        alias /path/to/wss_ocr/storage;
    }
}
```

### 4. 使用Supervisor管理进程

```ini
[program:wss_ocr]
command=/path/to/venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/path/to/wss_ocr
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/path/to/wss_ocr/logs/supervisor.log
```

## 安全建议

1. **修改默认密码**：部署后立即修改所有默认账号密码
2. **使用强密钥**：生成强随机的SECRET_KEY
3. **HTTPS**：生产环境使用HTTPS
4. **数据库安全**：使用强密码，限制数据库访问
5. **定期备份**：定期备份数据库和文件存储
6. **日志监控**：监控操作日志，及时发现异常
7. **更新依赖**：定期更新依赖包，修复安全漏洞

## 故障排查

### 数据库连接失败

检查：
- MySQL服务是否启动
- 数据库配置是否正确
- 数据库用户权限是否足够

### 文件上传失败

检查：
- storage目录是否存在且有写权限
- 文件大小是否超过限制
- 文件格式是否支持

### 权限验证失败

检查：
- Token是否有效
- 用户角色和权限配置是否正确
- 权限中间件是否正常工作

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请联系开发团队。

## 更新日志

### v1.0.0 (2024)
- 初始版本发布
- 完整的金属表管理功能
- RBAC权限系统
- 图片管理和本地存储
- 摄像头管理
- 配置参数管理
- 操作日志审计
