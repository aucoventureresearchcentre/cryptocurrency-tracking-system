from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    language: str = "zh"


class UserCreate(UserBase):
    """用户创建模型"""
    password: str


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    language: Optional[str] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    role: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDB):
    """用户响应模型"""
    pass


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None


class WalletMonitorBase(BaseModel):
    """钱包监控基础模型"""
    wallet_address: str
    blockchain: str
    label: Optional[str] = None
    threshold: Optional[float] = None
    alert_enabled: bool = True


class WalletMonitorCreate(WalletMonitorBase):
    """钱包监控创建模型"""
    pass


class WalletMonitorUpdate(BaseModel):
    """钱包监控更新模型"""
    label: Optional[str] = None
    threshold: Optional[float] = None
    alert_enabled: Optional[bool] = None


class WalletMonitorInDB(WalletMonitorBase):
    """数据库中的钱包监控模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class WalletMonitor(WalletMonitorInDB):
    """钱包监控响应模型"""
    pass


class AlertConfigBase(BaseModel):
    """警报配置基础模型"""
    alert_type: str
    threshold: Optional[float] = None
    enabled: bool = True
    notification_channels: Optional[Dict[str, Any]] = None


class AlertConfigCreate(AlertConfigBase):
    """警报配置创建模型"""
    pass


class AlertConfigUpdate(BaseModel):
    """警报配置更新模型"""
    threshold: Optional[float] = None
    enabled: Optional[bool] = None
    notification_channels: Optional[Dict[str, Any]] = None


class AlertConfigInDB(AlertConfigBase):
    """数据库中的警报配置模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AlertConfig(AlertConfigInDB):
    """警报配置响应模型"""
    pass


class AlertBase(BaseModel):
    """警报基础模型"""
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    related_data: Optional[Dict[str, Any]] = None
    status: str = "new"


class AlertCreate(AlertBase):
    """警报创建模型"""
    user_id: int


class AlertUpdate(BaseModel):
    """警报更新模型"""
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None


class AlertInDB(AlertBase):
    """数据库中的警报模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Alert(AlertInDB):
    """警报响应模型"""
    pass


class TransactionBase(BaseModel):
    """交易基础模型"""
    blockchain: str
    tx_hash: str
    block_number: int
    block_timestamp: datetime
    from_address: str
    to_address: str
    value: float
    fee: float
    status: str
    data: Optional[Dict[str, Any]] = None


class TransactionCreate(TransactionBase):
    """交易创建模型"""
    pass


class TransactionInDB(TransactionBase):
    """数据库中的交易模型"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Transaction(TransactionInDB):
    """交易响应模型"""
    pass


class TransactionAnalysis(BaseModel):
    """交易分析模型"""
    transaction: Transaction
    risk_score: float
    is_suspicious: bool
    related_entities: List[Dict[str, Any]]
    flow_analysis: Dict[str, Any]


class AddressAnalysis(BaseModel):
    """地址分析模型"""
    address: str
    blockchain: str
    balance: float
    total_received: float
    total_sent: float
    transaction_count: int
    first_seen: datetime
    last_seen: datetime
    risk_score: float
    tags: List[str]
    related_addresses: List[Dict[str, Any]]
