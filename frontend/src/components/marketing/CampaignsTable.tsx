import React, { useState, useMemo } from 'react';
import { Badge } from '@/components/ui/Badge';
import { TrendingUp, TrendingDown, Search, ExternalLink } from 'lucide-react';
import type { CampaignAnalyticsDTO } from '@/types';
import { formatCurrency } from '@/utils/formatters';

interface CampaignsTableProps {
  campaigns: CampaignAnalyticsDTO[];
  onViewDetail?: (campaign: CampaignAnalyticsDTO) => void;
}

const PERF_VARIANT: Record<string, 'success' | 'danger' | 'warning' | 'accent' | 'default'> = {
  'Top Performer': 'success',
  'High ROI': 'success',
  'Underperforming': 'danger',
  'Low ROI': 'danger',
  'Moderate': 'warning',
  'New Campaign': 'accent',
};

export const CampaignsTable: React.FC<CampaignsTableProps> = ({ campaigns, onViewDetail }) => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'All' | 'Active' | 'Completed' | 'Paused'>('All');

  const filtered = useMemo(() => {
    return campaigns.filter((c) => {
      const matchSearch = !search ||
        c.campaign_name.toLowerCase().includes(search.toLowerCase()) ||
        (c.outlet_name || '').toLowerCase().includes(search.toLowerCase()) ||
        (c.campaign_type || '').toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === 'All' || c.status === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [campaigns, search, statusFilter]);

  return (
    <div>
      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-2 px-5 py-3 border-b border-[#262B35]">
        <div className="relative flex-1 min-w-[160px] max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-[#5C6478]" />
          <input
            type="text"
            placeholder="Search campaigns, outlets, type..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-7 pr-3 py-1 bg-[#171A20] border border-[#262B35] rounded text-[11px] text-[#EDEFF3] placeholder-[#5C6478] focus:outline-none focus:border-[#6C8CFF]/50"
          />
        </div>
        {(['All', 'Active', 'Completed', 'Paused'] as const).map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
              statusFilter === s
                ? 'bg-[#6C8CFF] text-white'
                : 'bg-[#1D212A] text-[#8A93A6] border border-[#262B35] hover:border-[#6C8CFF]/50'
            }`}
          >
            {s}
          </button>
        ))}
        <span className="text-xs text-[#5C6478] ml-auto">{filtered.length} campaigns</span>
      </div>

      {filtered.length === 0 ? (
        <div className="py-10 text-center text-sm text-[#5C6478]">No campaigns match the current filters.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#1D212A] text-[#8A93A6] font-mono border-b border-[#262B35]">
              <tr>
                <th className="px-5 py-3">Campaign Name</th>
                <th className="px-5 py-3">Outlet</th>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3">Budget</th>
                <th className="px-5 py-3">Revenue</th>
                <th className="px-5 py-3">ROI %</th>
                <th className="px-5 py-3">Engagement</th>
                <th className="px-5 py-3">Conv. Rate</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Performance</th>
                {onViewDetail && <th className="px-5 py-3"></th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#262B35]">
              {filtered.map((camp) => {
                const roiNum = parseFloat(camp.roi_percentage) || 0;
                const isHigh = roiNum >= 100;
                return (
                  <tr key={camp.campaign_id} className="hover:bg-[#1D212A]/50 transition-colors">
                    <td className="px-5 py-3.5">
                      <span className="font-semibold text-[#EDEFF3] block">{camp.campaign_name}</span>
                      <span className="text-[10px] font-mono text-[#5C6478]">{camp.start_date} – {camp.end_date}</span>
                    </td>
                    <td className="px-5 py-3.5 text-[#EDEFF3]">{camp.outlet_name || `Outlet #${camp.outlet_id}`}</td>
                    <td className="px-5 py-3.5 text-[#8A93A6]">{camp.campaign_type || 'Promo'}</td>
                    <td className="px-5 py-3.5 font-mono text-[#EDEFF3]">{formatCurrency(camp.budget)}</td>
                    <td className="px-5 py-3.5 font-mono font-medium text-[#4FAE7C]">{formatCurrency(camp.total_revenue)}</td>
                    <td className="px-5 py-3.5 font-mono font-bold">
                      <span className={`inline-flex items-center gap-1 ${isHigh ? 'text-[#4FAE7C]' : 'text-[#E8A33D]'}`}>
                        {isHigh ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {parseFloat(camp.roi_percentage).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[#8A93A6]">{parseFloat(camp.engagement_rate).toFixed(2)}%</td>
                    <td className="px-5 py-3.5 font-mono text-[#8A93A6]">{parseFloat(camp.conversion_rate).toFixed(2)}%</td>
                    <td className="px-5 py-3.5">
                      <Badge variant={camp.status === 'Active' ? 'success' : 'neutral'}>{camp.status}</Badge>
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge variant={PERF_VARIANT[camp.performance_label] || 'default'}>
                        {camp.performance_label}
                      </Badge>
                    </td>
                    {onViewDetail && (
                      <td className="px-5 py-3.5">
                        <button
                          onClick={() => onViewDetail(camp)}
                          className="p-1.5 rounded text-[#5C6478] hover:text-[#6C8CFF] hover:bg-[#6C8CFF]/10 transition-colors"
                          title="View Detail"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
