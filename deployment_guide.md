# 加密货币追踪系统部署指南

## 目录

1. [系统要求](#系统要求)
2. [部署方式](#部署方式)
3. [Docker部署](#docker部署)
4. [手动部署](#手动部署)
5. [配置说明](#配置说明)
6. [数据库设置](#数据库设置)
7. [安全配置](#安全配置)
8. [启动服务](#启动服务)
9. [系统监控](#系统监控)
10. [常见问题](#常见问题)

## 系统要求

### 硬件要求

- **CPU**: 至少4核心
- **内存**: 至少8GB RAM
- **存储**: 至少50GB可用空间（取决于监控的交易量）
- **网络**: 稳定的互联网连接

### 软件要求

- **操作系统**: Ubuntu 20.04 LTS或更高版本
- **Docker**: 20.10或更高版本（推荐使用Docker部署）
- **Python**: 3.10或更高版本（手动部署时需要）
- **Node.js**: 16.x或更高版本（手动部署时需要）
- **数据库**:
  - PostgreSQL 14或更高版本
  - TimescaleDB扩展
  - Neo4j 4.4或更高版本

## 部署方式

加密货币追踪系统提供两种部署方式：

1. **Docker部署**（推荐）：使用Docker和Docker Compose快速部署整个系统
2. **手动部署**：手动安装和配置各个组件

## Docker部署

Docker部署是最简单的方式，只需几个命令即可启动整个系统。

### 前提条件

确保已安装Docker和Docker Compose：

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 部署步骤

1. **克隆代码仓库**：

```bash
git clone https://github.com/yourusername/crypto-tracker.git
cd crypto-tracker
```

2. **配置环境变量**：

```bash
cp .env.example .env
```

编辑`.env`文件，设置必要的环境变量：

```
# 应用设置
APP_NAME=加密货币追踪系统
DEBUG=false

# 安全设置
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# 数据库设置
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=dbpassword
POSTGRES_DB=crypto_tracker
TIMESCALE_DB=timeseries
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jpassword

# 区块链设置
ETH_NODE_URL=https://mainnet.infura.io/v3/your-api-key
BTC_NODE_URL=https://btc.getblock.io/mainnet/
BTC_NODE_USER=your-btc-node-user
BTC_NODE_PASSWORD=your-btc-node-password

# 管理员设置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin-password-here
ADMIN_EMAIL=admin@example.com
```

3. **启动服务**：

```bash
docker-compose up -d
```

4. **验证部署**：

```bash
docker-compose ps
```

所有服务应该处于"Up"状态。

5. **访问系统**：

打开浏览器，访问`http://your-server-ip:3000`

### 更新系统

当有新版本发布时，可以按照以下步骤更新系统：

```bash
# 拉取最新代码
git pull

# 重新构建并启动容器
docker-compose down
docker-compose build
docker-compose up -d
```

## 手动部署

如果您不想使用Docker，也可以手动部署系统。

### 安装依赖

1. **安装系统依赖**：

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib
```

2. **安装TimescaleDB**：

```bash
# 添加TimescaleDB仓库
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt update

# 安装TimescaleDB
sudo apt install -y timescaledb-postgresql-14

# 配置TimescaleDB
sudo timescaledb-tune --quiet --yes
sudo systemctl restart postgresql
```

3. **安装Neo4j**：

```bash
# 添加Neo4j仓库
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update

# 安装Neo4j
sudo apt install -y neo4j

# 启动Neo4j服务
sudo systemctl enable neo4j
sudo systemctl start neo4j
```

### 设置数据库

1. **配置PostgreSQL**：

```bash
# 创建数据库用户
sudo -u postgres createuser --interactive --pwprompt dbuser
# 创建数据库
sudo -u postgres createdb --owner=dbuser crypto_tracker
sudo -u postgres createdb --owner=dbuser timeseries

# 启用TimescaleDB扩展
sudo -u postgres psql -d timeseries -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

2. **配置Neo4j**：

```bash
# 设置Neo4j密码
sudo neo4j-admin set-initial-password neo4jpassword
```

### 部署后端

1. **克隆代码仓库**：

```bash
git clone https://github.com/yourusername/crypto-tracker.git
cd crypto-tracker
```

2. **设置Python虚拟环境**：

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **安装后端依赖**：

```bash
cd src/backend
pip install -r requirements.txt
```

4. **配置后端**：

创建配置文件：

```bash
cp app/config.example.py app/config.py
```

编辑`app/config.py`，设置必要的配置项。

5. **初始化数据库**：

```bash
python init_db.py
```

6. **启动后端服务**：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 部署前端

1. **安装前端依赖**：

```bash
cd src/frontend
npm install
```

2. **配置前端**：

创建环境配置文件：

```bash
cp .env.example .env
```

编辑`.env`文件，设置API地址：

```
REACT_APP_API_URL=http://your-server-ip:8000
```

3. **构建前端**：

```bash
npm run build
```

4. **部署前端**：

使用Nginx部署前端：

```bash
sudo apt install -y nginx

# 配置Nginx
sudo nano /etc/nginx/sites-available/crypto-tracker
```

添加以下配置：

```
server {
    listen 80;
    server_name your-server-domain-or-ip;

    root /path/to/crypto-tracker/src/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

启用配置并重启Nginx：

```bash
sudo ln -s /etc/nginx/sites-available/crypto-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 配置说明

### 环境变量

系统使用环境变量进行配置，主要配置项包括：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `APP_NAME` | 应用名称 | 加密货币追踪系统 |
| `DEBUG` | 调试模式 | false |
| `SECRET_KEY` | JWT密钥 | （必须设置） |
| `ENCRYPTION_KEY` | 数据加密密钥 | （必须设置） |
| `DATABASE_URL` | PostgreSQL连接URL | postgresql://dbuser:dbpassword@localhost/crypto_tracker |
| `TIMESCALE_URL` | TimescaleDB连接URL | postgresql://dbuser:dbpassword@localhost/timeseries |
| `NEO4J_URL` | Neo4j连接URL | bolt://localhost:7687 |
| `NEO4J_USER` | Neo4j用户名 | neo4j |
| `NEO4J_PASSWORD` | Neo4j密码 | （必须设置） |
| `ETH_NODE_URL` | 以太坊节点URL | （必须设置） |
| `BTC_NODE_URL` | 比特币节点URL | （必须设置） |
| `ADMIN_USERNAME` | 管理员用户名 | admin |
| `ADMIN_PASSWORD` | 管理员密码 | （必须设置） |

### 配置文件

如果不使用环境变量，也可以通过配置文件进行配置。配置文件位于`src/backend/app/config.py`。

## 数据库设置

### PostgreSQL和TimescaleDB

系统使用PostgreSQL存储用户数据和警报信息，使用TimescaleDB存储交易数据。

数据库架构初始化脚本位于`src/backend/scripts/init_db.sql`。

### Neo4j

系统使用Neo4j存储交易网络图数据，用于资金流向分析。

图数据库初始化脚本位于`src/backend/scripts/init_graph.cypher`。

## 安全配置

### HTTPS设置

在生产环境中，强烈建议启用HTTPS。可以使用Let's Encrypt获取免费的SSL证书：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 防火墙设置

建议配置防火墙，只开放必要的端口：

```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 安全最佳实践

1. 定期更新系统和依赖包
2. 使用强密码
3. 限制数据库访问
4. 启用日志监控
5. 定期备份数据

## 启动服务

### 使用Systemd管理服务

为了确保系统在服务器重启后自动启动，可以创建Systemd服务：

1. **创建后端服务**：

```bash
sudo nano /etc/systemd/system/crypto-tracker-backend.service
```

添加以下内容：

```
[Unit]
Description=Crypto Tracker Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/crypto-tracker/src/backend
Environment="PATH=/path/to/crypto-tracker/venv/bin"
ExecStart=/path/to/crypto-tracker/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

2. **启用并启动服务**：

```bash
sudo systemctl enable crypto-tracker-backend
sudo systemctl start crypto-tracker-backend
```

3. **检查服务状态**：

```bash
sudo systemctl status crypto-tracker-backend
```

## 系统监控

### 日志监控

系统日志位于以下位置：

- 后端日志：`/path/to/crypto-tracker/logs/`
- Nginx日志：`/var/log/nginx/`
- 数据库日志：`/var/log/postgresql/`

### 性能监控

可以使用Prometheus和Grafana监控系统性能：

1. **安装Prometheus和Grafana**：

```bash
# 安装Prometheus
sudo apt install -y prometheus

# 安装Grafana
sudo apt-get install -y apt-transport-https software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y grafana

# 启动服务
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

2. **配置Prometheus**：

```bash
sudo nano /etc/prometheus/prometheus.yml
```

添加以下配置：

```yaml
scrape_configs:
  - job_name: 'crypto-tracker'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

3. **重启Prometheus**：

```bash
sudo systemctl restart prometheus
```

4. **访问Grafana**：

打开浏览器，访问`http://your-server-ip:3000`，默认用户名和密码为`admin`。

## 常见问题

### 数据库连接问题

**问题**：无法连接到数据库

**解决方案**：
1. 检查数据库服务是否运行：`sudo systemctl status postgresql`
2. 检查数据库连接参数是否正确
3. 检查防火墙设置是否允许数据库连接

### 区块链节点连接问题

**问题**：无法连接到区块链节点

**解决方案**：
1. 检查节点URL是否正确
2. 检查API密钥是否有效
3. 尝试使用不同的节点提供商

### 内存使用过高

**问题**：系统内存使用过高

**解决方案**：
1. 调整PostgreSQL内存设置：`sudo nano /etc/postgresql/14/main/postgresql.conf`
2. 减少监控的钱包数量
3. 增加服务器内存

### 前端无法连接到后端

**问题**：前端无法连接到后端API

**解决方案**：
1. 检查后端服务是否运行：`sudo systemctl status crypto-tracker-backend`
2. 检查Nginx配置是否正确：`sudo nginx -t`
3. 检查前端环境变量中的API URL是否正确
