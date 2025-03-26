import unittest
import json
import jwt
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    ROLE_PERMISSIONS
)
from app.config import settings

class TestSecurity(unittest.TestCase):
    """测试安全模块功能"""
    
    def test_password_hashing(self):
        """测试密码哈希和验证"""
        password = "test_password123"
        hashed = get_password_hash(password)
        
        # 验证哈希格式
        self.assertIn(":", hashed)
        salt_hex, key_hex = hashed.split(":")
        self.assertEqual(len(bytes.fromhex(salt_hex)), 32)  # 盐值长度应为32字节
        
        # 验证正确密码
        self.assertTrue(verify_password(password, hashed))
        
        # 验证错误密码
        self.assertFalse(verify_password("wrong_password", hashed))
    
    def test_access_token_creation(self):
        """测试访问令牌创建"""
        username = "testuser"
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(
            data={"sub": username, "scopes": ["user"]},
            expires_delta=expires_delta
        )
        
        # 解码令牌
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 验证令牌内容
        self.assertEqual(payload["sub"], username)
        self.assertEqual(payload["scopes"], ["user"])
        
        # 验证过期时间
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + expires_delta
        self.assertAlmostEqual(exp_time.timestamp(), expected_exp.timestamp(), delta=1)
    
    def test_role_permissions(self):
        """测试角色权限映射"""
        # 验证管理员权限
        self.assertIn("admin", ROLE_PERMISSIONS["admin"])
        self.assertIn("user", ROLE_PERMISSIONS["admin"])
        self.assertIn("monitor", ROLE_PERMISSIONS["admin"])
        
        # 验证监控员权限
        self.assertIn("user", ROLE_PERMISSIONS["monitor"])
        self.assertIn("monitor", ROLE_PERMISSIONS["monitor"])
        self.assertNotIn("admin", ROLE_PERMISSIONS["monitor"])
        
        # 验证普通用户权限
        self.assertIn("user", ROLE_PERMISSIONS["user"])
        self.assertNotIn("admin", ROLE_PERMISSIONS["user"])
        self.assertNotIn("monitor", ROLE_PERMISSIONS["user"])

if __name__ == "__main__":
    unittest.main()
