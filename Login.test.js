import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../src/i18n';
import Login from '../src/pages/Login';
import { AuthProvider } from '../src/contexts/AuthContext';

// 模拟认证上下文
jest.mock('../src/contexts/AuthContext', () => {
  const originalModule = jest.requireActual('../src/contexts/AuthContext');
  
  return {
    ...originalModule,
    useAuth: () => ({
      login: jest.fn().mockImplementation((username, password) => {
        if (username === 'testuser' && password === 'password123') {
          return Promise.resolve({ success: true });
        } else {
          return Promise.resolve({ 
            success: false, 
            error: 'Invalid username or password' 
          });
        }
      }),
      isAuthenticated: false,
      loading: false,
      error: null
    })
  };
});

// 模拟路由导航
jest.mock('react-router-dom', () => {
  const originalModule = jest.requireActual('react-router-dom');
  
  return {
    ...originalModule,
    useNavigate: () => jest.fn()
  };
});

describe('Login Component', () => {
  beforeEach(() => {
    render(
      <BrowserRouter>
        <I18nextProvider i18n={i18n}>
          <Login />
        </I18nextProvider>
      </BrowserRouter>
    );
  });

  test('renders login form', () => {
    // 验证标题存在
    expect(screen.getByText(/login/i)).toBeInTheDocument();
    
    // 验证输入字段存在
    expect(screen.getByPlaceholderText(/username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    
    // 验证登录按钮存在
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    
    // 验证注册链接存在
    expect(screen.getByText(/register/i)).toBeInTheDocument();
  });

  test('handles form submission', async () => {
    // 填写表单
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: 'testuser' }
    });
    
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: 'password123' }
    });
    
    // 提交表单
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // 等待表单处理完成
    await waitFor(() => {
      // 验证登录函数被调用
      expect(require('../src/contexts/AuthContext').useAuth().login).toHaveBeenCalledWith(
        'testuser',
        'password123'
      );
    });
  });

  test('displays error message on failed login', async () => {
    // 填写表单（错误密码）
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: 'testuser' }
    });
    
    fireEvent.change(screen.getByPlaceholderText(/password/i), {
      target: { value: 'wrong_password' }
    });
    
    // 提交表单
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // 等待错误消息显示
    await waitFor(() => {
      expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
    });
  });

  test('toggles language', () => {
    // 获取语言切换开关
    const languageSwitch = screen.getByRole('switch');
    
    // 切换语言
    fireEvent.click(languageSwitch);
    
    // 验证语言已切换（检查中文标题）
    expect(screen.getByText(/登录/i)).toBeInTheDocument();
    
    // 再次切换回英文
    fireEvent.click(languageSwitch);
    
    // 验证语言已切换回英文
    expect(screen.getByText(/login/i)).toBeInTheDocument();
  });
});
