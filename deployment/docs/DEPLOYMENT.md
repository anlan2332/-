# 百考通AI写作平台 - 详细部署指南

## 部署概述

本指南详细介绍了百考通AI写作平台的各种部署方案，包括开发环境、生产环境的完整部署流程。

## 系统要求

### 最低要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 20GB | 50GB+ |
| 操作系统 | Linux/macOS | Ubuntu 20.04+ |

### 软件依赖

#### 本地开发环境
- Node.js 16.0+
- Python 3.8+
- Git
- npm/yarn

#### 生产环境（Docker）
- Docker 20.0+
- Docker Compose 1.29+

#### 生产环境（PM2）
- Node.js 16.0+
- Python 3.8+
- PostgreSQL 12+
- Nginx 1.18+
- PM2

## 本地开发部署

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd baikao-platform

# 检查系统要求
node --version  # 应显示 v16.0+
python3 --version  # 应显示 3.8+
```

### 2. 自动化部署

```bash
# 赋予执行权限
chmod +x deployment/scripts/deploy-local.sh

# 运行部署脚本
./deployment/scripts/deploy-local.sh
```

### 3. 手动部署步骤

如果自动化部署失败，可以按以下步骤手动部署：

#### 3.1 环境配置

```bash
# 复制环境配置文件
cp deployment/config/.env.local .env

# 编辑配置文件
nano .env
```

需要配置的关键参数：
```bash
DOUBAO_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
DB_TYPE=sqlite
DB_PATH=./data/local.db
```

#### 3.2 后端安装

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 初始化数据库
cd ..
mkdir -p data logs uploads
python3 deployment/scripts/migrate-db.py

# 测试后端
cd backend
source venv/bin/activate
python3 src/main.py
```

#### 3.3 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

#### 3.4 使用PM2管理（推荐）

```bash
# 安装PM2
npm install -g pm2

# 启动服务
pm2 start deployment/config/local-ecosystem.config.js

# 查看状态
pm2 status
pm2 logs
```

### 4. 验证部署

访问以下地址验证部署：
- 前端：http://localhost:3000
- 后端API：http://localhost:5000
- 健康检查：http://localhost:5000/health

## 生产环境部署

### Docker部署（推荐）

Docker部署是推荐的生产环境部署方式，提供了最佳的隔离性和可移植性。

#### 1. 系统准备

```bash
# Ubuntu/Debian 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER
```

#### 2. 部署执行

```bash
# 部署到生产环境
./deployment/scripts/deploy-server.sh --method docker --domain yourdomain.com

# 启用SSL（可选）
./deployment/scripts/deploy-server.sh --method docker --domain yourdomain.com --ssl
```

#### 3. 自定义配置

编辑 `deployment/docker/docker-compose.yml` 进行自定义：

```yaml
# 修改端口映射
ports:
  - "80:3000"    # HTTP端口
  - "443:3000"   # HTTPS端口（如果使用SSL）

# 修改环境变量
environment:
  - DOUBAO_API_KEY=${DOUBAO_API_KEY}
  - DB_PASSWORD=${DB_PASSWORD}

# 修改资源限制
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
```

#### 4. SSL配置

```bash
# 使用自有证书
./deployment/scripts/deploy-server.sh --method docker --ssl \
  --ssl-cert /path/to/cert.pem --ssl-key /path/to/key.pem

# 或者使用Let's Encrypt（推荐）
# 首先安装certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d yourdomain.com

# 然后部署
./deployment/scripts/deploy-server.sh --method docker --ssl \
  --ssl-cert /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
  --ssl-key /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### PM2部署

PM2部署适合对Docker有限制的环境或需要更细粒度控制的场景。

#### 1. 系统准备

```bash
# Ubuntu/Debian 系统准备
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip postgresql postgresql-contrib nginx

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 2. 数据库配置

```bash
# 切换到postgres用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE baikao_db;
CREATE USER baikao_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE baikao_db TO baikao_user;
\q
```

#### 3. 应用部署

```bash
# 使用部署脚本
./deployment/scripts/deploy-server.sh --method pm2 --domain yourdomain.com

# 或手动部署
# 1. 安装依赖
cd backend
pip3 install -r requirements.txt
cd ../frontend
npm ci
npm run build

# 2. 配置环境
cp deployment/config/.env.production .env
nano .env  # 编辑配置

# 3. 初始化数据库
python3 deployment/scripts/migrate-db.py

# 4. 安装和配置PM2
npm install -g pm2
pm2 start deployment/config/ecosystem.config.js --env production

# 5. 配置PM2开机启动
pm2 startup
pm2 save
```

#### 4. Nginx配置

