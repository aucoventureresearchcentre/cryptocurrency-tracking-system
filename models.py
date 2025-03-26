from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    language = Column(String(10), default="zh", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # 关系
    wallet_monitors = relationship("WalletMonitor", back_populates="user")
    alert_configs = relationship("AlertConfig", back_populates="user")
    alerts = relationship("Alert", back_populates="user")


class WalletMonitor(Base):
    """钱包监控模型"""
    __tablename__ = "wallet_monitors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wallet_address = Column(String(100), nullable=False)
    blockchain = Column(String(20), nullable=False)
    label = Column(String(100), nullable=True)
    threshold = Column(Float, nullable=True)
    alert_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="wallet_monitors")
    
    # 复合唯一约束
    __table_args__ = (
        {"UniqueConstraint": ("user_id", "wallet_address", "blockchain")},
    )


class AlertConfig(Base):
    """警报配置模型"""
    __tablename__ = "alert_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_type = Column(String(50), nullable=False)
    threshold = Column(Float, nullable=True)
    enabled = Column(Boolean, default=True)
    notification_channels = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="alert_configs")


class Alert(Base):
    """警报记录模型"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    related_data = Column(JSON, nullable=True)
    status = Column(String(20), default="new", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="alerts")


class Transaction(Base):
    """交易记录模型"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    blockchain = Column(String(20), nullable=False)
    tx_hash = Column(String(100), nullable=False, index=True)
    block_number = Column(Integer, nullable=False)
    block_timestamp = Column(DateTime, nullable=False, index=True)
    from_address = Column(String(100), nullable=False, index=True)
    to_address = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 复合唯一约束
    __table_args__ = (
        {"UniqueConstraint": ("blockchain", "tx_hash")},
    )
