import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Alert, Switch, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

const Login = () => {
  const { t, i18n } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onFinish = async (values) => {
    setLoading(true);
    setError('');
    
    const { username, password } = values;
    const result = await login(username, password);
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error || t('auth.invalidCredentials'));
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
          <Title level={2}>{t('auth.loginTitle')}</Title>
          <Text type="secondary">{t('common.welcome')}</Text>
        </div>
        
        {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 24 }} />}
        
        <Form
          name="login"
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
            name="password"
            rules={[{ required: true, message: t('auth.password') + ' ' + t('common.error') }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder={t('auth.password')} />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              {t('auth.loginButton')}
            </Button>
          </Form.Item>
          
          <div style={{ textAlign: 'center' }}>
            <Link to="/register">{t('auth.registerTitle')}</Link>
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

export default Login;
