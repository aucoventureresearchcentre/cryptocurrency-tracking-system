from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
import os
from datetime import timedelta

from app.database import get_db, engine, Base
from app.models import User
from app.schemas import Token, UserCreate, UserResponse
from app.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_active_user,
    get_current_admin_user,
    configure_security_middleware
)
from app.security_middleware import configure_security_middleware as configure_additional_security_middleware
from app.config import settings
from app.encryption import EncryptionService, SecureStorage, SENSITIVE_FIELDS

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app")

# 创建FastAPI应用
app = FastAPI(
    title="加密货币追踪系统",
    description="实时维护与跟踪加密货币转账信息的系统",
    version="1.0.0",
)

# 配置安全中间件
configure_security_middleware(app)
configure_additional_security_middleware(app)

# 创建加密服务和安全存储
encryption_service = EncryptionService(settings.ENCRYPTION_KEY)
secure_storage = SecureStorage(encryption_service)

# 认证路由
@app.post("/api/v1/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """获取访问令牌"""
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否被禁用
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": [user.role]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

# 用户注册路由
@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """注册新用户"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing username: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    
    # 加密敏感数据
    encrypted_email = encryption_service.encrypt(user_data.email)
    
    new_user = User(
        username=user_data.username,
        email=encrypted_email,
        hashed_password=hashed_password,
        role="user",  # 默认角色
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.username}")
    
    # 解密邮箱用于响应
    new_user.email = user_data.email
    
    return new_user

# 获取当前用户信息
@app.get("/api/v1/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    # 解密敏感数据
    try:
        current_user.email = encryption_service.decrypt(current_user.email)
    except Exception:
        # 如果解密失败，使用占位符
        current_user.email = "******"
    
    return current_user

# 修改密码
@app.post("/api/v1/auth/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改用户密码"""
    # 验证当前密码
    if not verify_password(current_password, current_user.hashed_password):
        logger.warning(f"Failed password change attempt for user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.username}")
    return {"detail": "Password changed successfully"}

# 健康检查路由
@app.get("/api/v1/health")
async def health_check():
    """系统健康检查"""
    return {"status": "ok", "version": "1.0.0"}

# 包含其他路由模块
# from app.routers import wallets, transactions, alerts, analytics
# app.include_router(wallets.router, prefix="/api/v1/wallets", tags=["wallets"])
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
# app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("Application startup")
    
    # 检查是否需要创建管理员用户
    db = next(get_db())
    admin_user = db.query(User).filter(User.role == "admin").first()
    
    if not admin_user and settings.ADMIN_USERNAME and settings.ADMIN_PASSWORD:
        # 创建管理员用户
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
        encrypted_email = encryption_service.encrypt(settings.ADMIN_EMAIL or "admin@example.com")
        
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=encrypted_email,
            hashed_password=hashed_password,
            role="admin",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        logger.info(f"Created admin user: {settings.ADMIN_USERNAME}")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("Application shutdown")

# 主入口点
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile=os.path.join(os.path.dirname(__file__), "key.pem") if settings.USE_HTTPS else None,
        ssl_certfile=os.path.join(os.path.dirname(__file__), "cert.pem") if settings.USE_HTTPS else None,
    )