```bash
# 复制Nginx配置
sudo cp deployment/config/nginx.conf /etc/nginx/sites-available/baikao
sudo ln -s /etc/nginx/sites-available/baikao /etc/nginx/sites-enabled/

# 修改配置中的域名
sudo nano /etc/nginx/sites-available/baikao

# 测试配置并重启
sudo nginx -t
sudo systemctl restart nginx
```

## 高级部署选项

### 负载均衡部署

对于高流量场景，可以配置多实例负载均衡：

#### Docker Swarm

```bash
# 初始化Swarm
docker swarm init

# 部署Stack
docker stack deploy -c deployment/docker/docker-compose.prod.yml baikao

# 扩容服务
docker service scale baikao_baikao-app=3
```

#### PM2 Cluster模式

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'baikao-backend',
    script: 'backend/src/main.py',
    instances: 'max',  // 使用所有CPU核心
    exec_mode: 'cluster',
    env_production: {
      NODE_ENV: 'production'
    }
  }]
}
```

### 数据库集群

#### PostgreSQL主从配置

```bash
# 主服务器配置
# /etc/postgresql/12/main/postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64

# /etc/postgresql/12/main/pg_hba.conf
host replication replica_user slave_ip/32 md5

# 从服务器配置
pg_basebackup -h master_ip -D /var/lib/postgresql/12/main -U replica_user -P -W
```

### 缓存配置

#### Redis缓存

```yaml
# docker-compose.yml 添加Redis服务
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

#### 应用配置缓存

```python
# backend/src/config.py
REDIS_URL = 'redis://localhost:6379/0'
CACHE_TYPE = 'redis'
CACHE_DEFAULT_TIMEOUT = 300
```

### 监控和日志

#### ELK Stack集成

```yaml
# docker-compose.monitoring.yml
elasticsearch:
  image: elasticsearch:7.14.0
  
logstash:
  image: logstash:7.14.0
  
kibana:
  image: kibana:7.14.0
  ports:
    - "5601:5601"
```

#### Prometheus + Grafana

```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
    
grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
```

## 部署验证

### 自动化验证

```bash
# 运行完整健康检查
./deployment/scripts/maintenance.sh health

# 运行部署验证脚本
./deployment/scripts/validate-deployment.sh
```

### 手动验证步骤

1. **服务状态检查**
```bash
# Docker部署
docker-compose ps

# PM2部署
pm2 status
```

2. **网络连接测试**
```bash
# 前端访问测试
curl -I http://yourdomain.com

# 后端API测试
curl -I http://yourdomain.com/api/health

# 数据库连接测试
psql -h localhost -U baikao_user -d baikao_db -c "SELECT 1;"
```

3. **功能测试**
- 用户注册和登录
- 文件上传功能
- AI生成功能
- 数据库读写操作

### 性能测试

```bash
# 使用Apache Bench测试
ab -n 1000 -c 10 http://yourdomain.com/

# 使用wrk测试
wrk -t12 -c400 -d30s http://yourdomain.com/api/health
```

## 故障恢复

### 数据备份策略

```bash
# 自动备份脚本
cat > /etc/cron.d/baikao-backup << EOF
0 2 * * * root /path/to/baikao-platform/deployment/scripts/maintenance.sh backup
EOF
```

### 灾难恢复流程

1. **服务停机**
```bash
# 停止所有服务
docker-compose down
# 或
pm2 stop all
```

2. **数据恢复**
```bash
# 从备份恢复
./deployment/scripts/maintenance.sh restore --backup-file latest_backup.tar.gz
```

3. **服务重启**
```bash
# 重新启动服务
./deployment/scripts/deploy-server.sh
```

## 安全加固

### 系统安全

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 配置防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 禁用root登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 应用安全

```bash
# 设置文件权限
chown -R www-data:www-data /path/to/uploads
chmod 755 /path/to/uploads

# 配置SSL
# 参见上面SSL配置部分

# 设置安全头
# 参见nginx.conf中的安全配置
```

## 性能优化

### 前端优化

```javascript
// webpack.config.js 优化配置
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
    },
  },
  plugins: [
    new CompressionPlugin({
      test: /\.(js|css|html|svg)$/,
      algorithm: 'gzip',
    }),
  ],
};
```

### 后端优化

```python
# gunicorn配置优化
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
keepalive = 5
```

### 数据库优化

```sql
-- PostgreSQL性能优化
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
```

---

## 下一步

部署完成后，请参考以下文档：
- [配置参数说明](CONFIGURATION.md) - 详细的配置参数介绍
- [维护操作手册](MAINTENANCE.md) - 日常维护操作指南
- [故障排除指南](TROUBLESHOOTING.md) - 常见问题解决方案