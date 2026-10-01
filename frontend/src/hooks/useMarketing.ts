import { useState, useEffect, useCallback } from 'react';
import { marketingApi } from '@/services/api';
import { apiPost } from '@/services/api/apiClient';
import type {
  MarketingDashboardDTO,
  CampaignAnalyticsDTO,
  MarketingCampaignCreate,
} from '@/types';

const EMPTY_SUMMARY: MarketingDashboardDTO = {
  total_campaigns: 0,
  active_campaigns: 0,
  total_budget: '0.00',
  total_revenue: '0.00',
  overall_roi_percentage: '0.00',
  average_engagement_rate: '0.00',
  average_conversion_rate: '0.00',
  top_campaigns: [],
  underperforming_campaigns: [],
  campaigns_by_type: {},
};

export function useMarketing(pollingIntervalMs = 30000) {
  const [summary, setSummary] = useState<MarketingDashboardDTO>(EMPTY_SUMMARY);
  const [campaigns, setCampaigns] = useState<CampaignAnalyticsDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMarketing = useCallback(async () => {
    try {
      const [sumRes, campsRes] = await Promise.allSettled([
        marketingApi.getSummary(),
        marketingApi.getCampaigns(),
      ]);

      setSummary(
        sumRes.status === 'fulfilled' ? sumRes.value : EMPTY_SUMMARY
      );
      setCampaigns(
        campsRes.status === 'fulfilled' ? campsRes.value : []
      );

      const anyFulfilled = [sumRes, campsRes].some(
        (r) => r.status === 'fulfilled'
      );
      if (!anyFulfilled) {
        setError('Failed to fetch marketing data from backend.');
      } else {
        setError(null);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch marketing data');
    } finally {
      setLoading(false);
    }
  }, []);

  const createCampaign = async (payload: MarketingCampaignCreate): Promise<boolean> => {
    try {
      await apiPost('/api/marketing-campaigns', {
        outlet_id: payload.outlet_id,
        campaign_name: payload.campaign_name,
        campaign_type: payload.channel || 'Digital Promotion',
        start_date: payload.start_date,
        end_date: payload.end_date,
        budget: payload.budget,
        status: 'Active',
      });
      await fetchMarketing();
      return true;
    } catch (err: any) {
      setError(err?.message || 'Failed to create campaign');
      return false;
    }
  };

  useEffect(() => {
    fetchMarketing();
    if (pollingIntervalMs > 0) {
      const interval = setInterval(fetchMarketing, pollingIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchMarketing, pollingIntervalMs]);

  return { summary, campaigns, loading, error, refresh: fetchMarketing, createCampaign };
}
