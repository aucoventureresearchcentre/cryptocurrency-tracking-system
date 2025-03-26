import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../src/i18n';
import Dashboard from '../src/pages/Dashboard';

// 模拟图表组件
jest.mock('echarts-for-react', () => {
  return function MockECharts(props) {
    return <div data-testid="mock-chart" />;
  };
});

describe('Dashboard Component', () => {
  beforeEach(() => {
    // 渲染组件
    render(
      <BrowserRouter>
        <I18nextProvider i18n={i18n}>
          <Dashboard />
        </I18nextProvider>
      </BrowserRouter>
    );
  });

  test('renders dashboard title', () => {
    // 验证标题存在
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
  });

  test('renders statistics cards', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证统计卡片存在
      expect(screen.getByText(/monitored wallets/i)).toBeInTheDocument();
      expect(screen.getByText(/transaction volume/i)).toBeInTheDocument();
      expect(screen.getByText(/alerts today/i)).toBeInTheDocument();
      expect(screen.getByText(/large transactions/i)).toBeInTheDocument();
    });
  });

  test('renders transaction chart', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证图表存在
      expect(screen.getByTestId('mock-chart')).toBeInTheDocument();
    });
  });

  test('renders recent transactions table', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证交易表格存在
      expect(screen.getByText(/recent transactions/i)).toBeInTheDocument();
      
      // 验证表格列标题存在
      expect(screen.getByText(/blockchain/i)).toBeInTheDocument();
      expect(screen.getByText(/value/i)).toBeInTheDocument();
      expect(screen.getByText(/status/i)).toBeInTheDocument();
      expect(screen.getByText(/time/i)).toBeInTheDocument();
      
      // 验证"查看全部"按钮存在
      expect(screen.getByText(/view all/i)).toBeInTheDocument();
    });
  });

  test('renders recent alerts table', async () => {
    // 等待加载完成
    await waitFor(() => {
      // 验证警报表格存在
      expect(screen.getByText(/recent alerts/i)).toBeInTheDocument();
      
      // 验证表格列标题存在
      expect(screen.getByText(/alert type/i)).toBeInTheDocument();
      expect(screen.getByText(/severity/i)).toBeInTheDocument();
      expect(screen.getByText(/description/i)).toBeInTheDocument();
      
      // 验证"查看全部"按钮存在
      expect(screen.getByText(/view all/i)).toBeInTheDocument();
    });
  });

  test('displays loading state initially', () => {
    // 重新渲染组件以观察初始加载状态
    render(
      <BrowserRouter>
        <I18nextProvider i18n={i18n}>
          <Dashboard />
        </I18nextProvider>
      </BrowserRouter>
    );
    
    // 验证加载指示器存在
    expect(screen.getByRole('img', { name: /loading/i })).toBeInTheDocument();
  });
});
