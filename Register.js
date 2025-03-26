import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Alert, Switch, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

const Register = () => {
  const { t, i18n } = useTranslation();
  const { register } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onFinish = async (values) => {
    setLoading(true);
    setError('');
    
    // 检查密码是否匹配
    if (values.password !== values.confirmPassword) {
      setError(t('auth.passwordMismatch'));
      setLoading(false);
      return;
    }
    
    const { username, email, password } = values;
    const result = await register(username, email, password);
    
    if (result.success) {
      // 注册成功，跳转到登录页面
      navigate('/login');
    } else {
      setError(result.error || t('common.error'));
    }
    
    setLoading(false);
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(newLang);
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      background: '#f0f2f5'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 8px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>{t('auth.registerTitle')}</Title>
          <Text type="secondary">{t('common.welcome')}</Text>
        </div>
        
        {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 24 }} />}
        
        <Form
          name="register"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: t('auth.username') + ' ' + t('common.error') }]}
          >
            <Input prefix={<UserOutlined />} placeholder={t('auth.username')} />
          </Form.Item>
          
          <Form.Item
            name="email"
            rules={[
              { required: true, message: t('auth.email') + ' ' + t('common.error') },
              { type: 'email', message: t('auth.email') + ' ' + t('common.error') }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder={t('auth.email')} />
          </Form.Item>
          
          <Form.Item
            name="password"
            rules={[{ required: true, message: t('auth.password') + ' ' + t('common.error') }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t('auth.password')} />
          </Form.Item>
          
          <Form.Item
            name="confirmPassword"
            rules={[{ required: true, message: t('auth.confirmPassword') + ' ' + t('common.error') }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t('auth.confirmPassword')} />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              {t('auth.registerButton')}
            </Button>
          </Form.Item>
          
          <div style={{ textAlign: 'center' }}>
            <Link to="/login">{t('auth.loginTitle')}</Link>
          </div>
        </Form>
        
        <Divider />
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text type="secondary">{t('common.language')}</Text>
          <div>
            <Text type="secondary" style={{ marginRight: 8 }}>中文</Text>
            <Switch 
              checked={i18n.language === 'en'} 
              onChange={toggleLanguage} 
              size="small" 
            />
            <Text type="secondary" style={{ marginLeft: 8 }}>English</Text>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Register;
