import React, { useState } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { KPICard } from '@/components/kpi/KPICard';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Megaphone, TrendingUp, DollarSign, Target, Plus, RefreshCw } from 'lucide-react';
import { useMarketing } from '@/hooks/useMarketing';
import { useOutlets } from '@/hooks/useOutlets';
import { CampaignCard, CampaignsTable, CreateCampaignModal } from '@/components/marketing';
import { CampaignDetailModal } from '@/components/marketing/CampaignDetailModal';
import { ROIRankingChart, CampaignTypePie, BudgetRevenueChart } from '@/components/marketing/MarketingCharts';
import { formatCurrency } from '@/utils/formatters';
import type { CampaignAnalyticsDTO } from '@/types';

export const Marketing: React.FC = () => {
  const { summary, campaigns, loading, refresh, createCampaign } = useMarketing();
  const { outlets } = useOutlets();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [detailCampaign, setDetailCampaign] = useState<CampaignAnalyticsDTO | null>(null);

  const totalBudget = parseFloat(summary.total_budget) || 0;
  const totalRev = parseFloat(summary.total_revenue) || 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Marketing & Campaign ROI"
        subtitle="Multi-channel campaign attribution, localized outlet promotions, and promotional ROI tracking."
        badge={<Badge variant="accent">{summary.active_campaigns || campaigns.length} Active Campaigns</Badge>}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={<RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />}
              onClick={refresh}
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={<Plus className="w-3.5 h-3.5" />}
              onClick={() => setIsModalOpen(true)}
            >
              New Campaign
            </Button>
          </div>
        }
      />

      {/* KPI Cards Row — real backend summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Active Campaigns"
          value={String(summary.active_campaigns || campaigns.length)}
          subtext={`Across ${summary.total_campaigns || campaigns.length} total launches`}
          icon={<Megaphone className="w-4 h-4 text-[#6C8CFF]" />}
        />
        <KPICard
          title="Overall Campaign ROI"
          value={`${parseFloat(summary.overall_roi_percentage || '0').toFixed(1)}%`}
          status="healthy"
          icon={<TrendingUp className="w-4 h-4 text-[#4FAE7C]" />}
        />
        <KPICard
          title="Attributed Revenue"
          value={formatCurrency(totalRev, true)}
          subtext={`From ${formatCurrency(totalBudget, true)} spend`}
          status="healthy"
          icon={<DollarSign className="w-4 h-4 text-[#4FAE7C]" />}
        />
        <KPICard
          title="Avg Conversion Rate"
          value={`${parseFloat(summary.average_conversion_rate || '0').toFixed(1)}%`}
          subtext="Target benchmark: 2.5%"
          status="healthy"
          icon={<Target className="w-4 h-4 text-[#6C8CFF]" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ROIRankingChart campaigns={campaigns} />
        </div>
        <CampaignTypePie summary={summary} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BudgetRevenueChart campaigns={campaigns} />

        {/* Top performers column */}
        <div className="space-y-4">
          {(summary.top_campaigns || []).slice(0, 2).map((camp) => (
            <CampaignCard key={camp.campaign_id} campaign={camp} />
          ))}
          {(summary.underperforming_campaigns || []).slice(0, 1).map((camp) => (
            <CampaignCard key={camp.campaign_id} campaign={camp} />
          ))}
          {!summary.top_campaigns?.length && campaigns.slice(0, 2).map((camp) => (
            <CampaignCard key={camp.campaign_id} campaign={camp} />
          ))}
        </div>
      </div>

      {/* Full Campaigns Table */}
      <Card>
        <CardHeader separator>
          <CardTitle>Campaign Performance & Multi-Unit Attribution</CardTitle>
          <Badge variant="outline">Attribution Model</Badge>
        </CardHeader>
        <CampaignsTable campaigns={campaigns} onViewDetail={(c) => setDetailCampaign(c)} />
      </Card>

      {/* Create Campaign Modal */}
      <CreateCampaignModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={createCampaign}
        outlets={outlets.map((o) => ({ outlet_id: o.outlet_id, name: `${o.id}: ${o.name}` }))}
      />

      {/* Campaign Detail Modal */}
      <CampaignDetailModal
        isOpen={Boolean(detailCampaign)}
        onClose={() => setDetailCampaign(null)}
        campaign={detailCampaign}
      />
    </div>
  );
};
