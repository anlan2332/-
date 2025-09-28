# 百考通AI写作平台 部署包

## 项目简介

百考通AI写作平台是一个基于AI的学术论文写作助手，支持从提案上传、大纲生成到论文写作的全流程功能。

### 核心功能

- 📝 **智能论文写作**：基于豆包AI的论文生成
- 📋 **提案分析**：自动解析研究提案并提取关键信息
- 🔍 **文献检索**：智能推荐相关学术文献
- 📊 **大纲生成**：多种方式生成论文大纲
- 💾 **文档导出**：生成Word格式的论文文档
- 👥 **用户管理**：完整的用户注册和认证系统
- 🛒 **订单系统**：集成的订单和支付管理

### 技术栈

- **前端**：React.js, Material-UI
- **后端**：Flask, SQLAlchemy, Flask-SocketIO
- **数据库**：PostgreSQL (生产环境) / SQLite (开发环境)
- **AI服务**：豆包大模型 API
- **部署**：Docker, PM2, Nginx
- **监控**：PM2监控, 自定义健康检查

## 部署方案

本部署包支持以下几种部署方式：

### 1. 本地开发部署
- 适用于开发和测试环境
- 使用SQLite数据库
- PM2进程管理
- 热重载支持

### 2. 服务器生产部署
- **Docker方式**：推荐的生产环境部署方式
- **PM2方式**：传统的进程管理部署方式
- PostgreSQL数据库
- Nginx反向代理
- SSL/TLS支持

### 3. 更新和维护
- 自动化更新脚本
- 数据备份和恢复
- 日志管理和清理
- 健康检查和监控

## 快速开始

### 本地部署

1. **系统要求**
   - Node.js 16+
   - Python 3.8+
   - Git

2. **部署命令**
   ```bash
   # 克隆项目
   git clone <repository-url>
   cd baikao-platform
   
   # 运行本地部署脚本
   chmod +x deployment/scripts/deploy-local.sh
   ./deployment/scripts/deploy-local.sh
   ```

3. **配置API密钥**
   ```bash
   # 编辑环境配置文件
   nano .env
   # 设置 DOUBAO_API_KEY=你的豆包API密钥
   ```

4. **访问应用**
   - 前端：http://localhost:3000
   - 后端API：http://localhost:5000

### 服务器部署

#### Docker方式（推荐）

1. **系统要求**
   - Docker 20+
   - Docker Compose 1.29+

2. **部署命令**
   ```bash
   # 使用Docker部署
   ./deployment/scripts/deploy-server.sh --method docker --domain yourdomain.com
   ```

#### PM2方式

1. **系统要求**
   - Node.js 16+
   - Python 3.8+
   - PostgreSQL 12+
   - Nginx

2. **部署命令**
   ```bash
   # 使用PM2部署
   ./deployment/scripts/deploy-server.sh --method pm2 --domain yourdomain.com
   ```

## 目录结构

```
deployment/
├── docker/                    # Docker配置
│   ├── Dockerfile            # 应用镜像构建文件
│   └── docker-compose.yml    # 服务编排文件
├── config/                   # 配置文件
│   ├── .env.example         # 环境配置示例
│   ├── .env.local           # 本地开发配置
│   ├── .env.production      # 生产环境配置
│   ├── nginx.conf           # Nginx配置
│   ├── ecosystem.config.js  # PM2生产配置
│   └── local-ecosystem.config.js  # PM2开发配置
├── scripts/                  # 部署脚本
│   ├── deploy-local.sh      # 本地部署脚本
│   ├── deploy-server.sh     # 服务器部署脚本
│   ├── start-production.sh  # 生产启动脚本
│   ├── update.sh           # 更新脚本
│   ├── maintenance.sh      # 维护脚本
│   ├── init-db.sql        # 数据库初始化SQL
│   └── migrate-db.py      # 数据库迁移脚本
└── docs/                   # 文档
    ├── README.md          # 主要文档
    ├── DEPLOYMENT.md      # 详细部署指南
    ├── CONFIGURATION.md   # 配置说明
    ├── MAINTENANCE.md     # 维护手册
    └── TROUBLESHOOTING.md # 故障排除指南
```

## 环境配置

### 必需配置项

```bash
# AI服务配置
DOUBAO_API_KEY=your_doubao_api_key_here

# 数据库配置
DB_TYPE=postgresql  # 或 sqlite
DB_HOST=localhost
DB_NAME=baikao_db
DB_USER=baikao_user
DB_PASSWORD=secure_password

# 安全配置
SECRET_KEY=your_very_secure_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

### 可选配置项

```bash
# 服务端口
FRONTEND_PORT=3000
BACKEND_PORT=5000

