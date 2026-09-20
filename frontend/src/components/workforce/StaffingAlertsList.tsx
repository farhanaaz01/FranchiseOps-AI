import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { AlertTriangle, UserMinus, ArrowRight } from 'lucide-react';
import type { StaffingAlertDTO } from '@/types';

interface StaffingAlertsListProps {
  alerts: StaffingAlertDTO[];
  onDispatchFloat?: (outletId: number) => void;
}

export const StaffingAlertsList: React.FC<StaffingAlertsListProps> = ({
  alerts,
  onDispatchFloat,
}) => {
  return (
    <Card>
      <CardHeader separator>
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-[#E8A33D]" />
            <CardTitle>Staffing Deficit & Overtime Warnings</CardTitle>
          </div>
          <span className="text-xs font-mono text-[#E8A33D]">
            {alerts.length} Warnings Active
          </span>
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        {alerts.map((alert, idx) => (
          <div
            key={`${alert.outlet_id}-${idx}`}
            className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 bg-[#171A20] border border-[#262B35] rounded-lg"
          >
            <div className="flex items-start gap-3">
              <div className="p-2 bg-[#E8A33D]/10 text-[#E8A33D] rounded-lg mt-0.5">
                <UserMinus className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-[#EDEFF3]">
                    {alert.outlet_name || `Outlet #${alert.outlet_id}`}
                  </span>
                  <span className="text-[10px] font-mono text-[#D0555A] bg-[#D0555A]/10 px-1.5 py-0.5 rounded">
                    Gap: {alert.expected_staff_count - alert.scheduled_staff_count} Staff
                  </span>
                </div>
                <p className="text-xs text-[#8A93A6]">{alert.message}</p>
                <div className="text-[11px] font-mono text-[#5C6478]">
                  Scheduled: <span className="text-[#EDEFF3]">{alert.scheduled_staff_count}</span> • Required: <span className="text-[#EDEFF3]">{alert.expected_staff_count}</span>
                </div>
              </div>
            </div>

            {onDispatchFloat && (
              <Button
                variant="outline"
                size="sm"
                className="self-end sm:self-center text-xs"
                onClick={() => onDispatchFloat(alert.outlet_id)}
                icon={<ArrowRight className="w-3 h-3" />}
              >
                Dispatch Float Staff
              </Button>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
