import unittest
from unittest.mock import patch, MagicMock
import os
import base64

from app.encryption import EncryptionService, SecureStorage, SENSITIVE_FIELDS

class TestEncryption(unittest.TestCase):
    """测试加密模块功能"""
    
    def setUp(self):
        """测试前准备"""
        self.test_key = "test_encryption_key_123"
        self.encryption_service = EncryptionService(self.test_key)
        
        # 创建临时存储文件路径
        self.temp_storage_path = "/tmp/test_secure_storage.enc"
        
        # 修补存储文件路径
        self.storage_file_patcher = patch.object(
            SecureStorage, 'storage_file', 
            new_callable=lambda: self.temp_storage_path
        )
        self.storage_file_patcher.start()
        
        # 创建安全存储实例
        self.secure_storage = SecureStorage(self.encryption_service)
    
    def tearDown(self):
        """测试后清理"""
        # 停止修补
        self.storage_file_patcher.stop()
        
        # 删除临时存储文件
        if os.path.exists(self.temp_storage_path):
            os.remove(self.temp_storage_path)
    
    def test_string_encryption(self):
        """测试字符串加密和解密"""
        original_text = "sensitive data 123!@#"
        
        # 加密
        encrypted_text = self.encryption_service.encrypt(original_text)
        
        # 验证加密后的文本与原文不同
        self.assertNotEqual(encrypted_text, original_text)
        
        # 解密
        decrypted_text = self.encryption_service.decrypt(encrypted_text)
        
        # 验证解密后的文本与原文相同
        self.assertEqual(decrypted_text, original_text)
    
    def test_dict_encryption(self):
        """测试字典加密和解密"""
        test_data = {
            "username": "testuser",
            "email": "test@example.com",
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "api_key": "sk_test_abcdefghijklmnopqrstuvwxyz",
            "non_sensitive": "public data"
        }
        
        # 定义敏感字段
        sensitive_fields = ["email", "wallet_address", "api_key"]
        
        # 加密字典
        encrypted_data = self.encryption_service.encrypt_dict(test_data, sensitive_fields)
        
        # 验证敏感字段已加密
        for field in sensitive_fields:
            self.assertNotEqual(encrypted_data[field], test_data[field])
        
        # 验证非敏感字段未加密
        self.assertEqual(encrypted_data["username"], test_data["username"])
        self.assertEqual(encrypted_data["non_sensitive"], test_data["non_sensitive"])
        
        # 解密字典
        decrypted_data = self.encryption_service.decrypt_dict(encrypted_data, sensitive_fields)
        
        # 验证解密后的数据与原始数据相同
        for key, value in test_data.items():
            self.assertEqual(decrypted_data[key], value)
    
    def test_secure_storage(self):
        """测试安全存储功能"""
        # 存储数据
        self.secure_storage.set("api_key", "test_api_key_123")
        self.secure_storage.set("secret_token", "test_secret_token_456")
        
        # 验证文件已创建
        self.assertTrue(os.path.exists(self.temp_storage_path))
        
        # 读取存储的数据
        retrieved_api_key = self.secure_storage.get("api_key")
        retrieved_token = self.secure_storage.get("secret_token")
        
        # 验证数据正确
        self.assertEqual(retrieved_api_key, "test_api_key_123")
        self.assertEqual(retrieved_token, "test_secret_token_456")
        
        # 删除数据
        self.secure_storage.delete("api_key")
        
        # 验证数据已删除
        self.assertIsNone(self.secure_storage.get("api_key"))
        self.assertEqual(self.secure_storage.get("secret_token"), "test_secret_token_456")
        
        # 清除所有数据
        self.secure_storage.clear()
        
        # 验证所有数据已清除
        self.assertIsNone(self.secure_storage.get("secret_token"))
    
    def test_sensitive_fields_list(self):
        """测试敏感字段列表"""
        # 验证敏感字段列表包含必要的字段
        required_fields = [
            'wallet_address',
            'private_key',
            'api_key',
            'password',
            'email'
        ]
        
        for field in required_fields:
            self.assertIn(field, SENSITIVE_FIELDS)

if __name__ == "__main__":
    unittest.main()
