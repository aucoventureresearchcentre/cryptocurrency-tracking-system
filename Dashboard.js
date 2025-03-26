import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Table, Alert, Spin, Empty, Typography, Tag, Button } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, AlertOutlined, WalletOutlined, TransactionOutlined, EyeOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';

const { Title, Text } = Typography;

const Dashboard = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    stats: {
      walletCount: 0,
      transactionCount: 0,
      alertCount: 0,
      largeTransactionCount: 0
    },
    recentTransactions: [],
    recentAlerts: [],
    transactionVolume: []
  });

  // 模拟获取仪表盘数据
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // 实际项目中应该从API获取数据
        // const response = await axios.get('/api/v1/dashboard');
        // setDashboardData(response.data);
        
        // 模拟数据
        setTimeout(() => {
          setDashboardData({
            stats: {
              walletCount: 12,
              transactionCount: 156,
              alertCount: 5,
              largeTransactionCount: 3
            },
            recentTransactions: [
              {
                id: 1,
                blockchain: 'ethereum',
                tx_hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
                from_address: '0xabcdef1234567890abcdef1234567890abcdef12',
                to_address: '0x7890abcdef1234567890abcdef1234567890abcd',
                value: 2.5,
                status: 'success',
                block_timestamp: '2025-03-25T10:30:00Z',
                is_large: true
              },
              {
                id: 2,
                blockchain: 'bitcoin',
                tx_hash: 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
                from_address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                to_address: '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
                value: 0.75,
                status: 'success',
                block_timestamp: '2025-03-25T09:45:00Z',
                is_large: false
              },
              {
                id: 3,
                blockchain: 'ethereum',
                tx_hash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
                from_address: '0x1234567890abcdef1234567890abcdef12345678',
                to_address: '0xdef1234567890abcdef1234567890abcdef123456',
                value: 1.2,
                status: 'pending',
                block_timestamp: '2025-03-25T08:15:00Z',
                is_large: false
              }
            ],
            recentAlerts: [
              {
                id: 1,
                alert_type: 'large_transaction',
                severity: 'high',
                title: t('alerts.typeLargeTransaction'),
                description: '检测到大额转账: 2.5 ETH',
                status: 'new',
                created_at: '2025-03-25T10:35:00Z'
              },
              {
                id: 2,
                alert_type: 'fund_dispersion',
                severity: 'high',
                title: t('alerts.typeFundDispersion'),
                description: '检测到资金分散转出模式',
                status: 'new',
                created_at: '2025-03-25T09:20:00Z'
              },
              {
                id: 3,
                alert_type: 'ai_anomaly',
                severity: 'medium',
                title: t('alerts.typeAiAnomaly'),
                description: 'AI检测到异常交易模式',
                status: 'read',
                created_at: '2025-03-25T07:45:00Z'
              }
            ],
            transactionVolume: [
              { date: '2025-03-19', value: 3.2 },
              { date: '2025-03-20', value: 4.5 },
              { date: '2025-03-21', value: 2.8 },
              { date: '2025-03-22', value: 5.1 },
              { date: '2025-03-23', value: 6.3 },
              { date: '2025-03-24', value: 4.2 },
              { date: '2025-03-25', value: 7.5 }
            ]
          });
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError(err.message || 'Failed to fetch dashboard data');
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [t]);

  // 交易量图表选项
  const getTransactionVolumeOptions = () => {
    const { transactionVolume } = dashboardData;
    
    return {
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}'
      },
      xAxis: {
        type: 'category',
        data: transactionVolume.map(item => item.date)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: transactionVolume.map(item => item.value),
          type: 'line',
          smooth: true,
          areaStyle: {}
        }
      ],
      color: ['#1890ff']
    };
  };

  // 交易表格列
  const transactionColumns = [
    {
      title: t('transactions.blockchain'),
      dataIndex: 'blockchain',
      key: 'blockchain',
      render: (text) => text.toUpperCase()
    },
    {
      title: t('transactions.value'),
      dataIndex: 'value',
      key: 'value',
      render: (text, record) => (
        <span>
          {text} {record.blockchain === 'ethereum' ? 'ETH' : 'BTC'}
          {record.is_large && (
            <Tag color="red" style={{ marginLeft: 8 }}>
              {t('transactions.largeTransaction')}
            </Tag>
          )}
        </span>
      )
    },
    {
      title: t('transactions.status'),
      dataIndex: 'status',
      key: 'status',
      render: (text) => (
        <Tag color={text === 'success' ? 'green' : text === 'pending' ? 'orange' : 'red'}>
          {text === 'success' ? t('transactions.statusSuccess') : 
           text === 'pending' ? t('transactions.statusPending') : 
           t('transactions.statusFailed')}
        </Tag>
      )
    },
    {
      title: t('common.time'),
      dataIndex: 'block_timestamp',
      key: 'block_timestamp',
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: t('common.action'),
      key: 'action',
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />} 
          onClick={() => console.log('View transaction', record.id)}
        >
          {t('transactions.details')}
        </Button>
      )
    }
  ];

  // 警报表格列
  const alertColumns = [
    {
      title: t('alerts.alertType'),
      dataIndex: 'alert_type',
      key: 'alert_type',
      render: (text) => {
        let color = 'blue';
        let label = '';
        
        switch (text) {
          case 'large_transaction':
            color = 'red';
            label = t('alerts.typeLargeTransaction');
            break;
          case 'fund_dispersion':
            color = 'orange';
            label = t('alerts.typeFundDispersion');
            break;
          case 'ai_anomaly':
            color = 'purple';
            label = t('alerts.typeAiAnomaly');
            break;
          case 'statistical_anomaly':
            color = 'cyan';
            label = t('alerts.typeStatisticalAnomaly');
            break;
          default:
            label = text;
        }
        
        return <Tag color={color}>{label}</Tag>;
      }
    },
    {
      title: t('alerts.severity'),
      dataIndex: 'severity',
      key: 'severity',
      render: (text) => {
        const color = text === 'high' ? 'red' : text === 'medium' ? 'orange' : 'green';
        const label = text === 'high' ? t('alerts.severityHigh') : 
                     text === 'medium' ? t('alerts.severityMedium') : 
                     t('alerts.severityLow');
        
        return <Tag color={color}>{label}</Tag>;
      }
    },
    {
      title: t('alerts.description'),
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: t('common.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: t('common.action'),
      key: 'action',
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />} 
          onClick={() => console.log('View alert', record.id)}
        >
          {t('alerts.viewDetails')}
        </Button>
      )
    }
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message={t('common.error')}
        description={error}
        type="error"
        showIcon
      />
    );
  }

  return (
    <div>
      <Title level={2}>{t('dashboard.title')}</Title>
      
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={12} md={6} lg={6} xl={6}>
          <Card>
            <Statistic
              title={t('dashboard.monitoredWallets')}
              value={dashboardData.stats.walletCount}
              prefix={<WalletOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={12} md={6} lg={6} xl={6}>
          <Card>
            <Statistic
              title={t('dashboard.transactionVolume')}
              value={dashboardData.stats.transactionCount}
              prefix={<TransactionOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={12} md={6} lg={6} xl={6}>
          <Card>
            <Statistic
              title={t('dashboard.alertsToday')}
              value={dashboardData.stats.alertCount}
              prefix={<AlertOutlined />}
              valueStyle={{ color: dashboardData.stats.alertCount > 0 ? '#cf1322' : undefined }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={12} md={6} lg={6} xl={6}>
          <Card>
            <Statistic
              title={t('dashboard.largeTransactions')}
              value={dashboardData.stats.largeTransactionCount}
              prefix={<ArrowUpOutlined />}
              valueStyle={{ color: dashboardData.stats.largeTransactionCount > 0 ? '#cf1322' : undefined }}
            />
          </Card>
        </Col>
      </Row>
      
      {/* 交易量图表 */}
      <Card title={t('dashboard.transactionVolume')} style={{ marginBottom: 24 }}>
        {dashboardData.transactionVolume.length > 0 ? (
          <ReactECharts option={getTransactionVolumeOptions()} style={{ height: 300 }} />
        ) : (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>
      
      {/* 最近交易和警报 */}
      <Row gutter={16}>
        <Col xs={24} sm={24} md={12} lg={12} xl={12}>
          <Card 
            title={t('dashboard.recentTransactions')}
            extra={<Button type="link" onClick={() => console.log('View all transactions')}>{t('dashboard.viewAll')}</Button>}
            style={{ marginBottom: 24 }}
          >
            <Table 
              columns={transactionColumns} 
              dataSource={dashboardData.recentTransactions}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} sm={24} md={12} lg={12} xl={12}>
          <Card 
            title={t('dashboard.recentAlerts')}
            extra={<Button type="link" onClick={() => console.log('View all alerts')}>{t('dashboard.viewAll')}</Button>}
            style={{ marginBottom: 24 }}
          >
            <Table 
              columns={alertColumns} 
              dataSource={dashboardData.recentAlerts}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
