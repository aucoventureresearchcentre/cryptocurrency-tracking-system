import os
from dotenv import load_dotenv
from pydantic import BaseModel

# 加载环境变量
load_dotenv()

class Settings(BaseModel):
    """应用配置设置"""
    # 应用基本设置
    APP_NAME: str = "CryptoTracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 数据库设置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cryptotracker")
    TIMESCALE_URL: str = os.getenv("TIMESCALE_URL", "postgresql://postgres:postgres@localhost:5432/cryptotracker_ts")
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # Redis设置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 安全设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 区块链API设置
    ETHEREUM_RPC_URL: str = os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/your-infura-key")
    BITCOIN_RPC_URL: str = os.getenv("BITCOIN_RPC_URL", "http://user:password@localhost:8332")
    
    # 警报设置
    LARGE_TRANSACTION_THRESHOLD: float = float(os.getenv("LARGE_TRANSACTION_THRESHOLD", "500000"))
    
    # 国际化设置
    DEFAULT_LANGUAGE: str = "zh"
    SUPPORTED_LANGUAGES: list = ["zh", "en"]

# 创建设置实例
settings = Settings()
