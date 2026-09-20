import React, { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell, CartesianGrid, Legend, PieChart, Pie,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import type { WorkforceDashboardDTO } from '@/types';
import type { EnrichedShiftRecord } from '@/hooks/useWorkforce';

const COLORS = {
  scheduled: '#6C8CFF',
  completed: '#4FAE7C',
  absent: '#D0555A',
  cancelled: '#E8A33D',
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

// ---- Shift Status Distribution ----
interface ShiftStatusChartProps {
  shifts: EnrichedShiftRecord[];
}

export const ShiftStatusChart: React.FC<ShiftStatusChartProps> = ({ shifts }) => {
  const data = useMemo(() => {
    const counts: Record<string, number> = { scheduled: 0, completed: 0, absent: 0, cancelled: 0 };
    shifts.forEach((s) => { counts[s.status] = (counts[s.status] || 0) + 1; });
    return [
      { name: 'Scheduled', count: counts.scheduled, fill: COLORS.scheduled },
      { name: 'Completed', count: counts.completed, fill: COLORS.completed },
      { name: 'Absent', count: counts.absent, fill: COLORS.absent },
      { name: 'Cancelled', count: counts.cancelled, fill: COLORS.cancelled },
    ].filter((d) => d.count > 0);
  }, [shifts]);

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Shift Status Breakdown</CardTitle>
        <span className="text-xs text-[#5C6478]">{shifts.length} total shifts</span>
      </CardHeader>
      <CardContent className="p-4">
        {data.length === 0 ? (
          <div className="h-40 flex items-center justify-center text-sm text-[#5C6478]">No shift data available</div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data} barSize={32}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
              <XAxis dataKey="name" tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: COLORS.text, fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(108,140,255,0.05)' }} />
              <Bar dataKey="count" name="Shifts" radius={[4, 4, 0, 0]}>
                {data.map((entry, i) => <Cell key={`cell-${i}`} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};

// ---- Workforce Summary KPI Mini-Chart ----
interface AttendanceChartProps {
  summary: WorkforceDashboardDTO;
}

export const AttendanceRateChart: React.FC<AttendanceChartProps> = ({ summary }) => {
  const attendanceRate = Math.min(100, parseFloat(summary.average_attendance_rate) || 0);
  const absentRate = 100 - attendanceRate;

  const pieData = [
    { name: 'Present', value: attendanceRate, fill: '#4FAE7C' },
    { name: 'Absent', value: absentRate, fill: '#262B35' },
  ];

  return (
    <Card>
      <CardHeader separator>
        <CardTitle>Attendance Rate</CardTitle>
        <span className="text-xs text-[#5C6478]">Avg across all outlets</span>
      </CardHeader>
      <CardContent className="p-4 flex items-center justify-center gap-8">
        <div className="relative">
          <PieChart width={140} height={140}>
            <Pie
              data={pieData}
              cx={65}
              cy={65}
              innerRadius={44}
              outerRadius={60}
              dataKey="value"
              startAngle={90}
              endAngle={-270}
              paddingAngle={3}
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
          </PieChart>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-xl font-bold font-mono text-[#4FAE7C]">{attendanceRate.toFixed(1)}%</span>
            <span className="text-[10px] text-[#5C6478]">Present</span>
          </div>
        </div>
        <div className="space-y-3">
          {[
            { label: 'Total Employees', value: summary.total_employees },
            { label: 'Active', value: summary.active_employees, color: '#4FAE7C' },
            { label: 'Outlets', value: summary.total_outlets_with_employees },
          ].map(({ label, value, color }) => (
            <div key={label}>
              <span className="text-[10px] text-[#5C6478] block">{label}</span>
              <span className="font-mono font-bold text-sm" style={{ color: color || '#EDEFF3' }}>{value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
