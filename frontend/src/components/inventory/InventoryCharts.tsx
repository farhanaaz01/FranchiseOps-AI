import React, { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, Legend, CartesianGrid,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import type { InventoryStatusDTO, InventoryDashboardDTO } from '@/types';

// ---- Design tokens ----
const COLORS = {
  normal: '#4FAE7C',
  low: '#E8A33D',
  critical: '#D0555A',
  overstock: '#6C8CFF',
  grid: '#262B35',
  text: '#8A93A6',
};

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

// ---- Stock Status Distribution ----
interface StatusDistributionChartProps {
  summary: InventoryDashboardDTO;
}

export const StockStatusDistributionChart: React.FC<StatusDistributionChartProps> = ({ summary }) => {
  const data = useMemo(() => [
    { name: 'Normal', count: summary.total_inventory_items - summary.low_stock_count - summary.critical_stock_count - summary.overstock_count, fill: COLORS.normal },
    { name: 'Low Stock', count: summary.low_stock_count, fill: COLORS.low },
    { name: 'Critical', count: summary.critical_stock_count, fill: COLORS.critical },
    { name: 'Overstock', count: summary.overstock_count, fill: COLORS.overstock },
  ], [summary]);

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Stock Health Distribution</CardTitle>
        <span className="text-xs text-[#5C6478]">{summary.total_inventory_items} total SKUs</span>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} barSize={32}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
            <XAxis dataKey="name" tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(108,140,255,0.05)' }} />
            <Bar dataKey="count" name="SKUs" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// ---- Stock vs Reorder Level ----
interface StockVsReorderChartProps {
  items: InventoryStatusDTO[];
}

export const StockVsReorderChart: React.FC<StockVsReorderChartProps> = ({ items }) => {
  const data = useMemo(() => {
    return items.slice(0, 10).map((item) => ({
      name: (item.product_name || `SKU-${item.product_id}`).substring(0, 12),
      current: parseFloat(item.current_stock) || 0,
      reorder: parseFloat(item.reorder_point) || 0,
      outlet: item.outlet_name || `Outlet #${item.outlet_id}`,
    }));
  }, [items]);

  if (data.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-sm text-[#5C6478]">Data not available</CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Stock vs Reorder Point</CardTitle>
        <span className="text-xs text-[#5C6478]">Current on-hand vs reorder threshold</span>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data} barSize={14}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
            <XAxis dataKey="name" tick={{ fill: COLORS.text, fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(108,140,255,0.05)' }} />
            <Legend
              wrapperStyle={{ fontSize: 11, color: COLORS.text }}
              formatter={(value) => <span style={{ color: COLORS.text }}>{value}</span>}
            />
            <Bar dataKey="current" name="Current Stock" fill={COLORS.normal} radius={[4, 4, 0, 0]} />
            <Bar dataKey="reorder" name="Reorder Point" fill={COLORS.low} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
