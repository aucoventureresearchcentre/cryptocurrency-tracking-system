from web3 import Web3
from typing import Dict, List, Optional, Any
import logging
import time
from datetime import datetime
import json

from app.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EthereumClient:
    """以太坊区块链客户端"""
    
    def __init__(self, rpc_url: str = settings.ETHEREUM_RPC_URL):
        """初始化以太坊客户端"""
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            logger.error(f"无法连接到以太坊节点: {rpc_url}")
            raise ConnectionError(f"无法连接到以太坊节点: {rpc_url}")
        logger.info(f"成功连接到以太坊节点: {rpc_url}")
        
    def get_latest_block_number(self) -> int:
        """获取最新区块号"""
        return self.w3.eth.block_number
    
    def get_block(self, block_identifier: int) -> Dict[str, Any]:
        """获取区块信息"""
        block = self.w3.eth.get_block(block_identifier, full_transactions=True)
        return dict(block)
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """获取交易信息"""
        tx_hash_bytes = self.w3.to_bytes(hexstr=tx_hash)
        tx = self.w3.eth.get_transaction(tx_hash_bytes)
        return dict(tx)
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """获取交易收据"""
        tx_hash_bytes = self.w3.to_bytes(hexstr=tx_hash)
        receipt = self.w3.eth.get_transaction_receipt(tx_hash_bytes)
        return dict(receipt)
    
    def get_balance(self, address: str) -> float:
        """获取地址余额（以ETH为单位）"""
        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def get_transactions_by_address(self, address: str, start_block: int, end_block: int) -> List[Dict[str, Any]]:
        """获取地址的交易（简化版，实际应使用索引服务如Etherscan API）"""
        transactions = []
        for block_num in range(start_block, end_block + 1):
            try:
                block = self.get_block(block_num)
                for tx in block['transactions']:
                    if isinstance(tx, dict):  # 确保tx是字典
                        if tx.get('from', '').lower() == address.lower() or tx.get('to', '').lower() == address.lower():
                            transactions.append(tx)
            except Exception as e:
                logger.error(f"获取区块 {block_num} 交易时出错: {str(e)}")
        return transactions
    
    def format_transaction(self, tx: Dict[str, Any], receipt: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """格式化交易数据"""
        # 获取交易收据（如果未提供）
        if receipt is None and 'blockHash' in tx and tx['blockHash'] is not None:
            try:
                receipt = self.get_transaction_receipt(tx['hash'].hex())
            except Exception as e:
                logger.error(f"获取交易收据时出错: {str(e)}")
                receipt = {}
        
        # 计算交易费用
        gas_price = tx.get('gasPrice', 0)
        gas_used = receipt.get('gasUsed', 0) if receipt else 0
        transaction_fee = self.w3.from_wei(gas_price * gas_used, 'ether') if gas_price and gas_used else 0
        
        # 获取区块时间戳
        block_timestamp = None
        if 'blockNumber' in tx and tx['blockNumber'] is not None:
            try:
                block = self.w3.eth.get_block(tx['blockNumber'])
                block_timestamp = datetime.fromtimestamp(block.timestamp)
            except Exception as e:
                logger.error(f"获取区块时间戳时出错: {str(e)}")
        
        # 格式化交易数据
        formatted_tx = {
            'blockchain': 'ethereum',
            'tx_hash': tx.get('hash', '').hex() if hasattr(tx.get('hash', ''), 'hex') else tx.get('hash', ''),
            'block_number': tx.get('blockNumber'),
            'block_timestamp': block_timestamp,
            'from_address': tx.get('from', ''),
            'to_address': tx.get('to', ''),
            'value': self.w3.from_wei(tx.get('value', 0), 'ether'),
            'fee': transaction_fee,
            'status': 'success' if receipt and receipt.get('status') == 1 else 'failed' if receipt else 'pending',
            'data': {
                'input': tx.get('input', ''),
                'nonce': tx.get('nonce'),
                'gas': tx.get('gas'),
                'gas_price': self.w3.from_wei(tx.get('gasPrice', 0), 'gwei'),
                'gas_used': gas_used,
                'logs': receipt.get('logs', []) if receipt else []
            }
        }
        
        return formatted_tx
    
    def monitor_new_transactions(self, callback, poll_interval: int = 15):
        """监控新交易（简化版，实际应使用WebSocket或事件订阅）"""
        last_block = self.get_latest_block_number()
        logger.info(f"开始监控新交易，从区块 {last_block}")
        
        while True:
            try:
                current_block = self.get_latest_block_number()
                if current_block > last_block:
                    logger.info(f"发现新区块: {last_block+1} 到 {current_block}")
                    for block_num in range(last_block + 1, current_block + 1):
                        block = self.get_block(block_num)
                        for tx in block['transactions']:
                            if isinstance(tx, dict):  # 确保tx是字典
                                formatted_tx = self.format_transaction(tx)
                                callback(formatted_tx)
                    last_block = current_block
                
                time.sleep(poll_interval)
            except Exception as e:
                logger.error(f"监控交易时出错: {str(e)}")
                time.sleep(poll_interval)
    
    def is_large_transaction(self, tx: Dict[str, Any], threshold: float = settings.LARGE_TRANSACTION_THRESHOLD) -> bool:
        """检查是否为大额交易"""
        return tx.get('value', 0) >= threshold
    
    def detect_fund_dispersion(self, address: str, time_window: int = 3600, threshold: int = 5) -> bool:
        """检测资金分散转出（简化版）
        
        Args:
            address: 要监控的地址
            time_window: 时间窗口（秒）
            threshold: 触发警报的最小转出次数
            
        Returns:
            bool: 是否检测到资金分散转出
        """
        current_block = self.get_latest_block_number()
        # 估算时间窗口内的区块数（以太坊平均出块时间约为15秒）
        blocks_in_window = time_window // 15
        start_block = max(0, current_block - blocks_in_window)
        
        # 获取地址在时间窗口内的交易
        transactions = self.get_transactions_by_address(address, start_block, current_block)
        
        # 筛选出从该地址转出的交易
        outgoing_txs = [tx for tx in transactions if tx.get('from', '').lower() == address.lower()]
        
        # 如果转出交易数量超过阈值，认为是资金分散转出
        return len(outgoing_txs) >= threshold
