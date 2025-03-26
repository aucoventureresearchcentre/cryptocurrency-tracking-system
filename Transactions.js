import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Input, DatePicker, Select, Tag, Typography, Spin, Alert, Tooltip, Space, Badge } from 'antd';
import { SearchOutlined, FilterOutlined, EyeOutlined, CopyOutlined, LinkOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const Transactions = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [filters, setFilters] = useState({
    address: '',
    blockchain: 'all',
    dateRange: null,
    status: 'all'
  });

  // 模拟获取交易数据
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        // 实际项目中应该从API获取数据
        // const response = await axios.get('/api/v1/transactions', { params: filters });
        // setTransactions(response.data);
        
        // 模拟数据
        setTimeout(() => {
          setTransactions([
            {
              id: 1,
              blockchain: 'ethereum',
              tx_hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
              from_address: '0xabcdef1234567890abcdef1234567890abcdef12',
              to_address: '0x7890abcdef1234567890abcdef1234567890abcd',
              value: 2.5,
              fee: 0.002,
              status: 'success',
              block_number: 12345678,
              block_timestamp: '2025-03-25T10:30:00Z',
              is_large: true,
              is_suspicious: false
            },
            {
              id: 2,
              blockchain: 'bitcoin',
              tx_hash: 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
              from_address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
              to_address: '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
              value: 0.75,
              fee: 0.0005,
              status: 'success',
              block_number: 789012,
              block_timestamp: '2025-03-25T09:45:00Z',
              is_large: false,
              is_suspicious: false
            },
            {
              id: 3,
              blockchain: 'ethereum',
              tx_hash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
              from_address: '0x1234567890abcdef1234567890abcdef12345678',
              to_address: '0xdef1234567890abcdef1234567890abcdef123456',
              value: 1.2,
              fee: 0.001,
              status: 'pending',
              block_number: 12345679,
              block_timestamp: '2025-03-25T08:15:00Z',
              is_large: false,
              is_suspicious: false
            },
            {
              id: 4,
              blockchain: 'ethereum',
              tx_hash: '0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba',
              from_address: '0x5678901234567890123456789012345678901234',
              to_address: '0x0123456789012345678901234567890123456789',
              value: 0.5,
              fee: 0.0015,
              status: 'success',
              block_number: 12345680,
              block_timestamp: '2025-03-24T15:20:00Z',
              is_large: false,
              is_suspicious: true
            },
            {
              id: 5,
              blockchain: 'bitcoin',
              tx_hash: '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
              from_address: 'bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq',
              to_address: 'bc1q9h6yzs4h88qmvfp2rkgv6utzdvkyspjhxxgg66',
              value: 1.5,
              fee: 0.0008,
              status: 'failed',
              block_number: 789013,
              block_timestamp: '2025-03-24T12:10:00Z',
              is_large: false,
              is_suspicious: false
            }
          ]);
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError(err.message || 'Failed to fetch transactions');
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [filters]);

  // 处理筛选变化
  const handleFilterChange = (key, value) => {
    setFilters({
      ...filters,
      [key]: value
    });
  };

  // 复制到剪贴板
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(
      () => {
        // 显示成功消息
        // message.success('Copied to clipboard');
        console.log('Copied to clipboard:', text);
      },
      (err) => {
        console.error('Could not copy text: ', err);
      }
    );
  };

  // 在区块浏览器中查看
  const viewOnExplorer = (blockchain, hash) => {
    let url = '';
    if (blockchain === 'ethereum') {
      url = `https://etherscan.io/tx/${hash}`;
    } else if (blockchain === 'bitcoin') {
      url = `https://www.blockchain.com/btc/tx/${hash}`;
    }
    
    if (url) {
      window.open(url, '_blank');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: t('transactions.blockchain'),
      dataIndex: 'blockchain',
      key: 'blockchain',
      render: (text) => text.toUpperCase()
    },
    {
      title: t('transactions.txHash'),
      dataIndex: 'tx_hash',
      key: 'tx_hash',
      render: (text, record) => (
        <div>
          <Tooltip title={text}>
            <span>{`${text.substring(0, 8)}...${text.substring(text.length - 8)}`}</span>
          </Tooltip>
          <Button 
            type="link" 
            icon={<CopyOutlined />} 
            size="small"
            onClick={() => copyToClipboard(text)}
            style={{ marginLeft: 8 }}
          />
        </div>
      )
    },
    {
      title: t('transactions.from'),
      dataIndex: 'from_address',
      key: 'from_address',
      render: (text) => (
        <div>
          <Tooltip title={text}>
            <span>{`${text.substring(0, 8)}...${text.substring(text.length - 8)}`}</span>
          </Tooltip>
          <Button 
            type="link" 
            icon={<CopyOutlined />} 
            size="small"
            onClick={() => copyToClipboard(text)}
            style={{ marginLeft: 8 }}
          />
        </div>
      )
    },
    {
      title: t('transactions.to'),
      dataIndex: 'to_address',
      key: 'to_address',
      render: (text) => (
        <div>
          <Tooltip title={text}>
            <span>{`${text.substring(0, 8)}...${text.substring(text.length - 8)}`}</span>
          </Tooltip>
          <Button 
            type="link" 
            icon={<CopyOutlined />} 
            size="small"
            onClick={() => copyToClipboard(text)}
            style={{ marginLeft: 8 }}
          />
        </div>
      )
    },
    {
      title: t('transactions.value'),
      dataIndex: 'value',
      key: 'value',
      render: (text, record) => (
        <div>
          <span>
            {text} {record.blockchain === 'ethereum' ? 'ETH' : 'BTC'}
          </span>
          {record.is_large && (
            <Tag color="red" style={{ marginLeft: 8 }}>
              {t('transactions.largeTransaction')}
            </Tag>
          )}
          {record.is_suspicious && (
            <Tag color="orange" style={{ marginLeft: 8 }}>
              {t('transactions.suspiciousTransaction')}
            </Tag>
          )}
        </div>
      )
    },
    {
      title: t('transactions.fee'),
      dataIndex: 'fee',
      key: 'fee',
      render: (text, record) => (
        <span>{text} {record.blockchain === 'ethereum' ? 'ETH' : 'BTC'}</span>
      )
    },
    {
      title: t('transactions.status'),
      dataIndex: 'status',
      key: 'status',
      render: (text) => {
        let color = 'green';
        let label = t('transactions.statusSuccess');
        
        if (text === 'pending') {
          color = 'orange';
          label = t('transactions.statusPending');
        } else if (text === 'failed') {
          color = 'red';
          label = t('transactions.statusFailed');
        }
        
        return <Tag color={color}>{label}</Tag>;
      }
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
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => console.log('View transaction details', record.id)}
          />
          <Button 
            type="link" 
            icon={<LinkOutlined />} 
            onClick={() => viewOnExplorer(record.blockchain, record.tx_hash)}
            title={t('transactions.viewOnExplorer')}
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
      <Title level={2}>{t('transactions.title')}</Title>
      
      {/* 筛选器 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ flex: '1 1 200px' }}>
            <Text strong>{t('transactions.filterByAddress')}</Text>
            <Input
              placeholder={t('common.address')}
              prefix={<SearchOutlined />}
              value={filters.address}
              onChange={(e) => handleFilterChange('address', e.target.value)}
              style={{ marginTop: 8 }}
            />
          </div>
          
          <div style={{ flex: '1 1 200px' }}>
            <Text strong>{t('common.blockchain')}</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={filters.blockchain}
              onChange={(value) => handleFilterChange('blockchain', value)}
            >
              <Option value="all">{t('common.all')}</Option>
              <Option value="ethereum">Ethereum</Option>
              <Option value="bitcoin">Bitcoin</Option>
            </Select>
          </div>
          
          <div style={{ flex: '1 1 200px' }}>
            <Text strong>{t('transactions.filterByDate')}</Text>
            <RangePicker
              style={{ width: '100%', marginTop: 8 }}
              onChange={(dates) => handleFilterChange('dateRange', dates)}
            />
          </div>
          
          <div style={{ flex: '1 1 200px' }}>
            <Text strong>{t('common.status')}</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={filters.status}
              onChange={(value) => handleFilterChange('status', value)}
            >
              <Option value="all">{t('common.all')}</Option>
              <Option value="success">{t('transactions.statusSuccess')}</Option>
              <Option value="pending">{t('transactions.statusPending')}</Option>
              <Option value="failed">{t('transactions.statusFailed')}</Option>
            </Select>
          </div>
        </div>
      </Card>
      
      {/* 交易表格 */}
      <Card>
        <Table 
          columns={columns} 
          dataSource={transactions}
          rowKey="id"
        />
      </Card>
    </div>
  );
};

export default Transactions;
