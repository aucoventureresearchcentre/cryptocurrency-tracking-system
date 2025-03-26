from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
import json
import networkx as nx
from datetime import datetime, timedelta

from app.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionAnalyzer:
    """交易分析器"""
    
    def __init__(self):
        """初始化交易分析器"""
        # 初始化异常检测模型
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        logger.info("交易分析器初始化完成")
    
    def train_model(self, transactions: List[Dict[str, Any]]):
        """训练异常检测模型"""
        if not transactions:
            logger.warning("没有交易数据用于训练模型")
            return
        
        # 提取特征
        features = self._extract_features(transactions)
        if features.empty:
            logger.warning("无法从交易数据中提取特征")
            return
        
        # 标准化特征
        scaled_features = self.scaler.fit_transform(features)
        
        # 训练模型
        self.model.fit(scaled_features)
        self.is_trained = True
        logger.info(f"异常检测模型训练完成，使用 {len(transactions)} 条交易记录")
    
    def _extract_features(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """从交易中提取特征"""
        features = []
        
        for tx in transactions:
            # 基本特征
            tx_features = {
                'value': float(tx.get('value', 0)),
                'fee': float(tx.get('fee', 0)),
            }
            
            # 添加时间特征
            if 'block_timestamp' in tx and tx['block_timestamp']:
                timestamp = tx['block_timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                tx_features['hour_of_day'] = timestamp.hour
                tx_features['day_of_week'] = timestamp.weekday()
            
            features.append(tx_features)
        
        return pd.DataFrame(features)
    
    def detect_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测异常交易"""
        if not self.is_trained:
            logger.warning("模型尚未训练，无法检测异常")
            return []
        
        if not transactions:
            return []
        
        # 提取特征
        features = self._extract_features(transactions)
        if features.empty:
            return []
        
        # 标准化特征
        scaled_features = self.scaler.transform(features)
        
        # 预测异常分数（越小越异常）
        anomaly_scores = self.model.decision_function(scaled_features)
        predictions = self.model.predict(scaled_features)
        
        # 标记异常交易
        anomalies = []
        for i, (tx, score, pred) in enumerate(zip(transactions, anomaly_scores, predictions)):
            # pred为-1表示异常
            if pred == -1:
                tx_copy = tx.copy()
                tx_copy['anomaly_score'] = float(score)
                tx_copy['is_anomaly'] = True
                anomalies.append(tx_copy)
        
        logger.info(f"检测到 {len(anomalies)} 条异常交易，共 {len(transactions)} 条交易")
        return anomalies
    
    def analyze_transaction(self, tx: Dict[str, Any], related_txs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分析单个交易"""
        analysis = {
            'transaction': tx,
            'risk_score': 0.0,
            'is_suspicious': False,
            'related_entities': [],
            'flow_analysis': {}
        }
        
        # 检查是否为大额交易
        if float(tx.get('value', 0)) >= settings.LARGE_TRANSACTION_THRESHOLD:
            analysis['risk_score'] += 0.5
            analysis['is_suspicious'] = True
            analysis['flow_analysis']['large_transaction'] = True
        
        # 如果有相关交易，分析资金流向
        if related_txs:
            flow_analysis = self.analyze_fund_flow(tx, related_txs)
            analysis['flow_analysis'].update(flow_analysis)
            
            # 如果检测到资金分散，增加风险分数
            if flow_analysis.get('fund_dispersion', False):
                analysis['risk_score'] += 0.3
                analysis['is_suspicious'] = True
        
        # 根据风险分数确定最终可疑状态
        if analysis['risk_score'] >= 0.7:
            analysis['is_suspicious'] = True
        
        return analysis
    
    def analyze_fund_flow(self, tx: Dict[str, Any], related_txs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析资金流向"""
        flow_analysis = {
            'fund_dispersion': False,
            'dispersion_count': 0,
            'circular_transfer': False,
            'mixing_pattern': False
        }
        
        # 构建交易图
        G = nx.DiGraph()
        
        # 添加当前交易
        from_addr = tx.get('from_address', '')
        to_addr = tx.get('to_address', '')
        if from_addr and to_addr:
            G.add_edge(from_addr, to_addr, **{
                'tx_hash': tx.get('tx_hash', ''),
                'value': float(tx.get('value', 0)),
                'timestamp': tx.get('block_timestamp', datetime.now())
            })
        
        # 添加相关交易
        for rtx in related_txs:
            from_addr = rtx.get('from_address', '')
            to_addr = rtx.get('to_address', '')
            if from_addr and to_addr:
                G.add_edge(from_addr, to_addr, **{
                    'tx_hash': rtx.get('tx_hash', ''),
                    'value': float(rtx.get('value', 0)),
                    'timestamp': rtx.get('block_timestamp', datetime.now())
                })
        
        # 检测资金分散模式
        if from_addr in G:
            out_degree = G.out_degree(from_addr)
            if out_degree > 3:  # 如果一个地址向多个地址转账
                flow_analysis['fund_dispersion'] = True
                flow_analysis['dispersion_count'] = out_degree
        
        # 检测环形转账
        try:
            cycles = list(nx.simple_cycles(G))
            if cycles:
                flow_analysis['circular_transfer'] = True
        except:
            pass
        
        # 检测混币模式（多个输入，多个输出）
        mixing_nodes = [node for node, degree in G.degree() if G.in_degree(node) > 2 and G.out_degree(node) > 2]
        if mixing_nodes:
            flow_analysis['mixing_pattern'] = True
        
        return flow_analysis
    
    def calculate_address_risk(self, address: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算地址风险评分"""
        if not transactions:
            return {
                'address': address,
                'risk_score': 0.0,
                'risk_factors': [],
                'transaction_count': 0
            }
        
        risk_score = 0.0
        risk_factors = []
        
        # 分析交易模式
        outgoing_txs = [tx for tx in transactions if tx.get('from_address', '') == address]
        incoming_txs = [tx for tx in transactions if tx.get('to_address', '') == address]
        
        # 检查大额交易
        large_txs = [tx for tx in transactions if float(tx.get('value', 0)) >= settings.LARGE_TRANSACTION_THRESHOLD]
        if large_txs:
            risk_score += 0.2
            risk_factors.append(f"有{len(large_txs)}笔大额交易")
        
        # 检查资金分散模式
        if len(outgoing_txs) > 0:
            unique_recipients = set(tx.get('to_address', '') for tx in outgoing_txs)
            if len(unique_recipients) > 5 and len(outgoing_txs) / len(unique_recipients) < 2:
                risk_score += 0.3
                risk_factors.append("资金分散转出模式")
        
        # 检查交易频率
        if len(transactions) > 0:
            timestamps = [tx.get('block_timestamp', datetime.now()) for tx in transactions if 'block_timestamp' in tx]
            if timestamps:
                timestamps.sort()
                time_span = (timestamps[-1] - timestamps[0]).total_seconds()
                if time_span > 0:
                    tx_per_day = len(timestamps) / (time_span / 86400)
                    if tx_per_day > 10:
                        risk_score += 0.2
                        risk_factors.append(f"交易频率高 ({tx_per_day:.1f}笔/天)")
        
        # 检查异常交易时间
        night_txs = [tx for tx in transactions if 'block_timestamp' in tx and 
                    isinstance(tx['block_timestamp'], datetime) and 
                    0 <= tx['block_timestamp'].hour < 5]
        if night_txs and len(night_txs) / len(transactions) > 0.3:
            risk_score += 0.1
            risk_factors.append("大量深夜交易")
        
        return {
            'address': address,
            'risk_score': min(risk_score, 1.0),
            'risk_factors': risk_factors,
            'transaction_count': len(transactions)
        }
