import React from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Megaphone, Calendar, DollarSign, TrendingUp, Target, Users, MousePointer } from 'lucide-react';
import type { CampaignAnalyticsDTO } from '@/types';
import { formatCurrency, formatDate } from '@/utils/formatters';

interface CampaignDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  campaign: CampaignAnalyticsDTO | null;
}

const PERFORMANCE_BADGE: Record<string, 'success' | 'danger' | 'warning' | 'accent' | 'default'> = {
  'Top Performer': 'success',
  'High ROI': 'success',
  'Underperforming': 'danger',
  'Low ROI': 'danger',
  'Moderate': 'warning',
  'New Campaign': 'accent',
};

function getRoiColor(roi: number): string {
  if (roi >= 150) return '#4FAE7C';
  if (roi >= 50) return '#E8A33D';
  return '#D0555A';
}

export const CampaignDetailModal: React.FC<CampaignDetailModalProps> = ({ isOpen, onClose, campaign }) => {
  if (!campaign) return null;

  const roi = parseFloat(campaign.roi_percentage);
  const budget = parseFloat(campaign.budget);
  const revenue = parseFloat(campaign.total_revenue);
  const engRate = parseFloat(campaign.engagement_rate);
  const convRate = parseFloat(campaign.conversion_rate);
  const roiColor = getRoiColor(roi);
  const perfVariant = PERFORMANCE_BADGE[campaign.performance_label] || 'default';

  const kpiRows = [
    { icon: DollarSign, label: 'Budget', value: formatCurrency(budget), color: '#6C8CFF' },
    { icon: TrendingUp, label: 'Attributed Revenue', value: formatCurrency(revenue), color: '#4FAE7C' },
    { icon: TrendingUp, label: 'ROI', value: `${roi.toFixed(1)}%`, color: roiColor },
    { icon: Users, label: 'Impressions', value: (campaign.total_impressions || 0).toLocaleString(), color: '#E8A33D' },
    { icon: MousePointer, label: 'Clicks', value: (campaign.total_clicks || 0).toLocaleString(), color: '#6C8CFF' },
    { icon: Target, label: 'Conversions', value: (campaign.total_conversions || 0).toLocaleString(), color: '#4FAE7C' },
    { icon: Target, label: 'Engagement Rate', value: `${engRate.toFixed(2)}%`, color: '#E8A33D' },
    { icon: Target, label: 'Conversion Rate', value: `${convRate.toFixed(2)}%`, color: '#4FAE7C' },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Campaign Analytics Detail" size="md">
      <div className="space-y-4">
        {/* Campaign header */}
        <div className="p-3.5 bg-[#171A20] border border-[#262B35] rounded-lg">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-[#6C8CFF]/10 flex-shrink-0">
              <Megaphone className="w-4 h-4 text-[#6C8CFF]" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-semibold text-[#EDEFF3] truncate">{campaign.campaign_name}</h4>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <span className="text-xs text-[#8A93A6]">{campaign.outlet_name || `Outlet #${campaign.outlet_id}`}</span>
                <span className="text-[#262B35]">·</span>
                <span className="text-xs text-[#8A93A6]">{campaign.campaign_type}</span>
              </div>
            </div>
            <Badge variant={perfVariant} size="sm">{campaign.performance_label}</Badge>
          </div>
          <div className="flex items-center gap-4 mt-3 text-[11px] text-[#5C6478]">
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {formatDate(campaign.start_date, 'short')} – {formatDate(campaign.end_date, 'short')}
            </span>
            <Badge variant={campaign.status === 'Active' ? 'success' : 'warning'} size="sm">
              {campaign.status}
            </Badge>
          </div>
        </div>

        {/* KPI Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {kpiRows.map(({ icon: Icon, label, value, color }) => (
            <div key={label} className="p-3 bg-[#1D212A] border border-[#262B35] rounded-lg">
              <div className="flex items-center gap-1.5 mb-1">
                <Icon className="w-3 h-3" style={{ color }} />
                <span className="text-[10px] text-[#5C6478]">{label}</span>
              </div>
              <span className="font-mono font-bold text-sm" style={{ color }}>{value}</span>
            </div>
          ))}
        </div>

        {/* Engagement score */}
        {campaign.average_engagement_score && (
          <div className="p-3 bg-[#1D212A] border border-[#262B35] rounded-lg flex items-center justify-between">
            <span className="text-xs text-[#8A93A6]">Avg Engagement Score</span>
            <div className="flex items-center gap-2">
              <div className="w-24 bg-[#171A20] h-2 rounded-full overflow-hidden border border-[#262B35]">
                <div
                  className="h-full rounded-full bg-[#6C8CFF]"
                  style={{ width: `${Math.min(100, parseFloat(campaign.average_engagement_score) * 10)}%` }}
                />
              </div>
              <span className="font-mono font-bold text-[#EDEFF3] text-sm">
                {parseFloat(campaign.average_engagement_score).toFixed(1)} / 10
              </span>
            </div>
          </div>
        )}

        <div className="flex justify-end pt-1">
          <Button variant="primary" size="sm" onClick={onClose}>Close</Button>
        </div>
      </div>
    </Modal>
  );
};
