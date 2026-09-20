import React, { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, CartesianGrid, PieChart, Pie, Legend,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import type { CampaignAnalyticsDTO, MarketingDashboardDTO } from '@/types';

const COLORS = {
  roi: '#4FAE7C',
  budget: '#6C8CFF',
  revenue: '#E8A33D',
  grid: '#262B35',
  text: '#8A93A6',
};

const TYPE_PALETTE = ['#6C8CFF', '#4FAE7C', '#E8A33D', '#D0555A', '#B17AFF', '#22D3EE'];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1D212A] border border-[#262B35] rounded-lg p-3 text-xs shadow-xl">
      <p className="font-semibold text-[#EDEFF3] mb-1.5">{label}</p>
      {payload.map((entry: any) => (
        <p key={entry.dataKey} style={{ color: entry.color }}>
          {entry.name}: <span className="font-mono font-bold">{entry.value}</span>
        </p>
      ))}
    </div>
  );
};

// ---- ROI Ranking Chart ----
interface ROIRankingChartProps {
  campaigns: CampaignAnalyticsDTO[];
}

export const ROIRankingChart: React.FC<ROIRankingChartProps> = ({ campaigns }) => {
  const data = useMemo(() =>
    [...campaigns]
      .sort((a, b) => parseFloat(b.roi_percentage) - parseFloat(a.roi_percentage))
      .slice(0, 8)
      .map((c) => ({
        name: c.campaign_name.substring(0, 16),
        roi: parseFloat(c.roi_percentage),
        fill: parseFloat(c.roi_percentage) >= 100 ? COLORS.roi : parseFloat(c.roi_percentage) >= 0 ? COLORS.budget : '#D0555A',
      })), [campaigns]);

  if (!data.length) return (
    <Card><CardContent className="p-8 text-center text-sm text-[#5C6478]">Data not available</CardContent></Card>
  );

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Campaign ROI Ranking</CardTitle>
        <span className="text-xs text-[#5C6478]">Return on spend %</span>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} layout="vertical" barSize={14}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} horizontal={false} />
            <XAxis type="number" tick={{ fill: COLORS.text, fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
            <YAxis type="category" dataKey="name" tick={{ fill: COLORS.text, fontSize: 10 }} axisLine={false} tickLine={false} width={90} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(108,140,255,0.05)' }} />
            <Bar dataKey="roi" name="ROI %" radius={[0, 4, 4, 0]}>
              {data.map((entry, i) => <Cell key={`cell-${i}`} fill={entry.fill} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// ---- Campaign Type Pie ----
interface CampaignTypePieProps {
  summary: MarketingDashboardDTO;
}

export const CampaignTypePie: React.FC<CampaignTypePieProps> = ({ summary }) => {
  const data = useMemo(() => {
    const byType = summary.campaigns_by_type || {};
    return Object.entries(byType).map(([name, value], i) => ({
      name, value, fill: TYPE_PALETTE[i % TYPE_PALETTE.length],
    }));
  }, [summary]);

  if (!data.length) return (
    <Card><CardContent className="p-8 text-center text-sm text-[#5C6478]">Data not available</CardContent></Card>
  );

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Campaigns by Type</CardTitle>
        <span className="text-xs text-[#5C6478]">Campaign mix</span>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={75}
              paddingAngle={3}
            >
              {data.map((entry, i) => <Cell key={`cell-${i}`} fill={entry.fill} />)}
            </Pie>
            <Tooltip
              contentStyle={{ background: '#1D212A', border: '1px solid #262B35', borderRadius: 8, fontSize: 12 }}
              itemStyle={{ color: '#EDEFF3' }}
            />
            <Legend
              wrapperStyle={{ fontSize: 11, color: COLORS.text }}
              formatter={(value) => <span style={{ color: COLORS.text }}>{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// ---- Budget vs Revenue ----
interface BudgetRevenueChartProps {
  campaigns: CampaignAnalyticsDTO[];
}

export const BudgetRevenueChart: React.FC<BudgetRevenueChartProps> = ({ campaigns }) => {
  const data = useMemo(() =>
    campaigns.slice(0, 6).map((c) => ({
      name: c.campaign_name.substring(0, 14),
      budget: parseFloat(c.budget),
      revenue: parseFloat(c.total_revenue),
    })), [campaigns]);

  if (!data.length) return (
    <Card><CardContent className="p-8 text-center text-sm text-[#5C6478]">Data not available</CardContent></Card>
  );

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Budget vs Revenue</CardTitle>
        <span className="text-xs text-[#5C6478]">Spend vs attributed revenue per campaign</span>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} barSize={14}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
            <XAxis dataKey="name" tick={{ fill: COLORS.text, fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: COLORS.text, fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(108,140,255,0.05)' }} />
            <Legend wrapperStyle={{ fontSize: 11, color: COLORS.text }} formatter={(value) => <span style={{ color: COLORS.text }}>{value}</span>} />
            <Bar dataKey="budget" name="Budget ($)" fill={COLORS.budget} radius={[4, 4, 0, 0]} />
            <Bar dataKey="revenue" name="Revenue ($)" fill={COLORS.revenue} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
