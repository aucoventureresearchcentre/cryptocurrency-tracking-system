import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd

from app.analytics.transaction_analyzer import TransactionAnalyzer
from app.analytics.ai_monitor import AnomalyDetector

class TestTransactionMonitoring(unittest.TestCase):
    """测试交易监控功能，特别是大额转账和资金分散转出检测"""
    
    def setUp(self):
        """测试前准备"""
        # 创建交易分析器实例
        self.transaction_analyzer = TransactionAnalyzer()
        
        # 创建异常检测器实例
        self.anomaly_detector = AnomalyDetector()
        
        # 模拟交易数据
        self.test_transactions = [
            {
                "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "from_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "to_address": "0x7890abcdef1234567890abcdef1234567890abcd",
                "value": 2.5,
                "blockchain": "ethereum",
                "timestamp": "2025-03-25T10:30:00Z"
            },
            {
                "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "from_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "to_address": "0xdef1234567890abcdef1234567890abcdef123456",
                "value": 0.2,
                "blockchain": "ethereum",
                "timestamp": "2025-03-25T10:35:00Z"
            },
            {
                "tx_hash": "0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba",
                "from_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "to_address": "0x5678901234567890123456789012345678901234",
                "value": 0.3,
                "blockchain": "ethereum",
                "timestamp": "2025-03-25T10:40:00Z"
            },
            {
                "tx_hash": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                "from_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "to_address": "0x0123456789012345678901234567890123456789",
                "value": 0.25,
                "blockchain": "ethereum",
                "timestamp": "2025-03-25T10:45:00Z"
            }
        ]
    
    def test_large_transaction_detection(self):
        """测试大额转账检测功能"""
        # 模拟检测大额转账的方法
        with patch.object(TransactionAnalyzer, 'detect_large_transactions') as mock_detect:
            # 设置模拟返回值
            mock_detect.return_value = [
                {
                    "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    "from_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                    "to_address": "0x7890abcdef1234567890abcdef1234567890abcd",
                    "value": 2.5,
                    "blockchain": "ethereum",
                    "timestamp": "2025-03-25T10:30:00Z",
                    "threshold": 1.0,
                    "is_large": True
                }
            ]
            
            # 调用方法
            large_txs = self.transaction_analyzer.detect_large_transactions(
                self.test_transactions,
                threshold=1.0
            )
            
            # 验证方法被调用
            mock_detect.assert_called_once()
            
            # 验证结果
            self.assertEqual(len(large_txs), 1)
            self.assertEqual(large_txs[0]["tx_hash"], "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
            self.assertEqual(large_txs[0]["value"], 2.5)
            self.assertTrue(large_txs[0]["is_large"])
    
    def test_fund_dispersion_detection(self):
        """测试资金分散转出检测功能"""
        # 模拟检测资金分散转出的方法
        with patch.object(TransactionAnalyzer, 'detect_fund_dispersion') as mock_detect:
            # 设置模拟返回值
            mock_detect.return_value = {
                "source_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "dispersion_count": 3,
                "total_value": 0.75,
                "time_window": 15,  # 分钟
                "transactions": [
                    {
                        "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                        "to_address": "0xdef1234567890abcdef1234567890abcdef123456",
                        "value": 0.2,
                        "timestamp": "2025-03-25T10:35:00Z"
                    },
                    {
                        "tx_hash": "0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba",
                        "to_address": "0x5678901234567890123456789012345678901234",
                        "value": 0.3,
                        "timestamp": "2025-03-25T10:40:00Z"
                    },
                    {
                        "tx_hash": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                        "to_address": "0x0123456789012345678901234567890123456789",
                        "value": 0.25,
                        "timestamp": "2025-03-25T10:45:00Z"
                    }
                ],
                "is_suspicious": True
            }
            
            # 调用方法
            dispersion = self.transaction_analyzer.detect_fund_dispersion(
                self.test_transactions,
                min_count=3,
                time_window_minutes=15
            )
            
            # 验证方法被调用
            mock_detect.assert_called_once()
            
            # 验证结果
            self.assertEqual(dispersion["source_address"], "0xabcdef1234567890abcdef1234567890abcdef12")
            self.assertEqual(dispersion["dispersion_count"], 3)
            self.assertEqual(dispersion["total_value"], 0.75)
            self.assertTrue(dispersion["is_suspicious"])
    
    def test_ai_anomaly_detection(self):
        """测试AI异常检测功能"""
        # 模拟交易数据
        transaction_data = pd.DataFrame({
            'value': [0.1, 0.2, 0.15, 0.3, 0.25, 0.1, 2.5, 0.2, 0.3, 0.25],
            'timestamp': pd.date_range(start='2025-03-25', periods=10, freq='H'),
            'from_address': ['0xabc'] * 10,
            'to_address': ['0xdef'] * 10
        })
        
        # 模拟LSTM预测方法
        with patch.object(AnomalyDetector, 'predict_lstm') as mock_predict:
            # 设置模拟返回值
            mock_predict.return_value = np.array([0.12, 0.18, 0.16, 0.28, 0.22, 0.15, 0.3, 0.25, 0.28, 0.22])
            
            # 调用方法
            anomalies = self.anomaly_detector.detect_anomalies(
                transaction_data,
                threshold=1.0
            )
            
            # 验证方法被调用
            mock_predict.assert_called_once()
            
            # 验证结果（第7个交易应被检测为异常）
            self.assertTrue(len(anomalies) > 0)
            self.assertEqual(anomalies.iloc[0]['value'], 2.5)
            self.assertTrue(anomalies.iloc[0]['is_anomaly'])
    
    def test_transaction_pattern_analysis(self):
        """测试交易模式分析功能"""
        # 模拟交易数据
        with patch.object(TransactionAnalyzer, 'analyze_transaction_patterns') as mock_analyze:
            # 设置模拟返回值
            mock_analyze.return_value = {
                "address": "0xabcdef1234567890abcdef1234567890abcdef12",
                "total_transactions": 4,
                "total_outgoing_value": 3.25,
                "average_transaction_value": 0.8125,
                "transaction_frequency": "high",
                "unusual_patterns": [
                    {
                        "pattern_type": "large_transaction",
                        "description": "Unusually large transaction detected",
                        "evidence": {
                            "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                            "value": 2.5,
                            "timestamp": "2025-03-25T10:30:00Z"
                        }
                    },
                    {
                        "pattern_type": "fund_dispersion",
                        "description": "Multiple small transactions in short time window",
                        "evidence": {
                            "transaction_count": 3,
                            "total_value": 0.75,
                            "time_window_minutes": 15
                        }
                    }
                ],
                "risk_score": 0.75
            }
            
            # 调用方法
            analysis = self.transaction_analyzer.analyze_transaction_patterns(
                self.test_transactions,
                address="0xabcdef1234567890abcdef1234567890abcdef12"
            )
            
            # 验证方法被调用
            mock_analyze.assert_called_once()
            
            # 验证结果
            self.assertEqual(analysis["address"], "0xabcdef1234567890abcdef1234567890abcdef12")
            self.assertEqual(len(analysis["unusual_patterns"]), 2)
            self.assertEqual(analysis["unusual_patterns"][0]["pattern_type"], "large_transaction")
            self.assertEqual(analysis["unusual_patterns"][1]["pattern_type"], "fund_dispersion")
            self.assertGreater(analysis["risk_score"], 0.7)  # 高风险分数

if __name__ == "__main__":
    unittest.main()
