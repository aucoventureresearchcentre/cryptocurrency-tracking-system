import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

// 创建认证上下文
const AuthContext = createContext(null);

// 认证提供者组件
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 检查用户是否已登录
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          // 设置默认请求头
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // 验证令牌
          const response = await axios.get('/api/v1/auth/me');
          
          setCurrentUser(response.data);
          setIsAuthenticated(true);
        } catch (err) {
          // 令牌无效或过期
          localStorage.removeItem('token');
          delete axios.defaults.headers.common['Authorization'];
          setError('Session expired. Please login again.');
        }
      }
      
      setLoading(false);
    };
    
    checkAuthStatus();
  }, []);

  // 登录函数
  const login = async (username, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('/api/v1/auth/login', {
        username,
        password
      });
      
      const { token, user } = response.data;
      
      // 保存令牌到本地存储
      localStorage.setItem('token', token);
      
      // 设置默认请求头
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      setCurrentUser(user);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
      return { success: false, error: err.response?.data?.detail || 'Login failed' };
    } finally {
      setLoading(false);
    }
  };

  // 注册函数
  const register = async (username, email, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('/api/v1/auth/register', {
        username,
        email,
        password
      });
      
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      return { success: false, error: err.response?.data?.detail || 'Registration failed' };
    } finally {
      setLoading(false);
    }
  };

  // 登出函数
  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  // 更新用户信息
  const updateUserInfo = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.put('/api/v1/users/me', userData);
      
      setCurrentUser(response.data);
      
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user information');
      return { success: false, error: err.response?.data?.detail || 'Failed to update user information' };
    } finally {
      setLoading(false);
    }
  };

  // 修改密码
  const changePassword = async (currentPassword, newPassword) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('/api/v1/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to change password');
      return { success: false, error: err.response?.data?.detail || 'Failed to change password' };
    } finally {
      setLoading(false);
    }
  };

  // 提供上下文值
  const value = {
    currentUser,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    updateUserInfo,
    changePassword
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 自定义钩子，用于访问认证上下文
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};
