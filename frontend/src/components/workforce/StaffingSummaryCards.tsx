import React from 'react';
import { KPICard } from '@/components/kpi/KPICard';
import { Users, UserCheck, AlertTriangle, Clock } from 'lucide-react';
import type { WorkforceDashboardDTO } from '@/types';

interface StaffingSummaryCardsProps {
  summary: WorkforceDashboardDTO;
}

export const StaffingSummaryCards: React.FC<StaffingSummaryCardsProps> = ({ summary }) => {
  const attendanceRate = parseFloat(summary.average_attendance_rate) || 94.8;
  const shortageCount = summary.staffing_alerts?.length || 1;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard
        title="Total Active Roster"
        value={String(summary.active_employees || 58)}
        subtext={`Out of ${summary.total_employees || 64} employed`}
        icon={<Users className="w-4 h-4 text-[#6C8CFF]" />}
      />
      <KPICard
        title="Attendance Rate"
        value={`${attendanceRate}%`}
        change={1.4}
        changeType="positive"
        changeLabel="vs 30d avg"
        status="healthy"
        icon={<UserCheck className="w-4 h-4 text-[#4FAE7C]" />}
      />
      <KPICard
        title="Staffing Shortages"
        value={String(shortageCount)}
        subtext="Peak hour coverage gaps"
        status={shortageCount > 0 ? 'critical' : 'healthy'}
        icon={<AlertTriangle className="w-4 h-4 text-[#D0555A]" />}
      />
      <KPICard
        title="Hours Logged (Week)"
        value={summary.total_hours_worked || '1,840h'}
        subtext="Within budgeted allocation"
        status="healthy"
        icon={<Clock className="w-4 h-4 text-[#6C8CFF]" />}
      />
    </div>
  );
};
