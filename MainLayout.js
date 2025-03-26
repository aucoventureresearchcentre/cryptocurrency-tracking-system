import React, { useState } from 'react';
import { Layout, Menu, Button, Avatar, Dropdown, Badge, Switch, Drawer } from 'antd';
import { 
  DashboardOutlined, 
  WalletOutlined, 
  TransactionOutlined, 
  AlertOutlined, 
  AreaChartOutlined, 
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  GlobalOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate, Outlet, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const { Header, Sider, Content } = Layout;

const MainLayout = () => {
  const { t, i18n } = useTranslation();
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileDrawerVisible, setMobileDrawerVisible] = useState(false);
  const [alertsDrawerVisible, setAlertsDrawerVisible] = useState(false);

  // 响应式设计
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  React.useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleCollapsed = () => {
    setCollapsed(!collapsed);
  };

  const toggleMobileDrawer = () => {
    setMobileDrawerVisible(!mobileDrawerVisible);
  };

  const toggleAlertsDrawer = () => {
    setAlertsDrawerVisible(!alertsDrawerVisible);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(newLang);
  };

  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        <Link to="/settings">{t('settings.profile')}</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        {t('common.logout')}
      </Menu.Item>
    </Menu>
  );

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: t('common.dashboard'),
    },
    {
      key: '/wallets',
      icon: <WalletOutlined />,
      label: t('common.wallets'),
    },
    {
      key: '/transactions',
      icon: <TransactionOutlined />,
      label: t('common.transactions'),
    },
    {
      key: '/alerts',
      icon: <AlertOutlined />,
      label: t('common.alerts'),
    },
    {
      key: '/analytics',
      icon: <AreaChartOutlined />,
      label: t('common.analytics'),
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: t('common.settings'),
    },
  ];

  const sideMenu = (
    <Menu
      theme="dark"
      mode="inline"
      defaultSelectedKeys={['/']}
      selectedKeys={[window.location.pathname]}
      items={menuItems}
      onClick={({ key }) => {
        navigate(key);
        if (isMobile) {
          setMobileDrawerVisible(false);
        }
      }}
    />
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {!isMobile && (
        <Sider trigger={null} collapsible collapsed={collapsed} width={250}>
          <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '16px 0' }}>
            <h1 style={{ color: 'white', margin: 0, fontSize: collapsed ? '14px' : '18px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {collapsed ? 'CT' : t('common.welcome')}
            </h1>
          </div>
          {sideMenu}
        </Sider>
      )}
      <Layout>
        <Header style={{ padding: 0, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {isMobile ? (
              <Button 
                type="text" 
                icon={<MenuUnfoldOutlined />} 
                onClick={toggleMobileDrawer} 
                style={{ fontSize: '16px', width: 64, height: 64 }}
              />
            ) : (
              <Button 
                type="text" 
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />} 
                onClick={toggleCollapsed} 
                style={{ fontSize: '16px', width: 64, height: 64 }}
              />
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', marginRight: 16 }}>
            <div style={{ marginRight: 16 }}>
              <Switch 
                checkedChildren="EN" 
                unCheckedChildren="中" 
                checked={i18n.language === 'en'} 
                onChange={toggleLanguage} 
              />
            </div>
            <Badge count={5} onClick={toggleAlertsDrawer} style={{ cursor: 'pointer', marginRight: 16 }}>
              <Avatar icon={<BellOutlined />} style={{ backgroundColor: '#1890ff' }} />
            </Badge>
            <Dropdown overlay={userMenu} placement="bottomRight">
              <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                <Avatar icon={<UserOutlined />} />
                {!isMobile && (
                  <span style={{ marginLeft: 8 }}>{currentUser?.username || 'User'}</span>
                )}
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff', minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>

      {/* 移动端侧边栏抽屉 */}
      <Drawer
        title={t('common.welcome')}
        placement="left"
        onClose={toggleMobileDrawer}
        visible={isMobile && mobileDrawerVisible}
        bodyStyle={{ padding: 0 }}
      >
        {sideMenu}
      </Drawer>

      {/* 警报抽屉 */}
      <Drawer
        title={t('alerts.title')}
        placement="right"
        onClose={toggleAlertsDrawer}
        visible={alertsDrawerVisible}
        width={320}
      >
        <p>{t('alerts.noAlerts')}</p>
      </Drawer>
    </Layout>
  );
};

export default MainLayout;
