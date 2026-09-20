import React, { useState } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Users, Bot, Plus, RefreshCw, Sparkles, CheckCircle2 } from 'lucide-react';
import { useWorkforce } from '@/hooks/useWorkforce';
import {
  StaffingSummaryCards,
  StaffingAlertsList,
  ShiftRosterTable,
  CreateScheduleModal,
} from '@/components/workforce';
import { ShiftStatusChart, AttendanceRateChart } from '@/components/workforce/WorkforceCharts';

export const Workforce: React.FC = () => {
  const { summary, alerts, shifts, loading, refresh, scheduleShift } = useWorkforce();
  const [isScheduleOpen, setIsScheduleOpen] = useState(false);
  const [rebalanced, setRebalanced] = useState(false);

  const handleRebalance = () => {
    setRebalanced(true);
    setTimeout(() => setRebalanced(false), 4000);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Workforce & Shift Optimization"
        subtitle="Staff attendance tracking, dynamic shift scheduling, and AI-assisted float rebalancing."
        badge={
          <Badge variant={alerts.length > 0 ? 'warning' : 'success'}>
            {alerts.length} Staffing Warnings
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={<RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />}
              onClick={refresh}
            >
              Sync Biometrics
            </Button>
            <Button
              variant="outline"
              size="sm"
              icon={<Plus className="w-3.5 h-3.5" />}
              onClick={() => setIsScheduleOpen(true)}
            >
              Schedule Shift
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={<Bot className="w-3.5 h-3.5" />}
              onClick={handleRebalance}
            >
              Autonomous Shift Rebalance
            </Button>
          </div>
        }
      />

      {rebalanced && (
        <div className="p-3.5 bg-[#4FAE7C]/10 border border-[#4FAE7C]/30 rounded-lg text-xs text-[#4FAE7C] flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>
            Staffing Agent dispatched 2 float barista units from Downtown Flagship to Airport Terminal to cover evening surge.
          </span>
        </div>
      )}

      {/* KPI Cards Row — real backend summary */}
      <StaffingSummaryCards summary={summary} />

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AttendanceRateChart summary={summary} />
        <ShiftStatusChart shifts={shifts} />
      </div>

      {/* Shift Roster + Alerts column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader separator>
              <div className="flex items-center justify-between w-full">
                <div>
                  <CardTitle>Daily Shift Roster & Attendance Matrix</CardTitle>
                  <span className="text-xs text-[#5C6478]">
                    Real-time biometric attendance — {shifts.length} shifts loaded
                  </span>
                </div>
                <Badge variant="outline">Live Roster</Badge>
              </div>
            </CardHeader>
            <ShiftRosterTable shifts={shifts} />
          </Card>
        </div>

        <div className="space-y-6">
          <StaffingAlertsList alerts={alerts} onDispatchFloat={handleRebalance} />

          {/* AI Workforce Recommendation */}
          <Card>
            <CardHeader separator>
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#6C8CFF]" />
                <CardTitle>Float Crew Optimization</CardTitle>
              </div>
              <Badge variant="accent" size="sm">Staff Agent</Badge>
            </CardHeader>
            <CardContent className="p-4 space-y-2.5 text-xs text-[#8A93A6]">
              <p>
                Airport Terminal experiences an average +35% foot-traffic spike between 17:00 and 20:00 due to cross-Atlantic flight departures.
              </p>
              <div className="p-3 bg-[#171A20] border border-[#262B35] rounded-lg font-mono text-[11px] text-[#EDEFF3]">
                Recommendation: Schedule 1 float barista on a split shift (16:30–21:00) to protect customer throughput.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Schedule Shift Modal */}
      <CreateScheduleModal
        isOpen={isScheduleOpen}
        onClose={() => setIsScheduleOpen(false)}
        onSubmit={scheduleShift}
      />
    </div>
  );
};
