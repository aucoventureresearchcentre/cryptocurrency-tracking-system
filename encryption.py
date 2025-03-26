import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Any, Optional

class EncryptionService:
    """加密服务，用于敏感数据的加密和解密"""
    
    def __init__(self, encryption_key: str):
        """
        初始化加密服务
        
        Args:
            encryption_key: 用于生成加密密钥的主密钥
        """
        # 从主密钥派生加密密钥
        salt = b'crypto_tracker_salt'  # 在生产环境中应使用随机盐并安全存储
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """
        加密字符串数据
        
        Args:
            data: 要加密的字符串
            
        Returns:
            加密后的字符串（Base64编码）
        """
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密字符串数据
        
        Args:
            encrypted_data: 加密的字符串（Base64编码）
            
        Returns:
            解密后的原始字符串
        """
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_dict(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """
        加密字典中的敏感字段
        
        Args:
            data: 包含数据的字典
            sensitive_fields: 需要加密的敏感字段列表
            
        Returns:
            处理后的字典，敏感字段已加密
        """
        result = data.copy()
        for field in sensitive_fields:
            if field in result and result[field]:
                if isinstance(result[field], str):
                    result[field] = self.encrypt(result[field])
        return result
    
    def decrypt_dict(self, data: Dict[str, Any], encrypted_fields: list) -> Dict[str, Any]:
        """
        解密字典中的加密字段
        
        Args:
            data: 包含加密数据的字典
            encrypted_fields: 已加密的字段列表
            
        Returns:
            处理后的字典，加密字段已解密
        """
        result = data.copy()
        for field in encrypted_fields:
            if field in result and result[field]:
                if isinstance(result[field], str):
                    try:
                        result[field] = self.decrypt(result[field])
                    except Exception:
                        # 如果解密失败，保留原始值
                        pass
        return result

class SecureStorage:
    """安全存储服务，用于敏感配置和API密钥的管理"""
    
    def __init__(self, encryption_service: EncryptionService):
        """
        初始化安全存储服务
        
        Args:
            encryption_service: 用于加密和解密数据的加密服务
        """
        self.encryption_service = encryption_service
        self.storage_file = os.path.join(os.path.dirname(__file__), 'secure_storage.enc')
        self.storage = self._load_storage()
    
    def _load_storage(self) -> Dict[str, str]:
        """
        从文件加载加密的存储数据
        
        Returns:
            解密后的存储数据字典
        """
        if not os.path.exists(self.storage_file):
            return {}
        
        try:
            with open(self.storage_file, 'r') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return {}
                decrypted_data = self.encryption_service.decrypt(encrypted_data)
                return eval(decrypted_data)  # 在生产环境中应使用更安全的序列化方法，如JSON
        except Exception as e:
            print(f"Error loading secure storage: {e}")
            return {}
    
    def _save_storage(self) -> None:
        """将存储数据加密并保存到文件"""
        try:
            encrypted_data = self.encryption_service.encrypt(str(self.storage))
            with open(self.storage_file, 'w') as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saving secure storage: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取存储的值
        
        Args:
            key: 存储键
            default: 如果键不存在，返回的默认值
            
        Returns:
            存储的值或默认值
        """
        return self.storage.get(key, default)
    
    def set(self, key: str, value: str) -> None:
        """
        设置存储值
        
        Args:
            key: 存储键
            value: 要存储的值
        """
        self.storage[key] = value
        self._save_storage()
    
    def delete(self, key: str) -> None:
        """
        删除存储的键值对
        
        Args:
            key: 要删除的存储键
        """
        if key in self.storage:
            del self.storage[key]
            self._save_storage()
    
    def clear(self) -> None:
        """清除所有存储的数据"""
        self.storage = {}
        self._save_storage()

# 敏感字段列表
SENSITIVE_FIELDS = [
    'wallet_address',
    'private_key',
    'api_key',
    'api_secret',
    'password',
    'email',
    'phone',
    'ip_address'
]
