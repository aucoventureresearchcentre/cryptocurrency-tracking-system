import bitcoinlib
from bitcoinlib.services.services import Service
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from app.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitcoinClient:
    """比特币区块链客户端"""
    
    def __init__(self, rpc_url: str = settings.BITCOIN_RPC_URL):
        """初始化比特币客户端"""
        try:
            self.service = Service(network='bitcoin')
            logger.info("成功初始化比特币客户端")
        except Exception as e:
            logger.error(f"初始化比特币客户端时出错: {str(e)}")
            raise ConnectionError(f"初始化比特币客户端时出错: {str(e)}")
    
    def get_latest_block_number(self) -> int:
        """获取最新区块号"""
        return self.service.blockcount()
    
    def get_block(self, block_identifier: int) -> Dict[str, Any]:
        """获取区块信息"""
        block = self.service.getblock(block_identifier, parse_transactions=True)
        return block
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """获取交易信息"""
        tx = self.service.gettransaction(tx_hash)
        return tx
    
    def get_balance(self, address: str) -> float:
        """获取地址余额（以BTC为单位）"""
        balance = self.service.getbalance(address)
        return balance
    
    def get_transactions_by_address(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取地址的交易"""
        transactions = self.service.gettransactions(address, limit=limit)
        return transactions
    
    def format_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """格式化交易数据"""
        # 计算交易价值（输入总和 - 输出总和）
        input_value = sum(inp.get('value', 0) for inp in tx.get('inputs', []))
        output_value = sum(out.get('value', 0) for out in tx.get('outputs', []))
        fee = input_value - output_value if input_value > output_value else 0
        
        # 确定交易方向和相关地址
        from_addresses = [inp.get('address', '') for inp in tx.get('inputs', [])]
        to_addresses = [out.get('address', '') for out in tx.get('outputs', [])]
        
        # 格式化交易数据
        formatted_tx = {
            'blockchain': 'bitcoin',
            'tx_hash': tx.get('txid', ''),
            'block_number': tx.get('block_height'),
            'block_timestamp': datetime.fromtimestamp(tx.get('date', 0)),
            'from_address': ','.join(filter(None, from_addresses)),
            'to_address': ','.join(filter(None, to_addresses)),
            'value': output_value,
            'fee': fee,
            'status': 'success' if tx.get('confirmations', 0) > 0 else 'pending',
            'data': {
                'confirmations': tx.get('confirmations', 0),
                'size': tx.get('size', 0),
                'inputs': tx.get('inputs', []),
                'outputs': tx.get('outputs', [])
            }
        }
        
        return formatted_tx
    
    def is_large_transaction(self, tx: Dict[str, Any], threshold: float = settings.LARGE_TRANSACTION_THRESHOLD) -> bool:
        """检查是否为大额交易"""
        # 计算交易输出总和
        output_value = sum(out.get('value', 0) for out in tx.get('outputs', []))
        return output_value >= threshold
    
    def detect_fund_dispersion(self, address: str, time_window: int = 86400, threshold: int = 5) -> bool:
        """检测资金分散转出
        
        Args:
            address: 要监控的地址
            time_window: 时间窗口（秒）
            threshold: 触发警报的最小转出次数
            
        Returns:
            bool: 是否检测到资金分散转出
        """
        # 获取地址的交易
        transactions = self.get_transactions_by_address(address)
        
        # 筛选出时间窗口内的交易
        current_time = datetime.now().timestamp()
        recent_txs = [tx for tx in transactions if current_time - tx.get('date', 0) <= time_window]
        
        # 筛选出从该地址转出的交易
        outgoing_txs = []
        for tx in recent_txs:
            inputs = tx.get('inputs', [])
            if any(inp.get('address') == address for inp in inputs):
                outgoing_txs.append(tx)
        
        # 如果转出交易数量超过阈值，认为是资金分散转出
        return len(outgoing_txs) >= threshold
