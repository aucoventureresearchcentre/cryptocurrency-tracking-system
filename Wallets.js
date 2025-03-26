import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Modal, Form, Input, Select, Switch, Tag, Typography, Spin, Alert, Tooltip, Space, InputNumber } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ExclamationCircleOutlined, EyeOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;
const { confirm } = Modal;

const Wallets = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wallets, setWallets] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [editingWallet, setEditingWallet] = useState(null);
  const [form] = Form.useForm();

  // 模拟获取钱包数据
  useEffect(() => {
    const fetchWallets = async () => {
      try {
        setLoading(true);
        // 实际项目中应该从API获取数据
        // const response = await axios.get('/api/v1/wallets');
        // setWallets(response.data);
        
        // 模拟数据
        setTimeout(() => {
          setWallets([
            {
              id: 1,
              wallet_address: '0x1234567890abcdef1234567890abcdef12345678',
              blockchain: 'ethereum',
              label: '主要以太坊钱包',
              threshold: 1.0,
              alert_enabled: true,
              balance: 5.23,
              transaction_count: 42,
              last_activity: '2025-03-24T15:30:00Z',
              risk_score: 0.2
            },
            {
              id: 2,
              wallet_address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
              blockchain: 'bitcoin',
              label: '比特币储蓄',
              threshold: 0.5,
              alert_enabled: true,
              balance: 0.75,
              transaction_count: 12,
              last_activity: '2025-03-23T10:15:00Z',
              risk_score: 0.1
            },
            {
              id: 3,
              wallet_address: '0xabcdef1234567890abcdef1234567890abcdef12',
              blockchain: 'ethereum',
              label: '交易钱包',
              threshold: 2.0,
              alert_enabled: false,
              balance: 1.45,
              transaction_count: 87,
              last_activity: '2025-03-25T09:45:00Z',
              risk_score: 0.6
            }
          ]);
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError(err.message || 'Failed to fetch wallets');
        setLoading(false);
      }
    };

    fetchWallets();
  }, []);

  // 打开添加钱包模态框
  const showAddModal = () => {
    setModalTitle(t('wallets.addWallet'));
    setEditingWallet(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 打开编辑钱包模态框
  const showEditModal = (wallet) => {
    setModalTitle(t('wallets.editWallet'));
    setEditingWallet(wallet);
    form.setFieldsValue({
      wallet_address: wallet.wallet_address,
      blockchain: wallet.blockchain,
      label: wallet.label,
      threshold: wallet.threshold,
      alert_enabled: wallet.alert_enabled
    });
    setModalVisible(true);
  };

  // 关闭模态框
  const handleCancel = () => {
    setModalVisible(false);
  };

  // 提交表单
  const handleSubmit = async (values) => {
    try {
      if (editingWallet) {
        // 编辑现有钱包
        // 实际项目中应该调用API
        // await axios.put(`/api/v1/wallets/${editingWallet.id}`, values);
        
        // 模拟更新
        const updatedWallets = wallets.map(wallet => 
          wallet.id === editingWallet.id ? { ...wallet, ...values } : wallet
        );
        setWallets(updatedWallets);
        console.log('Updated wallet:', { ...editingWallet, ...values });
      } else {
        // 添加新钱包
        // 实际项目中应该调用API
        // const response = await axios.post('/api/v1/wallets', values);
        // const newWallet = response.data;
        
        // 模拟添加
        const newWallet = {
          id: wallets.length + 1,
          ...values,
          balance: 0,
          transaction_count: 0,
          last_activity: new Date().toISOString(),
          risk_score: 0
        };
        setWallets([...wallets, newWallet]);
        console.log('Added wallet:', newWallet);
      }
      
      setModalVisible(false);
      // 显示成功消息
      // message.success(editingWallet ? t('wallets.editSuccess') : t('wallets.addSuccess'));
    } catch (err) {
      setError(err.message || 'Operation failed');
      // message.error(err.message || 'Operation failed');
    }
  };

  // 删除钱包确认
  const showDeleteConfirm = (wallet) => {
    confirm({
      title: t('wallets.deleteWallet'),
      icon: <ExclamationCircleOutlined />,
      content: t('wallets.deleteConfirm'),
      okText: t('common.confirm'),
      okType: 'danger',
      cancelText: t('common.cancel'),
      onOk: async () => {
        try {
          // 实际项目中应该调用API
          // await axios.delete(`/api/v1/wallets/${wallet.id}`);
          
          // 模拟删除
          const updatedWallets = wallets.filter(w => w.id !== wallet.id);
          setWallets(updatedWallets);
          console.log('Deleted wallet:', wallet);
          
          // 显示成功消息
          // message.success(t('wallets.deleteSuccess'));
        } catch (err) {
          setError(err.message || 'Delete failed');
          // message.error(err.message || 'Delete failed');
        }
      }
    });
  };

  // 表格列定义
  const columns = [
    {
      title: t('wallets.walletLabel'),
      dataIndex: 'label',
      key: 'label',
      render: (text, record) => (
        <div>
          <div>{text}</div>
          <Text type="secondary" style={{ fontSize: '12px' }}>{record.blockchain.toUpperCase()}</Text>
        </div>
      )
    },
    {
      title: t('wallets.walletAddress'),
      dataIndex: 'wallet_address',
      key: 'wallet_address',
      render: (text) => (
        <Tooltip title={text}>
          <span>{`${text.substring(0, 8)}...${text.substring(text.length - 8)}`}</span>
        </Tooltip>
      )
    },
    {
      title: t('wallets.balance'),
      dataIndex: 'balance',
      key: 'balance',
      render: (text, record) => (
        <span>{text} {record.blockchain === 'ethereum' ? 'ETH' : 'BTC'}</span>
      )
    },
    {
      title: t('wallets.alertThreshold'),
      dataIndex: 'threshold',
      key: 'threshold',
      render: (text, record) => (
        <span>
          {text} {record.blockchain === 'ethereum' ? 'ETH' : 'BTC'}
          {!record.alert_enabled && (
            <Tag color="red" style={{ marginLeft: 8 }}>
              {t('common.disabled')}
            </Tag>
          )}
        </span>
      )
    },
    {
      title: t('wallets.transactions'),
      dataIndex: 'transaction_count',
      key: 'transaction_count'
    },
    {
      title: t('wallets.lastActivity'),
      dataIndex: 'last_activity',
      key: 'last_activity',
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: t('wallets.riskScore'),
      dataIndex: 'risk_score',
      key: 'risk_score',
      render: (score) => {
        let color = 'green';
        if (score > 0.7) color = 'red';
        else if (score > 0.4) color = 'orange';
        
        return (
          <Tag color={color}>
            {(score * 100).toFixed(0)}%
          </Tag>
        );
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
            onClick={() => console.log('View wallet details', record.id)}
          />
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => showEditModal(record)}
          />
          <Button 
            type="link" 
            danger
            icon={<DeleteOutlined />} 
            onClick={() => showDeleteConfirm(record)}
          />
        </Space>
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2}>{t('wallets.title')}</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={showAddModal}>
          {t('wallets.addWallet')}
        </Button>
      </div>
      
      <Card>
        <Table 
          columns={columns} 
          dataSource={wallets}
          rowKey="id"
        />
      </Card>
      
      {/* 添加/编辑钱包模态框 */}
      <Modal
        title={modalTitle}
        visible={modalVisible}
        onCancel={handleCancel}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="wallet_address"
            label={t('wallets.walletAddress')}
            rules={[
              { required: true, message: t('wallets.walletAddress') + ' ' + t('common.error') },
              { 
                validator: (_, value) => {
                  // 简单的地址验证，实际项目中应该有更复杂的验证
                  if (value && value.length >= 26) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error(t('wallets.invalidAddress')));
                }
              }
            ]}
          >
            <Input disabled={!!editingWallet} />
          </Form.Item>
          
          <Form.Item
            name="blockchain"
            label={t('wallets.walletType')}
            rules={[{ required: true, message: t('wallets.walletType') + ' ' + t('common.error') }]}
          >
            <Select disabled={!!editingWallet}>
              <Option value="ethereum">Ethereum (ETH)</Option>
              <Option value="bitcoin">Bitcoin (BTC)</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="label"
            label={t('wallets.walletLabel')}
            rules={[{ required: true, message: t('wallets.walletLabel') + ' ' + t('common.error') }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="threshold"
            label={t('wallets.alertThreshold')}
            rules={[{ required: true, message: t('wallets.alertThreshold') + ' ' + t('common.error') }]}
          >
            <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
          </Form.Item>
          
          <Form.Item
            name="alert_enabled"
            label={t('wallets.enableAlerts')}
            valuePropName="checked"
            initialValue={true}
          >
            <Switch />
          </Form.Item>
          
          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button style={{ marginRight: 8 }} onClick={handleCancel}>
                {t('common.cancel')}
              </Button>
              <Button type="primary" htmlType="submit">
                {t('common.save')}
              </Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Wallets;
