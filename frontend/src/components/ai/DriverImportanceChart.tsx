import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import type { RiskFeatureImportance } from '@/types';

interface DriverImportanceChartProps {
  importances: RiskFeatureImportance[];
}

const FEATURE_LABELS: Record<string, string> = {
  compliance_score: 'Audit Compliance Score (Audit)',
  revenue_growth_pct: '30-Day Revenue Growth % (Financial)',
  wastage_rate: 'Inventory Wastage Rate (Inventory)',
  avg_daily_revenue: 'Average Daily Revenue (Financial)',
  peak_understaffed_pct: 'Peak Shift Understaffing % (Staff)',
  campaign_roi: 'Marketing Campaign ROI (Marketing)',
  absenteeism_rate: 'Staff Absenteeism Rate (Staff)',
};

function formatFeatureLabel(feature: string): string {
  return FEATURE_LABELS[feature] || feature;
}

export const DriverImportanceChart: React.FC<DriverImportanceChartProps> = ({ importances }) => {
  return (
    <Card>
      <CardHeader separator>
        <div>
          <CardTitle>XGBoost Risk Driver Feature Importances</CardTitle>
          <span className="text-xs text-[#5C6478]">
            Relative weight of operational factors in predicting underperformance risk
          </span>
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        {importances.map((item, idx) => {
          const pct = Math.round(item.importance * 100);
          return (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#EDEFF3] font-medium">{formatFeatureLabel(item.feature)}</span>
                <span className="font-mono text-[#6C8CFF] font-semibold">{pct}%</span>
              </div>
              <div className="w-full bg-[#171A20] h-2 rounded-full overflow-hidden border border-[#262B35]">
                <div
                  className="bg-gradient-to-r from-[#6C8CFF] to-[#8EAEFF] h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
};
