import os
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

import jwt
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("security.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("security")

# 创建限流器
limiter = Limiter(key_func=get_remote_address)

# OAuth2 密码流认证
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/token",
    scopes={
        "user": "标准用户权限",
        "admin": "管理员权限",
        "monitor": "监控权限"
    }
)

# 用户角色权限映射
ROLE_PERMISSIONS = {
    "admin": ["user", "admin", "monitor"],
    "monitor": ["user", "monitor"],
    "user": ["user"]
}

# 密码哈希函数
def get_password_hash(password: str) -> str:
    """使用SHA-256和盐值对密码进行哈希"""
    salt = os.urandom(32)  # 32字节的随机盐值
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # 迭代次数
    )
    # 将盐值和密钥一起存储
    return salt.hex() + ':' + key.hex()

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配哈希值"""
    try:
        salt_hex, key_hex = hashed_password.split(':')
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            100000  # 迭代次数
        )
        return key.hex() == key_hex
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """验证令牌并获取当前用户"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # 检查令牌是否过期
        token_exp = payload.get("exp")
        if token_exp is None or datetime.utcnow() > datetime.fromtimestamp(token_exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": authenticate_value},
            )
        
        # 获取令牌中的权限范围
        token_scopes = payload.get("scopes", [])
    except (jwt.PyJWTError, ValidationError):
        logger.warning(f"Invalid token attempt")
        raise credentials_exception
    
    # 从数据库获取用户
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.warning(f"User not found: {username}")
        raise credentials_exception
    
    # 检查用户是否被禁用
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # 检查用户权限
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    for scope in security_scopes.scopes:
        if scope not in user_permissions:
            logger.warning(f"User {username} attempted to access {scope} without permission")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    # 记录成功的认证
    logger.info(f"User {username} authenticated successfully with scopes: {security_scopes.scopes}")
    return user

# 获取当前活跃用户
async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["user"])
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# 获取当前管理员用户
async def get_current_admin_user(
    current_user: User = Security(get_current_user, scopes=["admin"])
) -> User:
    """获取当前管理员用户"""
    if not current_user.is_active or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# 配置FastAPI应用的安全中间件
def configure_security_middleware(app: FastAPI) -> None:
    """配置FastAPI应用的安全中间件"""
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 可信主机中间件
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # Gzip压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 限流异常处理
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    logger.info("Security middleware configured successfully")

# IP黑名单
class IPBlacklist:
    def __init__(self):
        self.blacklist = set()
        self.suspicious_ips = {}  # IP -> (count, first_seen)
        self.threshold = 10  # 可疑请求阈值
        self.window = 60  # 时间窗口（秒）
    
    def is_blacklisted(self, ip: str) -> bool:
        """检查IP是否在黑名单中"""
        return ip in self.blacklist
    
    def add_to_blacklist(self, ip: str) -> None:
        """将IP添加到黑名单"""
        self.blacklist.add(ip)
        logger.warning(f"IP {ip} added to blacklist")
    
    def record_suspicious_activity(self, ip: str) -> None:
        """记录可疑活动"""
        current_time = time.time()
        
        if ip in self.suspicious_ips:
            count, first_seen = self.suspicious_ips[ip]
            
            # 检查是否在时间窗口内
            if current_time - first_seen <= self.window:
                count += 1
                self.suspicious_ips[ip] = (count, first_seen)
                
                # 如果超过阈值，加入黑名单
                if count >= self.threshold:
                    self.add_to_blacklist(ip)
            else:
                # 重置计数
                self.suspicious_ips[ip] = (1, current_time)
        else:
            self.suspicious_ips[ip] = (1, current_time)

# 创建IP黑名单实例
ip_blacklist = IPBlacklist()

# 检查IP是否在黑名单中的中间件
async def check_ip_blacklist(request, call_next):
    """检查请求IP是否在黑名单中"""
    client_ip = get_remote_address(request)
    
    if ip_blacklist.is_blacklisted(client_ip):
        logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Access denied"}
        )
    
    response = await call_next(request)
    return response

# 敏感数据加密
class DataEncryption:
    def __init__(self, key: str):
        """初始化加密工具"""
        self.key = hashlib.sha256(key.encode()).digest()
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        from cryptography.fernet import Fernet
        f = Fernet(base64.urlsafe_b64encode(self.key))
        return f.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        from cryptography.fernet import Fernet
        f = Fernet(base64.urlsafe_b64encode(self.key))
        return f.decrypt(encrypted_data.encode()).decode()

# 创建数据加密实例
data_encryption = DataEncryption(settings.ENCRYPTION_KEY)

# 安全日志记录
def log_security_event(event_type: str, details: Dict, severity: str = "info") -> None:
    """记录安全事件"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "severity": severity,
        "details": details
    }
    
    if severity == "info":
        logger.info(f"Security event: {event_type} - {details}")
    elif severity == "warning":
        logger.warning(f"Security event: {event_type} - {details}")
    elif severity == "error":
        logger.error(f"Security event: {event_type} - {details}")
    elif severity == "critical":
        logger.critical(f"Security event: {event_type} - {details}")
