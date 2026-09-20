import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { formatCurrency } from '@/utils/formatters';

export interface RevenueDataPoint {
  date: string;
  actual?: number;
  forecast?: number;
  target?: number;
}

interface RevenueTrendChartProps {
  data?: RevenueDataPoint[];
  loading?: boolean;
  height?: number;
}

const defaultDemoData: RevenueDataPoint[] = [
  { date: 'Mon', actual: 4200, forecast: 4100 },
  { date: 'Tue', actual: 4800, forecast: 4600 },
  { date: 'Wed', actual: 5100, forecast: 5000 },
  { date: 'Thu', actual: 4700, forecast: 4900 },
  { date: 'Fri', actual: 6400, forecast: 6100 },
  { date: 'Sat', actual: 7800, forecast: 7500 },
  { date: 'Sun', actual: 6900, forecast: 7100 },
];

const formatDateLabel = (val: string) => {
  if (!val) return '';
  if (/^\d{4}-\d{2}-\d{2}/.test(val)) {
    const d = new Date(val);
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  }
  return val;
};

export const RevenueTrendChart: React.FC<RevenueTrendChartProps> = ({
  data = defaultDemoData,
  loading = false,
  height = 260,
}) => {
  if (loading) {
    return (
      <div
        className="w-full flex items-center justify-center bg-[#1D212A]/40 rounded-lg animate-pulse"
        style={{ height }}
      >
        <span className="text-xs font-mono text-[#5C6478]">Loading trend data...</span>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <defs>
            <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6C8CFF" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#6C8CFF" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4FAE7C" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#4FAE7C" stopOpacity={0.0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#262B35" vertical={false} />

          <XAxis
            dataKey="date"
            stroke="#5C6478"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#262B35' }}
            tickFormatter={formatDateLabel}
          />

          <YAxis
            stroke="#5C6478"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: '#171A20',
              border: '1px solid #262B35',
              borderRadius: '8px',
              fontSize: '12px',
              fontFamily: 'var(--font-mono)',
              boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            }}
            labelFormatter={formatDateLabel}
            formatter={(value: any, name: any) => [
              formatCurrency(Number(value) || 0),
              name === 'actual' ? 'Actual Revenue' : 'Forecast (XGBoost)',
            ]}
          />

          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            wrapperStyle={{ paddingBottom: '12px', fontSize: '11px', fontFamily: 'var(--font-mono)' }}
          />

          <Area
            type="monotone"
            dataKey="actual"
            name="Actual Revenue"
            stroke="#6C8CFF"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#actualGradient)"
          />

          <Area
            type="monotone"
            dataKey="forecast"
            name="Forecast (XGBoost)"
            stroke="#4FAE7C"
            strokeWidth={1.5}
            strokeDasharray="4 4"
            fillOpacity={1}
            fill="url(#forecastGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
