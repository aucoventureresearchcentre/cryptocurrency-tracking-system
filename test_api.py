import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import User
from app.security import get_password_hash

class TestAPI(unittest.TestCase):
    """测试API端点功能"""
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient(app)
        
        # 模拟数据库会话
        self.db_mock = MagicMock(spec=Session)
        
        # 模拟用户数据
        self.test_user = User(
            id=1,
            username="testuser",
            email="dGVzdEBleGFtcGxlLmNvbQ==",  # 加密的 test@example.com
            hashed_password=get_password_hash("password123"),
            role="user",
            is_active=True
        )
        
        self.test_admin = User(
            id=2,
            username="admin",
            email="YWRtaW5AZXhhbXBsZS5jb20=",  # 加密的 admin@example.com
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        
        # 修补数据库依赖
        self.db_patcher = patch("app.main.get_db")
        self.mock_get_db = self.db_patcher.start()
        self.mock_get_db.return_value = self.db_mock
    
    def tearDown(self):
        """测试后清理"""
        self.db_patcher.stop()
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get("/api/v1/health")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
    
    def test_login_success(self):
        """测试登录成功"""
        # 模拟数据库查询
        self.db_mock.query.return_value.filter.return_value.first.return_value = self.test_user
        
        # 发送登录请求
        response = self.client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "password123"}
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertEqual(response.json()["token_type"], "bearer")
    
    def test_login_failure(self):
        """测试登录失败"""
        # 模拟数据库查询
        self.db_mock.query.return_value.filter.return_value.first.return_value = self.test_user
        
        # 发送登录请求（错误密码）
        response = self.client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "wrong_password"}
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
    
    def test_register_success(self):
        """测试注册成功"""
        # 模拟数据库查询（用户不存在）
        self.db_mock.query.return_value.filter.return_value.first.return_value = None
        
        # 发送注册请求
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpassword123"
            }
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "newuser")
        self.assertEqual(response.json()["email"], "new@example.com")
        
        # 验证数据库操作
        self.db_mock.add.assert_called_once()
        self.db_mock.commit.assert_called_once()
        self.db_mock.refresh.assert_called_once()
    
    def test_register_duplicate_username(self):
        """测试注册失败（用户名已存在）"""
        # 模拟数据库查询（用户已存在）
        self.db_mock.query.return_value.filter.return_value.first.return_value = self.test_user
        
        # 发送注册请求
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "new@example.com",
                "password": "newpassword123"
            }
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
    
    def test_get_current_user(self):
        """测试获取当前用户信息"""
        # 创建访问令牌
        login_response = self.client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # 模拟数据库查询
        self.db_mock.query.return_value.filter.return_value.first.return_value = self.test_user
        
        # 发送获取用户信息请求
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "testuser")
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        # 发送获取用户信息请求（无令牌）
        response = self.client.get("/api/v1/auth/me")
        
        # 验证响应
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

if __name__ == "__main__":
    unittest.main()
