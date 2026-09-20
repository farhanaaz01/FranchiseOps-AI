import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ShoppingCart, CheckCircle2, Clock, Zap } from 'lucide-react';
import type { ReplenishmentRecommendationDTO } from '@/types';

interface ReplenishmentCardProps {
  recommendations: ReplenishmentRecommendationDTO[];
  approvedKeys: string[];
  onApprove: (key: string) => void;
}

export const ReplenishmentCard: React.FC<ReplenishmentCardProps> = ({
  recommendations,
  approvedKeys,
  onApprove,
}) => {
  return (
    <Card>
      <CardHeader separator>
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-[#E8A33D]" />
            <div>
              <CardTitle>Autonomous Replenishment Orders</CardTitle>
              <span className="text-xs text-[#5C6478]">
                Milestone 2 Inventory Agent: Reorder point formula triggered
              </span>
            </div>
          </div>
          <span className="text-xs font-mono text-[#8A93A6]">
            {recommendations.length} Suggestions
          </span>
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        {recommendations.map((rec) => {
          const key = `${rec.outlet_id}-${rec.product_id}`;
          const isApproved = approvedKeys.includes(key);

          return (
            <div
              key={key}
              className={`p-3.5 rounded-lg border transition-all ${
                isApproved
                  ? 'bg-[#4FAE7C]/5 border-[#4FAE7C]/30'
                  : 'bg-[#171A20] border-[#262B35] hover:border-[#6C8CFF]/40'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-xs text-[#EDEFF3]">
                      {rec.product_name}
                    </span>
                    <span className="text-[10px] font-mono text-[#6C8CFF] bg-[#6C8CFF]/10 px-1.5 py-0.5 rounded">
                      {rec.outlet_name || `Outlet #${rec.outlet_id}`}
                    </span>
                    {rec.days_until_stockout && (
                      <span className="text-[10px] font-mono text-[#D0555A] bg-[#D0555A]/10 px-1.5 py-0.5 rounded flex items-center gap-1">
                        <Clock className="w-2.5 h-2.5" /> {rec.days_until_stockout}d Runway
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[#8A93A6]">{rec.reason}</p>
                  <div className="text-[11px] font-mono text-[#5C6478]">
                    Current Stock: <span className="text-[#EDEFF3] font-bold">{rec.current_stock}</span> • Daily Demand: <span className="text-[#EDEFF3]">{rec.forecasted_daily_demand}/day</span>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center">
                  <div className="text-right">
                    <span className="text-[10px] text-[#5C6478] block">Recommend Order</span>
                    <span className="text-sm font-bold font-mono text-[#EDEFF3]">
                      +{rec.recommended_order_quantity}
                    </span>
                  </div>
                  {isApproved ? (
                    <div className="flex items-center gap-1 text-xs text-[#4FAE7C] font-medium bg-[#4FAE7C]/10 px-3 py-1.5 rounded-lg border border-[#4FAE7C]/20">
                      <CheckCircle2 className="w-3.5 h-3.5" /> PO Generated
                    </div>
                  ) : (
                    <Button
                      variant="primary"
                      size="sm"
                      icon={<ShoppingCart className="w-3.5 h-3.5" />}
                      onClick={() => onApprove(key)}
                    >
                      Approve PO
                    </Button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
};
