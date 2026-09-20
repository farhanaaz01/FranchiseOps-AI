import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { AlertTriangle, AlertCircle, Package } from 'lucide-react';
import type { StockAlertDTO } from '@/types';

interface StockAlertsListProps {
  alerts: StockAlertDTO[];
}

export const StockAlertsList: React.FC<StockAlertsListProps> = ({ alerts }) => {
  return (
    <Card>
      <CardHeader separator>
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-[#D0555A]" />
            <CardTitle>Active Stock Threshold Breaches</CardTitle>
          </div>
          <span className="text-xs font-mono text-[#D0555A] font-semibold">
            {alerts.length} Critical
          </span>
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-2.5">
        {alerts.map((alert, idx) => {
          const isCritical = alert.alert_type === 'CRITICAL';
          return (
            <div
              key={`${alert.outlet_id}-${alert.product_id}-${idx}`}
              className="flex items-start gap-3 p-3 bg-[#171A20] border border-[#262B35] rounded-lg"
            >
              <div
                className={`p-2 rounded-lg mt-0.5 ${
                  isCritical ? 'bg-[#D0555A]/10 text-[#D0555A]' : 'bg-[#E8A33D]/10 text-[#E8A33D]'
                }`}
              >
                {isCritical ? <AlertCircle className="w-4 h-4" /> : <Package className="w-4 h-4" />}
              </div>
              <div className="space-y-0.5 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-[#EDEFF3]">{alert.product_name}</span>
                  <span className="text-[10px] font-mono text-[#6C8CFF]">
                    {alert.outlet_name || `Outlet #${alert.outlet_id}`}
                  </span>
                </div>
                <p className="text-xs text-[#8A93A6]">{alert.message}</p>
                <div className="text-[11px] font-mono text-[#5C6478] pt-1">
                  Current: <span className="text-[#D0555A] font-bold">{alert.current_stock}</span> / Safety Threshold: {alert.threshold}
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
};
