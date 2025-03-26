import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input
from tensorflow.keras.optimizers import Adam
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import logging
from typing import List, Dict, Any, Tuple, Optional
import os
import json
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIMonitor:
    """人工智能监控模块"""
    
    def __init__(self, model_path: Optional[str] = None):
        """初始化AI监控模块
        
        Args:
            model_path: 预训练模型路径，如果提供则加载模型
        """
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        self.sequence_length = 10  # 用于预测的序列长度
        
        if model_path and os.path.exists(model_path):
            try:
                self.model = load_model(model_path)
                self.is_trained = True
                logger.info(f"成功加载预训练模型: {model_path}")
            except Exception as e:
                logger.error(f"加载模型时出错: {str(e)}")
        else:
            logger.info("未提供预训练模型，将使用新模型")
    
    def build_model(self, input_shape: Tuple[int, int]):
        """构建LSTM模型
        
        Args:
            input_shape: 输入形状 (sequence_length, features)
        """
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(25))
        model.add(Dense(1))
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        self.model = model
        logger.info("LSTM模型构建完成")
    
    def prepare_data(self, transactions: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """准备训练数据
        
        Args:
            transactions: 交易列表，按时间排序
            
        Returns:
            X: 特征数据
            y: 目标数据
        """
        # 提取特征
        data = []
        for tx in transactions:
            features = {
                'value': float(tx.get('value', 0)),
                'timestamp': tx.get('block_timestamp', datetime.now()).timestamp()
            }
            data.append(features)
        
        df = pd.DataFrame(data)
        
        # 确保数据按时间排序
        df = df.sort_values('timestamp')
        
        # 提取特征和目标
        values = df['value'].values.reshape(-1, 1)
        scaled_values = self.scaler.fit_transform(values)
        
        X, y = [], []
        for i in range(len(scaled_values) - self.sequence_length):
            X.append(scaled_values[i:i+self.sequence_length])
            y.append(scaled_values[i+self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def train(self, transactions: List[Dict[str, Any]], epochs: int = 50, batch_size: int = 32):
        """训练模型
        
        Args:
            transactions: 交易列表，按时间排序
            epochs: 训练轮数
            batch_size: 批次大小
        """
        if len(transactions) < self.sequence_length + 10:
            logger.warning(f"训练数据不足，需要至少 {self.sequence_length + 10} 条交易记录")
            return
        
        # 准备数据
        X, y = self.prepare_data(transactions)
        
        if X.shape[0] == 0 or y.shape[0] == 0:
            logger.warning("无法从交易数据中提取有效特征")
            return
        
        # 构建模型（如果尚未构建）
        if self.model is None:
            self.build_model((X.shape[1], X.shape[2]))
        
        # 训练模型
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
        self.is_trained = True
        logger.info(f"模型训练完成，使用 {len(transactions)} 条交易记录")
    
    def predict_next_transaction(self, recent_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """预测下一笔交易
        
        Args:
            recent_transactions: 最近的交易列表，按时间排序
            
        Returns:
            预测结果
        """
        if not self.is_trained or self.model is None:
            logger.warning("模型尚未训练，无法进行预测")
            return {'predicted_value': None, 'confidence': 0}
        
        if len(recent_transactions) < self.sequence_length:
            logger.warning(f"数据不足，需要至少 {self.sequence_length} 条最近交易记录")
            return {'predicted_value': None, 'confidence': 0}
        
        # 提取特征
        data = []
        for tx in recent_transactions[-self.sequence_length:]:
            features = {
                'value': float(tx.get('value', 0)),
                'timestamp': tx.get('block_timestamp', datetime.now()).timestamp()
            }
            data.append(features)
        
        df = pd.DataFrame(data)
        
        # 确保数据按时间排序
        df = df.sort_values('timestamp')
        
        # 提取特征
        values = df['value'].values.reshape(-1, 1)
        scaled_values = self.scaler.transform(values)
        
        # 准备预测数据
        X = np.array([scaled_values])
        
        # 预测
        scaled_prediction = self.model.predict(X)
        prediction = self.scaler.inverse_transform(scaled_prediction)
        
        return {
            'predicted_value': float(prediction[0][0]),
            'confidence': 0.8  # 简化的置信度计算
        }
    
    def detect_anomalies(self, transactions: List[Dict[str, Any]], threshold: float = 0.5) -> List[Dict[str, Any]]:
        """检测异常交易
        
        Args:
            transactions: 交易列表
            threshold: 异常阈值
            
        Returns:
            异常交易列表
        """
        if not self.is_trained or self.model is None:
            logger.warning("模型尚未训练，无法检测异常")
            return []
        
        anomalies = []
        
        # 按地址分组处理交易
        address_txs = {}
        for tx in transactions:
            from_addr = tx.get('from_address', '')
            if from_addr:
                if from_addr not in address_txs:
                    address_txs[from_addr] = []
                address_txs[from_addr].append(tx)
        
        # 对每个地址的交易序列进行异常检测
        for address, addr_txs in address_txs.items():
            if len(addr_txs) < self.sequence_length:
                continue
            
            # 按时间排序
            addr_txs.sort(key=lambda x: x.get('block_timestamp', datetime.now()))
            
            # 滑动窗口检测
            for i in range(len(addr_txs) - self.sequence_length):
                window = addr_txs[i:i+self.sequence_length]
                next_tx = addr_txs[i+self.sequence_length]
                
                # 预测下一笔交易
                prediction = self.predict_next_transaction(window)
                
                # 计算实际值与预测值的偏差
                if prediction['predicted_value'] is not None:
                    actual_value = float(next_tx.get('value', 0))
                    predicted_value = prediction['predicted_value']
                    
                    # 计算相对偏差
                    if predicted_value > 0:
                        deviation = abs(actual_value - predicted_value) / predicted_value
                        
                        # 如果偏差超过阈值，标记为异常
                        if deviation > threshold:
                            anomaly_tx = next_tx.copy()
                            anomaly_tx['ai_anomaly'] = True
                            anomaly_tx['deviation'] = float(deviation)
                            anomaly_tx['predicted_value'] = float(predicted_value)
                            anomalies.append(anomaly_tx)
        
        logger.info(f"AI检测到 {len(anomalies)} 条异常交易，共 {len(transactions)} 条交易")
        return anomalies
    
    def save_model(self, model_path: str):
        """保存模型
        
        Args:
            model_path: 模型保存路径
        """
        if self.is_trained and self.model is not None:
            try:
                self.model.save(model_path)
                logger.info(f"模型已保存到: {model_path}")
            except Exception as e:
                logger.error(f"保存模型时出错: {str(e)}")
        else:
            logger.warning("模型尚未训练，无法保存")
    
    def monitor_wallet(self, address: str, recent_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """监控钱包活动
        
        Args:
            address: 钱包地址
            recent_transactions: 最近的交易列表
            
        Returns:
            监控结果
        """
        result = {
            'address': address,
            'anomalies_detected': False,
            'risk_level': 'low',
            'predicted_next_transaction': None,
            'unusual_patterns': []
        }
        
        if not recent_transactions:
            return result
        
        # 筛选与该地址相关的交易
        address_txs = [tx for tx in recent_transactions if 
                      tx.get('from_address', '') == address or 
                      tx.get('to_address', '') == address]
        
        if not address_txs:
            return result
        
        # 按时间排序
        address_txs.sort(key=lambda x: x.get('block_timestamp', datetime.now()))
        
        # 检测异常
        anomalies = self.detect_anomalies(address_txs)
        if anomalies:
            result['anomalies_detected'] = True
            result['risk_level'] = 'high' if len(anomalies) > 2 else 'medium'
        
        # 预测下一笔交易
        if len(address_txs) >= self.sequence_length:
            prediction = self.predict_next_transaction(address_txs[-self.sequence_length:])
            result['predicted_next_transaction'] = prediction
        
        # 检测异常模式
        patterns = self._detect_unusual_patterns(address_txs)
        if patterns:
            result['unusual_patterns'] = patterns
            if result['risk_level'] == 'low':
                result['risk_level'] = 'medium'
        
        return result
    
    def _detect_unusual_patterns(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """检测异常模式
        
        Args:
            transactions: 交易列表
            
        Returns:
            检测到的异常模式列表
        """
        patterns = []
        
        if len(transactions) < 3:
            return patterns
        
        # 检查交易频率突然增加
        timestamps = [tx.get('block_timestamp', datetime.now()) for tx in transactions]
        timestamps.sort()
        
        if len(timestamps) >= 5:
            # 计算平均交易间隔
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                        for i in range(len(timestamps)-1)]
            avg_interval = sum(intervals) / len(intervals)
            
            # 检查最近的交易间隔是否明显小于平均值
            recent_intervals = intervals[-3:]
            if recent_intervals and sum(recent_intervals) / len(recent_intervals) < avg_interval * 0.3:
                patterns.append("交易频率突然增加")
        
        # 检查交易金额突然增加
        values = [float(tx.get('value', 0)) for tx in transactions]
        if values:
            avg_value = sum(values) / len(values)
            recent_values = values[-3:]
            if recent_values and sum(recent_values) / len(recent_values) > avg_value * 3:
                patterns.append("交易金额突然增加")
        
        # 检查深夜交易模式
        night_txs = [tx for tx in transactions if 
                    tx.get('block_timestamp', datetime.now()).hour >= 0 and 
                    tx.get('block_timestamp', datetime.now()).hour < 5]
        if night_txs and len(night_txs) / len(transactions) > 0.5:
            patterns.append("频繁深夜交易")
        
        return patterns
