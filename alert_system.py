from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json
from sqlalchemy.orm import Session

from app.models import Alert, AlertConfig, WalletMonitor, User
from app.schemas import AlertCreate
from app.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSystem:
    """警报系统模块"""
    
    def __init__(self, db: Session):
        """初始化警报系统
        
        Args:
            db: 数据库会话
        """
        self.db = db
        logger.info("警报系统初始化完成")
    
    def create_alert(self, alert_data: AlertCreate) -> Alert:
        """创建新警报
        
        Args:
            alert_data: 警报数据
            
        Returns:
            创建的警报对象
        """
        alert = Alert(**alert_data.dict())
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        logger.info(f"创建新警报: {alert.id}, 类型: {alert.alert_type}, 严重性: {alert.severity}")
        return alert
    
    def process_transaction(self, transaction: Dict[str, Any]) -> List[Alert]:
        """处理交易并生成警报
        
        Args:
            transaction: 交易数据
            
        Returns:
            生成的警报列表
        """
        alerts = []
        
        # 检查是否为大额交易
        if self._is_large_transaction(transaction):
            # 查找监控该地址的用户
            from_address = transaction.get('from_address', '')
            to_address = transaction.get('to_address', '')
            blockchain = transaction.get('blockchain', '')
            
            # 查找监控发送方地址的用户
            if from_address:
                monitors = self.db.query(WalletMonitor).filter(
                    WalletMonitor.wallet_address == from_address,
                    WalletMonitor.blockchain == blockchain,
                    WalletMonitor.alert_enabled == True
                ).all()
                
                for monitor in monitors:
                    alert = self._create_large_transaction_alert(
                        transaction, 
                        monitor.user_id, 
                        "outgoing", 
                        monitor.wallet_address
                    )
                    alerts.append(alert)
            
            # 查找监控接收方地址的用户
            if to_address:
                monitors = self.db.query(WalletMonitor).filter(
                    WalletMonitor.wallet_address == to_address,
                    WalletMonitor.blockchain == blockchain,
                    WalletMonitor.alert_enabled == True
                ).all()
                
                for monitor in monitors:
                    alert = self._create_large_transaction_alert(
                        transaction, 
                        monitor.user_id, 
                        "incoming", 
                        monitor.wallet_address
                    )
                    alerts.append(alert)
            
            # 查找设置了全局大额交易警报的用户
            configs = self.db.query(AlertConfig).filter(
                AlertConfig.alert_type == "large_transaction",
                AlertConfig.enabled == True
            ).all()
            
            for config in configs:
                # 检查是否已经为该用户创建了警报
                if not any(a.user_id == config.user_id for a in alerts):
                    alert = self._create_large_transaction_alert(
                        transaction, 
                        config.user_id, 
                        "global", 
                        None
                    )
                    alerts.append(alert)
        
        return alerts
    
    def process_anomaly(self, anomaly: Dict[str, Any]) -> List[Alert]:
        """处理异常并生成警报
        
        Args:
            anomaly: 异常数据
            
        Returns:
            生成的警报列表
        """
        alerts = []
        
        # 确定异常类型
        alert_type = "unknown_anomaly"
        if anomaly.get('ai_anomaly', False):
            alert_type = "ai_anomaly"
        elif anomaly.get('is_anomaly', False):
            alert_type = "statistical_anomaly"
        elif anomaly.get('fund_dispersion', False):
            alert_type = "fund_dispersion"
        
        # 查找监控相关地址的用户
        from_address = anomaly.get('from_address', '')
        blockchain = anomaly.get('blockchain', '')
        
        if from_address:
            monitors = self.db.query(WalletMonitor).filter(
                WalletMonitor.wallet_address == from_address,
                WalletMonitor.blockchain == blockchain,
                WalletMonitor.alert_enabled == True
            ).all()
            
            for monitor in monitors:
                alert = self._create_anomaly_alert(
                    anomaly, 
                    monitor.user_id, 
                    alert_type, 
                    monitor.wallet_address
                )
                alerts.append(alert)
        
        # 查找设置了全局异常警报的用户
        configs = self.db.query(AlertConfig).filter(
            AlertConfig.alert_type == alert_type,
            AlertConfig.enabled == True
        ).all()
        
        for config in configs:
            # 检查是否已经为该用户创建了警报
            if not any(a.user_id == config.user_id for a in alerts):
                alert = self._create_anomaly_alert(
                    anomaly, 
                    config.user_id, 
                    alert_type, 
                    None
                )
                alerts.append(alert)
        
        return alerts
    
    def _is_large_transaction(self, transaction: Dict[str, Any]) -> bool:
        """检查是否为大额交易
        
        Args:
            transaction: 交易数据
            
        Returns:
            是否为大额交易
        """
        value = float(transaction.get('value', 0))
        return value >= settings.LARGE_TRANSACTION_THRESHOLD
    
    def _create_large_transaction_alert(
        self, 
        transaction: Dict[str, Any], 
        user_id: int, 
        direction: str, 
        wallet_address: Optional[str]
    ) -> Alert:
        """创建大额交易警报
        
        Args:
            transaction: 交易数据
            user_id: 用户ID
            direction: 交易方向 (outgoing/incoming/global)
            wallet_address: 钱包地址
            
        Returns:
            创建的警报对象
        """
        value = float(transaction.get('value', 0))
        blockchain = transaction.get('blockchain', '')
        tx_hash = transaction.get('tx_hash', '')
        from_address = transaction.get('from_address', '')
        to_address = transaction.get('to_address', '')
        
        # 确定警报标题和描述
        if direction == "outgoing":
            title = f"监控到大额转出交易: {value} {blockchain.upper()}"
            description = f"您监控的钱包 {wallet_address} 转出了 {value} {blockchain.upper()} 到地址 {to_address}"
        elif direction == "incoming":
            title = f"监控到大额转入交易: {value} {blockchain.upper()}"
            description = f"您监控的钱包 {wallet_address} 收到了来自 {from_address} 的 {value} {blockchain.upper()}"
        else:  # global
            title = f"监控到大额交易: {value} {blockchain.upper()}"
            description = f"检测到从 {from_address} 到 {to_address} 的大额交易，金额为 {value} {blockchain.upper()}"
        
        # 创建警报数据
        alert_data = AlertCreate(
            user_id=user_id,
            alert_type="large_transaction",
            severity="high",
            title=title,
            description=description,
            related_data={
                "transaction": {
                    "blockchain": blockchain,
                    "tx_hash": tx_hash,
                    "from_address": from_address,
                    "to_address": to_address,
                    "value": value
                },
                "direction": direction,
                "wallet_address": wallet_address
            },
            status="new"
        )
        
        # 创建警报
        return self.create_alert(alert_data)
    
    def _create_anomaly_alert(
        self, 
        anomaly: Dict[str, Any], 
        user_id: int, 
        alert_type: str, 
        wallet_address: Optional[str]
    ) -> Alert:
        """创建异常警报
        
        Args:
            anomaly: 异常数据
            user_id: 用户ID
            alert_type: 警报类型
            wallet_address: 钱包地址
            
        Returns:
            创建的警报对象
        """
        blockchain = anomaly.get('blockchain', '')
        tx_hash = anomaly.get('tx_hash', '')
        from_address = anomaly.get('from_address', '')
        to_address = anomaly.get('to_address', '')
        
        # 确定警报标题和描述
        if alert_type == "ai_anomaly":
            title = "AI检测到异常交易模式"
            description = f"人工智能系统检测到与地址 {from_address} 相关的异常交易模式"
        elif alert_type == "statistical_anomaly":
            title = "检测到统计异常交易"
            description = f"系统检测到与地址 {from_address} 相关的统计异常交易"
        elif alert_type == "fund_dispersion":
            title = "检测到资金分散转出"
            description = f"系统检测到地址 {from_address} 的资金分散转出模式"
        else:
            title = "检测到未知异常"
            description = f"系统检测到与地址 {from_address} 相关的未知异常"
        
        # 如果是监控特定钱包的警报，添加相关信息
        if wallet_address:
            description += f"，这与您监控的钱包 {wallet_address} 相关"
        
        # 创建警报数据
        alert_data = AlertCreate(
            user_id=user_id,
            alert_type=alert_type,
            severity="medium" if alert_type != "fund_dispersion" else "high",
            title=title,
            description=description,
            related_data={
                "anomaly": anomaly,
                "wallet_address": wallet_address
            },
            status="new"
        )
        
        # 创建警报
        return self.create_alert(alert_data)
    
    def get_user_alerts(self, user_id: int, status: Optional[str] = None, limit: int = 100) -> List[Alert]:
        """获取用户警报
        
        Args:
            user_id: 用户ID
            status: 警报状态过滤
            limit: 返回结果数量限制
            
        Returns:
            警报列表
        """
        query = self.db.query(Alert).filter(Alert.user_id == user_id)
        
        if status:
            query = query.filter(Alert.status == status)
        
        query = query.order_by(Alert.created_at.desc()).limit(limit)
        
        return query.all()
    
    def update_alert_status(self, alert_id: int, status: str) -> Optional[Alert]:
        """更新警报状态
        
        Args:
            alert_id: 警报ID
            status: 新状态
            
        Returns:
            更新后的警报对象，如果不存在则返回None
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        
        if alert:
            alert.status = status
            if status == "resolved":
                alert.resolved_at = datetime.utcnow()
            alert.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(alert)
            logger.info(f"更新警报 {alert_id} 状态为 {status}")
        
        return alert
