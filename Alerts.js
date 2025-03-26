import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Select, Tag, Typography, Spin, Alert, Space, Tabs, Badge, Modal, Descriptions } from 'antd';
import { BellOutlined, CheckCircleOutlined, EyeOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const Alerts = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [filters, setFilters] = useState({
    type: 'all',
    severity: 'all',
    status: 'all'
  });
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);

  // 模拟获取警报数据
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setLoading(true);
        // 实际项目中应该从API获取数据
        // const response = await axios.get('/api/v1/alerts', { params: filters });
        // setAlerts(response.data);
        
        // 模拟数据
        setTimeout(() => {
          setAlerts([
            {
              id: 1,
              alert_type: 'large_transaction',
              severity: 'high',
              title: '大额转账警报',
              description: '检测到大额转账: 2.5 ETH',
              related_address: '0xabcdef1234567890abcdef1234567890abcdef12',
              status: 'new',
              created_at: '2025-03-25T10:35:00Z',
              related_data: {
                transaction: {
                  blockchain: 'ethereum',
                  tx_hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
                  from_address: '0xabcdef1234567890abcdef1234567890abcdef12',
                  to_address: '0x7890abcdef1234567890abcdef1234567890abcd',
                  value: 2.5
                }
              }
            },
            {
              id: 2,
              alert_type: 'fund_dispersion',
              severity: 'high',
              title: '资金分散转出警报',
              description: '检测到资金分散转出模式',
              related_address: '0x1234567890abcdef1234567890abcdef12345678',
              status: 'new',
              created_at: '2025-03-25T09:20:00Z',
              related_data: {
                dispersion_count: 5,
                transactions: [
                  {
                    tx_hash: '0xabcd1234...',
                    value: 0.2
                  },
                  {
                    tx_hash: '0xefgh5678...',
                    value: 0.3
                  }
                ]
              }
            },
            {
              id: 3,
              alert_type: 'ai_anomaly',
              severity: 'medium',
              title: 'AI异常检测警报',
              description: 'AI检测到异常交易模式',
              related_address: '0x5678901234567890123456789012345678901234',
              status: 'read',
              created_at: '2025-03-25T07:45:00Z',
              related_data: {
                anomaly_score: 0.85,
                predicted_value: 0.1,
                actual_value: 0.5
              }
            },
            {
              id: 4,
              alert_type: 'statistical_anomaly',
              severity: 'medium',
              title: '统计异常警报',
              description: '检测到统计异常交易',
              related_address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
              status: 'resolved',
              created_at: '2025-03-24T15:30:00Z',
              resolved_at: '2025-03-24T16:45:00Z',
              related_data: {
                anomaly_score: 0.75
              }
            },
            {
              id: 5,
              alert_type: 'large_transaction',
              severity: 'high',
              title: '大额转账警报',
              description: '检测到大额转账: 1.5 BTC',
              related_address: 'bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq',
              status: 'resolved',
              created_at: '2025-03-24T12:15:00Z',
              resolved_at: '2025-03-24T14:20:00Z',
              related_data: {
                transaction: {
                  blockchain: 'bitcoin',
                  tx_hash: '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                  from_address: 'bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq',
                  to_address: 'bc1q9h6yzs4h88qmvfp2rkgv6utzdvkyspjhxxgg66',
                  value: 1.5
                }
              }
            }
          ]);
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError(err.message || 'Failed to fetch alerts');
        setLoading(false);
      }
    };

    fetchAlerts();
  }, [filters]);

  // 处理筛选变化
  const handleFilterChange = (key, value) => {
    setFilters({
      ...filters,
      [key]: value
    });
  };

  // 显示警报详情
  const showAlertDetail = (alert) => {
    setSelectedAlert(alert);
    setDetailModalVisible(true);
  };

  // 关闭警报详情模态框
  const closeDetailModal = () => {
    setDetailModalVisible(false);
  };

  // 标记警报为已读
  const markAsRead = async (alertId) => {
    try {
      // 实际项目中应该调用API
      // await axios.put(`/api/v1/alerts/${alertId}`, { status: 'read' });
      
      // 模拟更新
      const updatedAlerts = alerts.map(alert => 
        alert.id === alertId ? { ...alert, status: 'read' } : alert
      );
      setAlerts(updatedAlerts);
      console.log('Marked alert as read:', alertId);
    } catch (err) {
      setError(err.message || 'Operation failed');
    }
  };

  // 标记警报为已解决
  const markAsResolved = async (alertId) => {
    try {
      // 实际项目中应该调用API
      // await axios.put(`/api/v1/alerts/${alertId}`, { 
      //   status: 'resolved',
      //   resolved_at: new Date().toISOString()
      // });
      
      // 模拟更新
      const updatedAlerts = alerts.map(alert => 
        alert.id === alertId ? { 
          ...alert, 
          status: 'resolved',
          resolved_at: new Date().toISOString()
        } : alert
      );
      setAlerts(updatedAlerts);
      console.log('Marked alert as resolved:', alertId);
    } catch (err) {
      setError(err.message || 'Operation failed');
    }
  };

  // 删除警报
  const deleteAlert = async (alertId) => {
    try {
      // 实际项目中应该调用API
      // await axios.delete(`/api/v1/alerts/${alertId}`);
      
      // 模拟删除
      const updatedAlerts = alerts.filter(alert => alert.id !== alertId);
      setAlerts(updatedAlerts);
      console.log('Deleted alert:', alertId);
    } catch (err) {
      setError(err.message || 'Operation failed');
    }
  };

  // 表格列定义
  const columns = [
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
      title: t('alerts.title'),
      dataIndex: 'title',
      key: 'title'
    },
    {
      title: t('alerts.description'),
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: t('alerts.relatedAddress'),
      dataIndex: 'related_address',
      key: 'related_address',
      render: (text) => (
        text ? `${text.substring(0, 8)}...${text.substring(text.length - 8)}` : '-'
      )
    },
    {
      title: t('common.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      render: (text) => {
        let color = 'red';
        let label = t('alerts.statusNew');
        
        if (text === 'read') {
          color = 'blue';
          label = t('alerts.statusRead');
        } else if (text === 'resolved') {
          color = 'green';
          label = t('alerts.statusResolved');
        }
        
        return <Tag color={color}>{label}</Tag>;
      }
    },
    {
      title: t('common.action'),
      key: 'action',
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => showAlertDetail(record)}
          />
          {record.status === 'new' && (
            <Button 
              type="link" 
              icon={<BellOutlined />} 
              onClick={() => markAsRead(record.id)}
              title={t('alerts.markAsRead')}
            />
          )}
          {record.status !== 'resolved' && (
            <Button 
              type="link" 
              icon={<CheckCircleOutlined />} 
              onClick={() => markAsResolved(record.id)}
              title={t('alerts.markAsResolved')}
            />
          )}
          <Button 
            type="link" 
            danger
            icon={<ExclamationCircleOutlined />} 
            onClick={() => deleteAlert(record.id)}
            title={t('alerts.deleteAlert')}
          />
        </Space>
      )
    }
  ];

  // 获取不同状态的警报数量
  const getAlertCounts = () => {
    const newAlerts = alerts.filter(alert => alert.status === 'new').length;
    const readAlerts = alerts.filter(alert => alert.status === 'read').length;
    const resolvedAlerts = alerts.filter(alert => alert.status === 'resolved').length;
    
    return { newAlerts, readAlerts, resolvedAlerts };
  };

  const { newAlerts, readAlerts, resolvedAlerts } = getAlertCounts();

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
      <Title level={2}>{t('alerts.title')}</Title>
      
      {/* 筛选器 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ flex: '1 1 200px' }}>
            <Text strong>{t('alerts.filterByType')}</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={filters.type}
              onChange={(value) => handleFilterChange('type', value)}
            >
              <Option value="all">{t('common.all')}</Option>
              <Option value="large_transaction">{t('alerts.typeLargeTransaction')}</Option>
              <Option value="fund_dispersion">{t('alerts.typeFundDispersion')}</Option>
              <Option value="ai_anomaly">{t('alerts.typeAiAnomaly')}</Option>
              <Option value="statistical_anomaly">{t('alerts.typeStatisticalAnomaly')}</Option>
            </Select>
          </div>
          
          <div style={{ flex: '1 1 200px' }}>
            <Text strong>{t('alerts.filterBySeverity')}</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={filters.severity}
              onChange={(value) => handleFilterChange('severity', value)}
            >
              <Option value="all">{t('common.all')}</Option>
              <Option value="high">{t('alerts.severityHigh')}</Option>
              <Option value="medium">{t('alerts.severityMedium')}</Option>
              <Option value="low">{t('alerts.severityLow')}</Option>
            </Select>
          </div>
          
          <div style={{ flex: '1 1 200px' }}>
            <Text strong>{t('alerts.filterByStatus')}</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={filters.status}
              onChange={(value) => handleFilterChange('status', value)}
            >
              <Option value="all">{t('common.all')}</Option>
              <Option value="new">{t('alerts.statusNew')}</Option>
              <Option value="read">{t('alerts.statusRead')}</Option>
              <Option value="resolved">{t('alerts.statusResolved')}</Option>
            </Select>
          </div>
        </div>
      </Card>
      
      {/* 警报标签页 */}
      <Card>
        <Tabs defaultActiveKey="all">
          <TabPane 
            tab={
              <span>
                {t('common.all')}
                <Badge count={alerts.length} style={{ marginLeft: 8 }} />
              </span>
            } 
            key="all"
          >
            <Table 
              columns={columns} 
              dataSource={alerts}
              rowKey="id"
            />
          </TabPane>
          <TabPane 
            tab={
              <span>
                {t('alerts.statusNew')}
                <Badge count={newAlerts} style={{ marginLeft: 8, backgroundColor: '#f5222d' }} />
              </span>
            } 
            key="new"
          >
            <Table 
              columns={columns} 
              dataSource={alerts.filter(alert => alert.status === 'new')}
              rowKey="id"
            />
          </TabPane>
          <TabPane 
            tab={
              <span>
                {t('alerts.statusRead')}
                <Badge count={readAlerts} style={{ marginLeft: 8, backgroundColor: '#1890ff' }} />
              </span>
            } 
            key="read"
          >
            <Table 
              columns={columns} 
              dataSource={alerts.filter(alert => alert.status === 'read')}
              rowKey="id"
            />
          </TabPane>
          <TabPane 
            tab={
              <span>
                {t('alerts.statusResolved')}
                <Badge count={resolvedAlerts} style={{ marginLeft: 8, backgroundColor: '#52c41a' }} />
              </span>
            } 
            key="resolved"
          >
            <Table 
              columns={columns} 
              dataSource={alerts.filter(alert => alert.status === 'resolved')}
              rowKey="id"
            />
          </TabPane>
        </Tabs>
      </Card>
      
      {/* 警报详情模态框 */}
      <Modal
        title={selectedAlert?.title || t('alerts.viewDetails')}
        visible={detailModalVisible}
        onCancel={closeDetailModal}
        footer={[
          <Button key="close" onClick={closeDetailModal}>
            {t('common.close')}
          </Button>
        ]}
        width={700}
      >
        {selectedAlert && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label={t('alerts.alertType')}>
              {(() => {
                let label = '';
                switch (selectedAlert.alert_type) {
                  case 'large_transaction':
                    label = t('alerts.typeLargeTransaction');
                    break;
                  case 'fund_dispersion':
                    label = t('alerts.typeFundDispersion');
                    break;
                  case 'ai_anomaly':
                    label = t('alerts.typeAiAnomaly');<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>