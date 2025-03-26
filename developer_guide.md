# 加密货币追踪系统开发者文档

## 目录

1. [系统架构](#系统架构)
2. [技术栈](#技术栈)
3. [后端服务](#后端服务)
4. [前端应用](#前端应用)
5. [数据库结构](#数据库结构)
6. [API文档](#api文档)
7. [安全机制](#安全机制)
8. [人工智能模块](#人工智能模块)
9. [测试指南](#测试指南)
10. [贡献指南](#贡献指南)

## 系统架构

加密货币追踪系统采用微服务架构，由以下主要组件组成：

### 架构概览

```
+------------------+    +------------------+    +------------------+
|                  |    |                  |    |                  |
|  前端应用        |    |  API网关         |    |  用户管理服务    |
|  (React.js)      |<-->|  (FastAPI)       |<-->|  (FastAPI)       |
|                  |    |                  |    |                  |
+------------------+    +------------------+    +------------------+
                              ^      ^
                              |      |
                              v      v
+------------------+    +------------------+    +------------------+
|                  |    |                  |    |                  |
|  区块链数据服务  |    |  交易分析服务    |    |  警报服务        |
|  (FastAPI)       |<-->|  (FastAPI)       |<-->|  (FastAPI)       |
|                  |    |                  |    |                  |
+------------------+    +------------------+    +------------------+
        ^                       ^                       ^
        |                       |                       |
        v                       v                       v
+------------------+    +------------------+    +------------------+
|                  |    |                  |    |                  |
|  区块链节点      |    |  数据库          |    |  消息队列        |
|  (Bitcoin, ETH)  |    |  (PostgreSQL,    |    |  (RabbitMQ)      |
|                  |    |   TimescaleDB)   |    |                  |
+------------------+    +------------------+    +------------------+
```

### 组件说明

- **前端应用**：基于React.js的单页面应用，提供用户界面
- **API网关**：处理所有客户端请求，负责路由和认证
- **用户管理服务**：处理用户注册、认证和授权
- **区块链数据服务**：从区块链网络获取交易数据
- **交易分析服务**：分析交易模式，检测异常行为
- **警报服务**：生成和管理警报通知
- **区块链节点**：连接到各种区块链网络
- **数据库**：存储用户数据、交易记录和警报信息
- **消息队列**：处理服务间的异步通信

## 技术栈

### 后端技术

- **语言**：Python 3.10+
- **Web框架**：FastAPI
- **ORM**：SQLAlchemy
- **数据库**：
  - PostgreSQL：关系型数据
  - TimescaleDB：时间序列数据
  - Neo4j：图数据库（交易网络分析）
- **缓存**：Redis
- **消息队列**：RabbitMQ
- **区块链接口**：
  - Web3.py (以太坊)
  - python-bitcoinlib (比特币)

### 前端技术

- **语言**：TypeScript
- **框架**：React.js
- **状态管理**：Redux
- **UI组件**：Material-UI
- **图表**：ECharts
- **国际化**：i18next
- **网络请求**：Axios
- **构建工具**：Webpack

### DevOps工具

- **容器化**：Docker
- **编排**：Docker Compose
- **CI/CD**：GitHub Actions
- **监控**：Prometheus + Grafana
- **日志**：ELK Stack (Elasticsearch, Logstash, Kibana)

## 后端服务

### 项目结构

```
/src/backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # 应用入口点
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── models.py              # 数据模型
│   ├── schemas.py             # Pydantic模式
│   ├── security.py            # 安全功能
│   ├── security_middleware.py # 安全中间件
│   ├── encryption.py          # 加密服务
│   ├── blockchain/            # 区块链模块
│   │   ├── __init__.py
│   │   ├── ethereum.py        # 以太坊客户端
│   │   └── bitcoin.py         # 比特币客户端
│   ├── analytics/             # 分析模块
│   │   ├── __init__.py
│   │   ├── transaction_analyzer.py  # 交易分析器
│   │   └── ai_monitor.py      # AI监控
│   └── alerts/                # 警报模块
│       ├── __init__.py
│       └── alert_system.py    # 警报系统
├── tests/                     # 测试目录
│   ├── test_security.py
│   ├── test_encryption.py
│   ├── test_api.py
│   └── test_transaction_monitoring.py
└── requirements.txt           # 依赖项
```

### 主要模块

#### 区块链模块

区块链模块负责与各种区块链网络交互，获取交易数据。

**以太坊客户端** (`ethereum.py`):
- 连接以太坊节点
- 获取交易数据
- 监控地址余额变化
- 解析智能合约交互

**比特币客户端** (`bitcoin.py`):
- 连接比特币节点
- 获取交易数据
- 监控UTXO变化
- 分析交易输入和输出

#### 分析模块

分析模块负责处理和分析交易数据，检测异常行为。

**交易分析器** (`transaction_analyzer.py`):
- 检测大额交易
- 分析交易模式
- 识别资金分散转出
- 计算地址风险评分

**AI监控** (`ai_monitor.py`):
- 使用LSTM模型预测交易模式
- 检测异常交易行为
- 分析地址关联性
- 评估交易风险

#### 警报模块

警报模块负责生成和管理警报通知。

**警报系统** (`alert_system.py`):
- 生成警报
- 管理警报状态
- 发送通知
- 警报统计和报告

### 配置管理

系统使用环境变量和配置文件进行配置管理。主要配置项包括：

- 数据库连接参数
- API密钥和密钥
- 安全设置
- 区块链节点URL
- 警报阈值

配置示例 (`config.py`):

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 应用设置
    APP_NAME: str = "加密货币追踪系统"
    DEBUG: bool = False
    
    # 安全设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key")
    
    # 数据库设置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/crypto_tracker")
    TIMESCALE_URL: str = os.getenv("TIMESCALE_URL", "postgresql://user:password@localhost/timeseries")
    NEO4J_URL: str = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # 区块链设置
    ETH_NODE_URL: str = os.getenv("ETH_NODE_URL", "https://mainnet.infura.io/v3/your-api-key")
    BTC_NODE_URL: str = os.getenv("BTC_NODE_URL", "https://btc.getblock.io/mainnet/")
    BTC_NODE_USER: str = os.getenv("BTC_NODE_USER", "user")
    BTC_NODE_PASSWORD: str = os.getenv("BTC_NODE_PASSWORD", "password")
    
    # 警报设置
    LARGE_TX_THRESHOLD: float = 500000.0
    DISPERSION_COUNT_THRESHOLD: int = 5
    DISPERSION_TIME_WINDOW: int = 60  # 分钟
    
    # CORS设置
    CORS_ORIGINS: list = ["http://localhost:3000"]
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1"]
    
    # 管理员设置
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    
    # HTTPS设置
    USE_HTTPS: bool = False

settings = Settings()
```

## 前端应用

### 项目结构

```
/src/frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── locales/              # 国际化资源
│       ├── en/
│       │   └── translation.json
│       └── zh/
│           └── translation.json
├── src/
│   ├── App.js                # 应用入口
│   ├── index.js              # 渲染入口
│   ├── i18n.js               # 国际化配置
│   ├── contexts/             # React上下文
│   │   └── AuthContext.js    # 认证上下文
│   ├── components/           # 组件
│   │   ├── layouts/
│   │   │   └── MainLayout.js # 主布局
│   │   └── ...
│   ├── pages/                # 页面
│   │   ├── Login.js          # 登录页面
│   │   ├── Register.js       # 注册页面
│   │   ├── Dashboard.js      # 仪表盘
│   │   ├── Wallets.js        # 钱包管理
│   │   ├── Transactions.js   # 交易列表
│   │   ├── Alerts.js         # 警报管理
│   │   └── Analytics.js      # 数据分析
│   ├── services/             # 服务
│   │   ├── api.js            # API客户端
│   │   └── ...
│   └── utils/                # 工具函数
│       └── ...
├── tests/                    # 测试目录
│   ├── Login.test.js
│   ├── Dashboard.test.js
│   └── Alerts.test.js
└── package.json              # 依赖项
```

### 主要组件

#### 认证组件

认证组件处理用户登录、注册和会话管理。

**AuthContext** (`AuthContext.js`):
- 管理用户认证状态
- 处理登录和注册请求
- 存储和刷新访问令牌
- 提供用户信息

#### 页面组件

**仪表盘** (`Dashboard.js`):
- 显示系统概览
- 展示关键指标和统计数据
- 提供最近交易和警报摘要
- 显示交易趋势图表

**钱包管理** (`Wallets.js`):
- 管理监控的钱包地址
- 添加和删除钱包
- 设置监控参数
- 查看钱包详情和交易历史

**交易列表** (`Transactions.js`):
- 显示所有监控的交易
- 筛选和搜索交易
- 查看交易详情
- 追踪资金流向

**警报管理** (`Alerts.js`):
- 显示所有警报
- 筛选和搜索警报
- 处理和更新警报状态
- 查看警报详情

**数据分析** (`Analytics.js`):
- 提供交易分析工具
- 生成可视化图表
- 展示地址关系网络
- 分析交易模式

### 国际化

系统使用i18next实现国际化，支持中文和英文界面。

**国际化配置** (`i18n.js`):
```javascript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    supportedLngs: ['en', 'zh'],
    interpolation: {
      escapeValue: false,
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
  });

export default i18n;
```

## 数据库结构

系统使用多种数据库存储不同类型的数据：

### PostgreSQL (关系型数据)

**用户表** (`users`):
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**钱包监控表** (`wallet_monitors`):
```sql
CREATE TABLE wallet_monitors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    blockchain VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    label VARCHAR(100),
    threshold NUMERIC(20, 8) DEFAULT 500000,
    alert_level VARCHAR(10) DEFAULT 'medium',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blockchain, address)
);
```

**警报表** (`alerts`):
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(10) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    related_address VARCHAR(255),
    status VARCHAR(20) DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    related_data JSONB
);
```

### TimescaleDB (时间序列数据)

**交易记录表** (`transactions`):
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    blockchain VARCHAR(20) NOT NULL,
    tx_hash VARCHAR(255) NOT NULL,
    from_address VARCHAR(255) NOT NULL,
    to_address VARCHAR(255) NOT NULL,
    value NUMERIC(30, 18) NOT NULL,
    gas_price NUMERIC(30, 18),
    gas_used NUMERIC(30, 18),
    block_number INTEGER,
    block_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blockchain, tx_hash)
);

-- 转换为TimescaleDB超表
SELECT create_hypertable('transactions', 'block_timestamp');
```

### Neo4j (图数据库)

**地址节点**:
```cypher
CREATE (a:Address {
    blockchain: 'ethereum',
    address: '0x1234567890abcdef1234567890abcdef12345678',
    first_seen: timestamp(),
    last_seen: timestamp(),
    total_received: 0.0,
    total_sent: 0.0,
    balance: 0.0,
    risk_score: 0.0
})
```

**交易关系**:
```cypher
MATCH (from:Address {address: '0x1234567890abcdef1234567890abcdef12345678'})
MATCH (to:Address {address: '0xabcdef1234567890abcdef1234567890abcdef12'})
CREATE (from)-[t:TRANSACTION {
    tx_hash: '0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba',
    value: 1.5,
    timestamp: timestamp(),
    block_number: 12345678
}]->(to)
```

## API文档

系统提供RESTful API和WebSocket API，用于与前端和其他系统集成。

### 认证API

#### 获取访问令牌

```
POST /api/v1/auth/token
```

请求体:
```json
{
  "username": "user123",
  "password": "password123"
}
```

响应:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 注册新用户

```
POST /api/v1/auth/register
```

请求体:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123"
}
```

响应:
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "role": "user",
  "is_active": true
}
```

### 钱包API

#### 获取监控钱包列表

```
GET /api/v1/wallets
```

响应:
```json
[
  {
    "id": 1,
    "blockchain": "ethereum",
    "address": "0x1234567890abcdef1234567890abcdef12345678",
    "label": "主钱包",
    "threshold": 500000,
    "alert_level": "high",
    "is_active": true
  }
]
```

#### 添加监控钱包

```
POST /api/v1/wallets
```

请求体:
```json
{
  "blockchain": "ethereum",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "主钱包",
  "threshold": 500000,
  "alert_level": "high"
}
```

### 交易API

#### 获取交易列表

```
GET /api/v1/transactions
```

查询参数:
- `blockchain`: 区块链网络
- `address`: 钱包地址
- `start_time`: 开始时间
- `end_time`: 结束时间
- `min_value`: 最小金额
- `max_value`: 最大金额
- `limit`: 返回记录数量
- `offset`: 分页偏移量

响应:
```json
{
  "total": 100,
  "items": [
    {
      "blockchain": "ethereum",
      "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
      "from_address": "0x1234567890abcdef1234567890abcdef12345678",
      "to_address": "0xabcdef1234567890abcdef1234567890abcdef12",
      "value": 2.5,
      "block_timestamp": "2025-03-25T10:30:00Z",
      "status": "confirmed"
    }
  ]
}
```

### 警报API

#### 获取警报列表

```
GET /api/v1/alerts
```

查询参数:
- `alert_type`: 警报类型
- `severity`: 严重程度
- `status`: 状态
- `start_time`: 开始时间
- `end_time`: 结束时间
- `limit`: 返回记录数量
- `offset`: 分页偏移量

响应:
```json
{
  "total": 50,
  "items": [
    {
      "id": 1,
      "alert_type": "large_transaction",
      "severity": "high",
      "title": "大额转账警报",
      "description": "检测到大额转账: 2.5 ETH",
      "related_address": "0x1234567890abcdef1234567890abcdef12345678",
      "status": "new",
      "created_at": "2025-03-25T10:35:00Z"
    }
  ]
}
```

#### 更新警报状态

```
PATCH /api/v1/alerts/{alert_id}
```

请求体:
```json
{
  "status": "resolved",
  "notes": "已确认为正常交易"
}
```

### WebSocket API

系统提供WebSocket API，用于实时更新和通知。

#### 连接WebSocket

```
WebSocket: /ws
```

认证:
```
Authorization: Bearer {access_token}
```

#### 订阅主题

```json
{
  "action": "subscribe",
  "topics": ["alerts", "transactions"]
}
```

#### 接收消息

警报消息:
```json
{
  "type": "alert",
  "data": {
    "id": 1,
    "alert_type": "large_transaction",
    "severity": "high",
    "title": "大额转账警报",
    "description": "检测到大额转账: 2.5 ETH",
    "related_address": "0x1234567890abcdef1234567890abcdef12345678",
    "status": "new",
    "created_at": "2025-03-25T10:35:00Z"
  }
}
```

交易消息:
```json
{
  "type": "transaction",
  "data": {
    "blockchain": "ethereum",
    "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "from_address": "0x1234567890abcdef1234567890abcdef12345678",
    "to_address": "0xabcdef1234567890abcdef1234567890abcdef12",
    "value": 2.5,
    "block_timestamp": "2025-03-25T10:30:00Z",
    "status": "confirmed"
  }
}
```

## 安全机制

系统实现了多层安全机制，保护用户数据和防止黑客攻击。

### 认证与授权

系统使用JWT（JSON Web Token）进行认证，实现基于角色的访问控制。

**认证流程**:
1. 用户提供用户名和密码
2. 服务器验证凭据并生成JWT
3. 客户端在后续请求中包含JWT
4. 服务器验证JWT并授权访问

**角色和权限**:
- `admin`: 管理员权限，可访问所有功能
- `monitor`: 监控权限，可访问监控和分析功能
- `user`: 用户权限，可访问基本功能

### 数据加密

系统使用多种加密技术保护敏感数据。

**存储加密**:
- 密码使用PBKDF2-SHA256哈希存储
- 敏感数据（如电子邮件、API密钥）使用Fernet对称加密存储
- 加密密钥使用环境变量安全存储

**传输加密**:
- 所有API通信使用HTTPS/TLS加密
- WebSocket连接使用WSS（WebSocket Secure）

### 防DDoS攻击措施

系统实现了多种防DDoS攻击措施。

**请求限流**:
- 基于IP的请求速率限制
- 基于用户的API调用限制
- 突发流量控制

**IP黑名单**:
- 自动检测和阻止可疑IP
- 记录和分析可疑活动
- 手动添加和管理黑名单

**异常流量检测**:
- 监控请求模式和频率
- 检测异常请求行为
- 自动阻止异常流量

### 安全中间件

系统使用多种安全中间件保护API端点。

**CORS中间件**:
- 限制跨域请求
- 配置允许的源、方法和头部

**SQL注入防护**:
- 使用参数化查询
- 验证和清理用户输入
- 检测SQL注入模式

**XSS防护**:
- 内容安全策略（CSP）
- 输入验证和输出编码
- 检测XSS攻击模式

## 人工智能模块

系统使用多种人工智能技术分析交易数据和检测异常行为。

### 异常检测模型

**LSTM模型**:
- 预测正常交易模式
- 检测偏离预测的异常交易
- 学习地址的历史交易行为

**实现** (`ai_monitor.py`):
```python
def predict_lstm(self, data, sequence_length=10):
    """
    使用LSTM模型预测交易模式
    
    Args:
        data: 包含交易数据的DataFrame
        sequence_length: 序列长度
        
    Returns:
        预测值数组
    """
    # 准备数据
    X, y = self._prepare_sequences(data, sequence_length)
    
    # 创建模型
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(sequence_length, 1), return_sequences=False),
        Dense(1)
    ])
    
    # 编译模型
    model.compile(optimizer='adam', loss='mse')
    
    # 训练模型
    model.fit(X, y, epochs=50, verbose=0)
    
    # 预测
    predictions = model.predict(X)
    
    return predictions.flatten()
```

### 资金流向分析

**图算法**:
- 构建交易网络图
- 分析资金流向路径
- 检测环形交易和混币行为

**实现** (`transaction_analyzer.py`):
```python
def analyze_fund_flow(self, address, depth=3):
    """
    分析资金流向
    
    Args:
        address: 起始地址
        depth: 分析深度
        
    Returns:
        资金流向图
    """
    # 连接Neo4j
    driver = GraphDatabase.driver(
        settings.NEO4J_URL,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    
    with driver.session() as session:
        # 执行Cypher查询
        result = session.run("""
            MATCH path = (start:Address {address: $address})-[:TRANSACTION*1..$depth]->(end:Address)
            RETURN path
        """, address=address, depth=depth)
        
        # 处理结果
        flow_graph = self._process_graph_result(result)
    
    driver.close()
    
    return flow_graph
```

### 风险评估

**机器学习分类器**:
- 评估地址风险
- 识别可疑交易模式
- 生成风险评分

**实现** (`transaction_analyzer.py`):
```python
def calculate_risk_score(self, features):
    """
    计算风险评分
    
    Args:
        features: 特征向量
        
    Returns:
        风险评分 (0-1)
    """
    # 加载模型
    model = joblib.load('models/risk_classifier.pkl')
    
    # 预测风险
    risk_score = model.predict_proba([features])[0][1]
    
    return risk_score
```

## 测试指南

系统包含全面的测试套件，确保功能正确性和代码质量。

### 后端测试

**运行测试**:
```bash
cd src/backend
pytest
```

**测试文件**:
- `test_security.py`: 测试安全模块
- `test_encryption.py`: 测试加密模块
- `test_api.py`: 测试API端点
- `test_transaction_monitoring.py`: 测试交易监控功能

### 前端测试

**运行测试**:
```bash
cd src/frontend
npm test
```

**测试文件**:
- `Login.test.js`: 测试登录组件
- `Dashboard.test.js`: 测试仪表盘组件
- `Alerts.test.js`: 测试警报组件

### 集成测试

**运行测试**:
```bash
cd src/backend
pytest -m integration
```

**测试场景**:
- 用户注册和登录
- 添加监控钱包
- 检测大额交易
- 生成和处理警报

## 贡献指南

我们欢迎社区贡献，帮助改进加密货币追踪系统。

### 贡献流程

1. Fork项目仓库
2. 创建功能分支
3. 提交更改
4. 运行测试
5. 提交Pull Request

### 代码风格

- **Python**: 遵循PEP 8风格指南
- **JavaScript**: 遵循Airbnb JavaScript风格指南
- **提交消息**: 遵循约定式提交规范

### 问题报告

报告问题时，请提供以下信息：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、浏览器等）

### 功能请求

请求新功能时，请提供以下信息：
- 功能描述
- 使用场景
- 预期行为
- 可能的实现方式