# 文件上传
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# SSL配置（HTTPS）
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

## 管理命令

### 服务管理

```bash
# 查看服务状态
./deployment/scripts/maintenance.sh status

# 查看日志
./deployment/scripts/maintenance.sh logs
./deployment/scripts/maintenance.sh logs --follow

# 重启服务
./deployment/scripts/maintenance.sh restart
./deployment/scripts/maintenance.sh restart --service backend

# 健康检查
./deployment/scripts/maintenance.sh health
```

### 更新管理

```bash
# 检查并更新应用
./deployment/scripts/update.sh

# 强制更新
./deployment/scripts/update.sh --force

# 从指定分支更新
./deployment/scripts/update.sh --branch develop
```

### 备份和维护

```bash
# 创建完整备份
./deployment/scripts/maintenance.sh backup

# 从备份恢复
./deployment/scripts/maintenance.sh restore --backup-file backup.tar.gz

# 系统清理
./deployment/scripts/maintenance.sh cleanup
./deployment/scripts/maintenance.sh cleanup --days 7
```

## Docker管理命令

```bash
# 查看容器状态
docker-compose -f deployment/docker/docker-compose.yml ps

# 查看日志
docker-compose -f deployment/docker/docker-compose.yml logs
docker-compose -f deployment/docker/docker-compose.yml logs -f frontend

# 重启服务
docker-compose -f deployment/docker/docker-compose.yml restart
docker-compose -f deployment/docker/docker-compose.yml restart backend

# 停止所有服务
docker-compose -f deployment/docker/docker-compose.yml down

# 重新构建并启动
docker-compose -f deployment/docker/docker-compose.yml up -d --build
```

## PM2管理命令

```bash
# 查看PM2服务
pm2 status

# 查看日志
pm2 logs
pm2 logs backend --lines 100

# 重启服务
pm2 restart all
pm2 restart backend

# 停止服务
pm2 stop all
pm2 delete all

# 监控
pm2 monit
```

## 监控和日志

### 日志位置

- **应用日志**：`logs/`目录
- **Docker日志**：`docker-compose logs`
- **PM2日志**：`~/.pm2/logs/`
- **Nginx日志**：`/var/log/nginx/`

### 监控指标

- **服务状态**：前端和后端服务运行状态
- **资源使用**：CPU、内存、磁盘使用率
- **响应时间**：HTTP请求响应时间
- **数据库连接**：数据库连接状态
- **API调用**：豆包AI API调用次数和状态

## 性能优化

### 前端优化

- React生产构建优化
- 静态资源压缩
- 浏览器缓存配置
- CDN加速（可选）

### 后端优化

- Gunicorn多进程部署
- 数据库连接池
- Redis缓存（可选）
- API响应缓存

### 数据库优化

- 索引优化
- 查询优化
- 连接池配置
- 定期备份

## 安全配置

### 网络安全

- Nginx反向代理
- 防火墙配置
- SSL/TLS加密
- CORS配置

### 应用安全

- 环境变量管理
- 密钥轮换
- 输入验证
- SQL注入防护

### 文件安全

- 上传文件类型限制
- 文件大小限制
- 路径遍历防护
- 恶意文件扫描

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口占用
   - 验证环境配置
   - 查看错误日志

2. **数据库连接失败**
   - 确认数据库服务运行
   - 检查连接参数
   - 验证用户权限

3. **AI API调用失败**
   - 验证API密钥
   - 检查网络连接
   - 确认API额度

4. **文件上传失败**
   - 检查磁盘空间
   - 验证文件权限
   - 确认文件大小限制

### 诊断命令

```bash
# 完整健康检查
./deployment/scripts/maintenance.sh health

# 查看详细日志
./deployment/scripts/maintenance.sh logs --follow

# 测试数据库连接
python3 deployment/scripts/migrate-db.py

# 测试HTTP服务
curl -f http://localhost:3000
curl -f http://localhost:5000/health
```

## 技术支持

### 联系方式

- 项目维护者：开发团队
- 技术支持邮箱：support@baikao.com
- 问题反馈：GitHub Issues

### 文档链接

- [详细部署指南](DEPLOYMENT.md)
- [配置参数说明](CONFIGURATION.md)
- [维护操作手册](MAINTENANCE.md)
- [故障排除指南](TROUBLESHOOTING.md)

### 版本信息

- 当前版本：1.0.0
- 发布日期：2024年
- 最后更新：请查看Git提交记录

---

**注意**：在生产环境部署前，请务必：
1. 更改所有默认密码和密钥
2. 配置正确的API密钥
3. 设置适当的防火墙规则
4. 启用SSL/TLS加密
5. 配置定期备份策略