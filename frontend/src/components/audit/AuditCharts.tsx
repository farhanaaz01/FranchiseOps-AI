import React, { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, CartesianGrid, ReferenceLine,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import type { ComplianceOutletRecord } from '@/services/api/auditApi';

const COLORS = {
  healthy: '#4FAE7C',
  risk: '#E8A33D',
  critical: '#D0555A',
  threshold: '#6C8CFF',
  grid: '#262B35',
  text: '#8A93A6',
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1D212A] border border-[#262B35] rounded-lg p-3 text-xs shadow-xl">
      <p className="font-semibold text-[#EDEFF3] mb-1.5">{label}</p>
      {payload.map((entry: any) => (
        <p key={entry.dataKey} style={{ color: entry.fill || entry.color }}>
          {entry.name}: <span className="font-mono font-bold">{typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value}</span>
        </p>
      ))}
    </div>
  );
};

// ---- Compliance Score Bar Chart ----
interface ComplianceBarChartProps {
  records: ComplianceOutletRecord[];
}

export const ComplianceBarChart: React.FC<ComplianceBarChartProps> = ({ records }) => {
  const data = useMemo(() =>
    [...records]
      .sort((a, b) => b.compliance_score - a.compliance_score)
      .map((r) => ({
        name: r.outlet_id.replace('OUT-', 'Outlet '),
        score: r.compliance_score,
        fill: r.compliance_score >= 80 ? COLORS.healthy : r.compliance_score >= 65 ? COLORS.risk : COLORS.critical,
      })), [records]);

  if (!data.length) return (
    <Card><CardContent className="p-8 text-center text-sm text-[#5C6478]">Data not available</CardContent></Card>
  );

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Compliance Score by Outlet</CardTitle>
        <span className="text-xs text-[#5C6478]">Blue line = 75% threshold</span>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data} barSize={28}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
            <XAxis dataKey="name" tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 100]} tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(108,140,255,0.05)' }} />
            <ReferenceLine y={75} stroke={COLORS.threshold} strokeDasharray="4 4" strokeWidth={1.5} />
            <Bar dataKey="score" name="Compliance Score" radius={[4, 4, 0, 0]}>
              {data.map((entry, i) => <Cell key={`cell-${i}`} fill={entry.fill} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

// ---- Wastage Rate Chart ----
export const WastageRateChart: React.FC<ComplianceBarChartProps> = ({ records }) => {
  const data = useMemo(() =>
    [...records]
      .sort((a, b) => b.wastage_rate - a.wastage_rate)
      .map((r) => ({
        name: r.outlet_id.replace('OUT-', 'Outlet '),
        wastage: r.wastage_rate,
        absenteeism: r.absenteeism_rate,
        fill: r.wastage_rate > 4 ? COLORS.critical : r.wastage_rate > 2 ? COLORS.risk : COLORS.healthy,
      })), [records]);

  if (!data.length) return (
    <Card><CardContent className="p-8 text-center text-sm text-[#5C6478]">Data not available</CardContent></Card>
  );

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Wastage & Absenteeism by Outlet</CardTitle>
        <span className="text-xs text-[#5C6478]">Operational risk indicators (%)</span>
      </CardHeader>
      <CardContent className="p-4">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} barSize={14}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
            <XAxis dataKey="name" tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(108,140,255,0.05)' }} />
            <Bar dataKey="wastage" name="Wastage Rate" fill={COLORS.critical} radius={[4, 4, 0, 0]} />
            <Bar dataKey="absenteeism" name="Absenteeism Rate" fill={COLORS.risk} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
