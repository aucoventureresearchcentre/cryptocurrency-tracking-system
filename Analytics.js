import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Select, Typography, Spin, Alert, Tabs, Row, Col, Statistic, Descriptions, List, Tag, Divider } from 'antd';
import { SearchOutlined, AreaChartOutlined, NodeIndexOutlined, RiseOutlined, FallOutlined, WarningOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const Analytics = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [address, setAddress] = useState('');
  const [blockchain, setBlockchain] = useState('ethereum');
  const [analysisData, setAnalysisData] = useState(null);

  // 执行地址分析
  const analyzeAddress = async () => {
    if (!address) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // 实际项目中应该从API获取数据
      // const response = await axios.get(`/api/v1/analytics/address/${blockchain}/${address}`);
      // setAnalysisData(response.data);
      
      // 模拟数据
      setTimeout(() => {
        setAnalysisData({
          address: address,
          blockchain: blockchain,
          balance: blockchain === 'ethereum' ? 5.23 : 0.75,
          total_received: blockchain === 'ethereum' ? 15.45 : 2.5,
          total_sent: blockchain === 'ethereum' ? 10.22 : 1.75,
          transaction_count: blockchain === 'ethereum' ? 42 : 12,
          first_seen: '2024-11-15T10:30:00Z',
          last_seen: '2025-03-25T09:45:00Z',
          risk_score: 0.35,
          risk_factors: [
            '多次大额交易',
            '与高风险地址有交互'
          ],
          tags: ['Exchange', 'Whale'],
          related_addresses: [
            {
              address: blockchain === 'ethereum' ? '0x7890abcdef1234567890abcdef1234567890abcd' : '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
              relationship: 'frequent_counterparty',
              transaction_count: 15,
              last_transaction: '2025-03-20T14:25:00Z'
            },
            {
              address: blockchain === 'ethereum' ? '0xdef1234567890abcdef1234567890abcdef123456' : 'bc1q9h6yzs4h88qmvfp2rkgv6utzdvkyspjhxxgg66',
              relationship: 'possible_owner',
              transaction_count: 8,
              last_transaction: '2025-03-18T09:10:00Z'
            }
          ],
          transactions: [
            {
              tx_hash: blockchain === 'ethereum' ? '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef' : 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
              from_address: address,
              to_address: blockchain === 'ethereum' ? '0x7890abcdef1234567890abcdef1234567890abcd' : '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
              value: blockchain === 'ethereum' ? 2.5 : 0.5,
              timestamp: '2025-03-25T10:30:00Z',
              is_large: true
            },
            {
              tx_hash: blockchain === 'ethereum' ? '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890' : '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
              from_address: blockchain === 'ethereum' ? '0xdef1234567890abcdef1234567890abcdef123456' : 'bc1q9h6yzs4h88qmvfp2rkgv6utzdvkyspjhxxgg66',
              to_address: address,
              value: blockchain === 'ethereum' ? 1.2 : 0.25,
              timestamp: '2025-03-23T08:15:00Z',
              is_large: false
            }
          ],
          time_distribution: [
            { hour: 0, count: 2 },
            { hour: 1, count: 0 },
            { hour: 2, count: 1 },
            { hour: 3, count: 0 },
            { hour: 4, count: 0 },
            { hour: 5, count: 0 },
            { hour: 6, count: 0 },
            { hour: 7, count: 0 },
            { hour: 8, count: 3 },
            { hour: 9, count: 5 },
            { hour: 10, count: 7 },
            { hour: 11, count: 4 },
            { hour: 12, count: 3 },
            { hour: 13, count: 2 },
            { hour: 14, count: 4 },
            { hour: 15, count: 3 },
            { hour: 16, count: 2 },
            { hour: 17, count: 1 },
            { hour: 18, count: 0 },
            { hour: 19, count: 1 },
            { hour: 20, count: 2 },
            { hour: 21, count: 1 },
            { hour: 22, count: 0 },
            { hour: 23, count: 1 }
          ],
          value_distribution: [
            { range: '0-0.1', count: 15 },
            { range: '0.1-0.5', count: 12 },
            { range: '0.5-1.0', count: 8 },
            { range: '1.0-2.0', count: 5 },
            { range: '2.0+', count: 2 }
          ],
          flow_data: {
            nodes: [
              { id: 'center', name: address.substring(0, 8) + '...', value: blockchain === 'ethereum' ? 5.23 : 0.75 },
              { id: 'in1', name: 'Input 1', value: blockchain === 'ethereum' ? 3.5 : 0.6 },
              { id: 'in2', name: 'Input 2', value: blockchain === 'ethereum' ? 2.1 : 0.4 },
              { id: 'out1', name: 'Output 1', value: blockchain === 'ethereum' ? 4.2 : 0.8 },
              { id: 'out2', name: 'Output 2', value: blockchain === 'ethereum' ? 1.5 : 0.3 },
              { id: 'out3', name: 'Output 3', value: blockchain === 'ethereum' ? 0.8 : 0.15 }
            ],
            links: [
              { source: 'in1', target: 'center', value: blockchain === 'ethereum' ? 3.5 : 0.6 },
              { source: 'in2', target: 'center', value: blockchain === 'ethereum' ? 2.1 : 0.4 },
              { source: 'center', target: 'out1', value: blockchain === 'ethereum' ? 4.2 : 0.8 },
              { source: 'center', target: 'out2', value: blockchain === 'ethereum' ? 1.5 : 0.3 },
              { source: 'center', target: 'out3', value: blockchain === 'ethereum' ? 0.8 : 0.15 }
            ]
          }
        });
        setLoading(false);
      }, 1500);
    } catch (err) {
      setError(err.message || 'Analysis failed');
      setLoading(false);
    }
  };

  // 时间分布图表选项
  const getTimeDistributionOptions = () => {
    if (!analysisData || !analysisData.time_distribution) return {};
    
    return {
      title: {
        text: t('analytics.timeDistribution'),
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}'
      },
      xAxis: {
        type: 'category',
        data: analysisData.time_distribution.map(item => `${item.hour}:00`)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: analysisData.time_distribution.map(item => item.count),
          type: 'bar'
        }
      ],
      color: ['#1890ff']
    };
  };

  // 金额分布图表选项
  const getValueDistributionOptions = () => {
    if (!analysisData || !analysisData.value_distribution) return {};
    
    return {
      title: {
        text: t('analytics.valueDistribution'),
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      series: [
        {
          type: 'pie',
          radius: '60%',
          data: analysisData.value_distribution.map(item => ({
            name: item.range,
            value: item.count
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
  };

  // 资金流向图表选项
  const getFlowChartOptions = () => {
    if (!analysisData || !analysisData.flow_data) return {};
    
    return {
      title: {
        text: t('analytics.flowVisualization'),
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}'
      },
      series: [
        {
          type: 'sankey',
          layout: 'none',
          emphasis: {
            focus: 'adjacency'
          },
          data: analysisData.flow_data.nodes,
          links: analysisData.flow_data.links
        }
      ]
    };
  };

  return (
    <div>
      <Title level={2}>{t('analytics.title')}</Title>
      
      {/* 地址分析搜索 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'flex-end' }}>
          <div style={{ flex: '1 1 300px' }}>
            <Text strong>{t('analytics.enterAddress')}</Text>
            <Input
              placeholder={t('common.address')}
              prefix={<SearchOutlined />}
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              style={{ marginTop: 8 }}
            />
          </div>
          
          <div style={{ flex: '0 1 200px' }}>
            <Text strong>{t('common.blockchain')}</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={blockchain}
              onChange={(value) => setBlockchain(value)}
            >
              <Option value="ethereum">Ethereum</Option>
              <Option value="bitcoin">Bitcoin</Option>
            </Select>
          </div>
          
          <div>
            <Button 
              type="primary" 
              onClick={analyzeAddress} 
              loading={loading}
              disabled={!address}
            >
              {t('analytics.analyzeButton')}
            </Button>
          </div>
        </div>
      </Card>
      
      {/* 加载中 */}
      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
          <Spin size="large" tip={t('analytics.loadingAnalysis')} />
        </div>
      )}
      
      {/* 错误信息 */}
      {error && (
        <Alert
          message={t('common.error')}
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      {/* 分析结果 */}
      {!loading && !error && analysisData && (
        <div>
          {/* 基本信息和统计 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col xs={24} sm={24} md={12} lg={8} xl={8}>
              <Card>
                <Statistic
                  title={t('analytics.currentBalance')}
                  value={analysisData.balance}
                  precision={4}
                  suffix={analysisData.blockchain === 'ethereum' ? 'ETH' : 'BTC'}
                  valueStyle={{ color: '#3f8600' }}
                  prefix={<RiseOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={24} md={12} lg={8} xl={8}>
              <Card>
                <Statistic
                  title={t('analytics.transactionCount')}
                  value={analysisData.transaction_count}
                  valueStyle={{ color: '#1890ff' }}
                  prefix={<AreaChartOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={24} md={12} lg={8} xl={8}>
              <Card>
                <Statistic
                  title={t('analytics.riskAssessment')}
                  value={`${(analysisData.risk_score * 100).toFixed(0)}%`}
                  valueStyle={{ 
                    color: analysisData.risk_score > 0.7 ? '#cf1322' : 
                           analysisData.risk_score > 0.4 ? '#faad14' : '#3f8600' 
                  }}
                  prefix={<WarningOutlined />}
                />
              </Card>
            </Col>
          </Row>
          
          {/* 详细信息 */}
          <Card title={t('analytics.addressAnalysis')} style={{ marginBottom: 16 }}>
            <Descriptions bordered column={{ xxl: 4, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }}>
              <Descriptions.Item label={t('common.address')}>
                {analysisData.address}
              </Descriptions.Item>
              <Descriptions.Item label={t('common.blockchain')}>
                {analysisData.blockchain.toUpperCase()}
              </Descriptions.Item>
              <Descriptions.Item label={t('analytics.totalReceived')}>
                {analysisData.total_received} {analysisData.blockchain === 'ethereum' ? 'ETH' : 'BTC'}
              </Descriptions.Item>
              <Descriptions.Item label={t('analytics.totalSent')}>
                {analysisData.total_sent} {analysisData.blockchain === 'ethereum' ? 'ETH' : 'BTC'}
              </Descriptions.Item>
              <Descriptions.Item label={t('analytics.firstSeen')}>
                {new Date(analysisData.first_seen).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label={t('analytics.lastSeen')}>
                {new Date(analysisData.last_seen).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label={t('analytics.riskFactors')} span={2}>
                {analysisData.risk_factors.length > 0 ? (
                  <ul>
                    {analysisData.risk_factors.map((factor, index) => (
                      <li key={index}>{factor}</li>
                    ))}
                  </ul>
                ) : (
                  t('common.noData')
                )}
              </Descriptions.Item>
              <Descriptions.Item label={t('common.tags')}>
                {analysisData.tags.map(tag => (
                  <Tag key={tag} color="blue" style={{ margin: '0 4px 4px 0' }}>{tag}</Tag>
                ))}
              </Descriptions.Item>
            </Descriptions>
          </Card>
          
          {/* 图表分析 */}
          <Tabs defaultActiveKey="flow" style={{ marginBottom: 16 }}>
            <TabPane 
              tab={<span><NodeIndexOutlined /> {t('analytics.flowAnalysis')}</span>} 
              key="flow"
            >
              <Card>
                <ReactECharts option={getFlowChartOptions()} style={{ height: 400 }} />
              </Card>
            </TabPane>
            <TabPane 
              tab={<span><AreaChartOutlined /> {t('analytics.timeDistribution')}</span>} 
              key="time"
            >
              <Card>
                <ReactECharts option={getTimeDistributionOptions()} style={{ height: 400 }} />
              </Card>
            </TabPane>
            <TabPane 
              tab={<span><AreaChartOutlined /> {t('analytics.valueDistribution')}</span>} 
              key="value"
            >
              <Card>
                <ReactECharts option={getValueDistributionOptions()} style={{ height: 400 }} />
              </Card>
            </TabPane>
          </Tabs>
          
          {/* 相关地址 */}
          <Card title={t('analytics.relatedAddresses')} style={{ marginBottom: 16 }}>
            <List
              itemLayout="horizontal"
              dataSource={analysisData.related_addresses}
              renderItem={item => (
                <List.Item
                  actions={[
                    <Button 
                      type="link" 
                      onClick={() => {
                        setAddress(item.address);
                        analyzeAddress();
                      }}
                    >
                      {t('analytics.analyzeButton')}
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <div>
                        {item.address.substring(0, 8)}...{item.address.substring(item.address.length - 8)}
                        <Tag color="blue" style={{ marginLeft: 8 }}>{item.relationship}</Tag>
                      </div>
                    }
                    description={`${t('analytics.transactionCount')}: ${item.transaction_count}, ${t('analytics.lastSeen')}: ${new Date(item.last_transaction).toLocaleString()}`}
                  />
                </List.Item>
              )}
            />
          </Card>
          
          {/* 最近交易 */}
          <Card title={t('transactions.title')}>
            <List
              i<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>