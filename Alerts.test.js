import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../src/i18n';
import Alerts from '../src/pages/Alerts';

// 模拟数据
const mockAlerts = [
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
  }
];

// 模拟API调用
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: mockAlerts }))
}));

describe('Alerts Component', () => {
  beforeEach(() => {
    // 渲染组件
    render(
      <BrowserRouter>
        <I18nextProvider i18n={i18n}>
          <Alerts />
        </I18nextProvider>
      </BrowserRouter>
    );
  });

  test('renders alerts title', () => {
    // 验证标题存在
    expect(screen.getByText(/alerts/i)).toBeInTheDocument();
  });

  test('renders filter options', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证筛选选项存在
      expect(screen.getByText(/filter by type/i)).toBeInTheDocument();
      expect(screen.getByText(/filter by severity/i)).toBeInTheDocument();
      expect(screen.getByText(/filter by status/i)).toBeInTheDocument();
    });
  });

  test('renders alert tabs', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证标签页存在
      expect(screen.getByText(/all/i)).toBeInTheDocument();
      expect(screen.getByText(/new/i)).toBeInTheDocument();
      expect(screen.getByText(/read/i)).toBeInTheDocument();
      expect(screen.getByText(/resolved/i)).toBeInTheDocument();
    });
  });

  test('renders alerts table with correct columns', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证表格列标题存在
      expect(screen.getByText(/alert type/i)).toBeInTheDocument();
      expect(screen.getByText(/severity/i)).toBeInTheDocument();
      expect(screen.getByText(/title/i)).toBeInTheDocument();
      expect(screen.getByText(/description/i)).toBeInTheDocument();
      expect(screen.getByText(/related address/i)).toBeInTheDocument();
      expect(screen.getByText(/time/i)).toBeInTheDocument();
      expect(screen.getByText(/status/i)).toBeInTheDocument();
      expect(screen.getByText(/action/i)).toBeInTheDocument();
    });
  });

  test('displays large transaction alerts', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证大额转账警报存在
      expect(screen.getByText(/大额转账警报/i)).toBeInTheDocument();
      expect(screen.getByText(/检测到大额转账: 2.5 ETH/i)).toBeInTheDocument();
    });
  });

  test('displays fund dispersion alerts', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证资金分散转出警报存在
      expect(screen.getByText(/资金分散转出警报/i)).toBeInTheDocument();
      expect(screen.getByText(/检测到资金分散转出模式/i)).toBeInTheDocument();
    });
  });

  test('shows alert details when clicking view button', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 点击查看按钮
      const viewButtons = screen.getAllByRole('button', { name: '' });
      fireEvent.click(viewButtons[0]);
      
      // 验证详情模态框显示
      expect(screen.getByText(/大额转账警报/i)).toBeInTheDocument();
      expect(screen.getByText(/related address/i)).toBeInTheDocument();
      expect(screen.getByText(/0xabcdef1234567890abcdef1234567890abcdef12/i)).toBeInTheDocument();
    });
  });
});
