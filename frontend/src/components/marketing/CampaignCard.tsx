import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Megaphone, DollarSign, TrendingUp, Users } from 'lucide-react';
import type { CampaignAnalyticsDTO } from '@/types';

interface CampaignCardProps {
  campaign: CampaignAnalyticsDTO;
}

export const CampaignCard: React.FC<CampaignCardProps> = ({ campaign }) => {
  const roi = parseFloat(campaign.roi_percentage) || 0;
  const isHighRoi = roi >= 100;

  return (
    <Card className="hover:border-[#6C8CFF]/50 transition-colors">
      <CardContent className="p-5 space-y-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-2.5">
            <div className="p-2 rounded-lg bg-[#6C8CFF]/10 text-[#6C8CFF]">
              <Megaphone className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-[#EDEFF3]">{campaign.campaign_name}</h4>
              <span className="text-xs text-[#8A93A6]">
                {campaign.outlet_name || `Outlet #${campaign.outlet_id}`} • {campaign.campaign_type || 'Promotion'}
              </span>
            </div>
          </div>
          <Badge variant={isHighRoi ? 'success' : 'warning'}>
            ROI {campaign.roi_percentage}%
          </Badge>
        </div>

        <div className="grid grid-cols-3 gap-2 py-3 border-y border-[#262B35] bg-[#171A20]/40 rounded-lg px-3 text-xs">
          <div>
            <span className="text-[10px] text-[#5C6478] block">Budget</span>
            <span className="font-mono font-bold text-[#EDEFF3]">${campaign.budget}</span>
          </div>
          <div>
            <span className="text-[10px] text-[#5C6478] block">Revenue</span>
            <span className="font-mono font-bold text-[#4FAE7C]">${campaign.total_revenue}</span>
          </div>
          <div>
            <span className="text-[10px] text-[#5C6478] block">Conv. Rate</span>
            <span className="font-mono font-bold text-[#EDEFF3]">{campaign.conversion_rate}%</span>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-[#8A93A6]">
          <span className="flex items-center gap-1 font-mono">
            <Users className="w-3 h-3 text-[#5C6478]" /> {campaign.total_conversions} Conversions
          </span>
          <span className="text-[11px] font-mono text-[#5C6478]">
            {campaign.start_date} to {campaign.end_date}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};
