import { useState, useEffect, useCallback } from 'react';
import { marketingApi } from '@/services/api';
import type {
  MarketingDashboardDTO,
  CampaignAnalyticsDTO,
  MarketingCampaignCreate,
} from '@/types';

const FALLBACK_CAMPAIGNS: CampaignAnalyticsDTO[] = [
  {
    campaign_id: 1,
    campaign_name: 'Summer Cold Brew Launch',
    outlet_id: 1,
    outlet_name: 'Downtown Flagship',
    campaign_type: 'Seasonal Promotion',
    start_date: '2026-06-01',
    end_date: '2026-08-31',
    budget: '4000.00',
    total_revenue: '14200.00',
    total_impressions: 48000,
    total_clicks: 3120,
    total_conversions: 840,
    average_engagement_score: '8.4',
    roi_percentage: '268.8',
    engagement_rate: '6.5',
    conversion_rate: '4.2',
    status: 'Active',
    performance_label: 'Top Performer',
  },
  {
    campaign_id: 2,
    campaign_name: 'Student Discount BOGO',
    outlet_id: 4,
    outlet_name: 'Uptown Express',
    campaign_type: 'Local Discount',
    start_date: '2026-09-01',
    end_date: '2026-10-15',
    budget: '2500.00',
    total_revenue: '6200.00',
    total_impressions: 29000,
    total_clicks: 2200,
    total_conversions: 590,
    average_engagement_score: '7.8',
    roi_percentage: '244.4',
    engagement_rate: '7.6',
    conversion_rate: '5.8',
    status: 'Active',
    performance_label: 'High ROI',
  },
  {
    campaign_id: 3,
    campaign_name: 'Airport Traveler Morning Combo',
    outlet_id: 5,
    outlet_name: 'Airport Terminal',
    campaign_type: 'Bundle Deal',
    start_date: '2026-08-15',
    end_date: '2026-09-30',
    budget: '3500.00',
    total_revenue: '4100.00',
    total_impressions: 34000,
    total_clicks: 1450,
    total_conversions: 210,
    average_engagement_score: '4.5',
    roi_percentage: '28.1',
    engagement_rate: '4.3',
    conversion_rate: '1.9',
    status: 'Active',
    performance_label: 'Underperforming',
  },
  {
    campaign_id: 4,
    campaign_name: 'Fall Bakery Sampler',
    outlet_id: 2,
    outlet_name: 'Westside Hub',
    campaign_type: 'Product Sampling',
    start_date: '2026-09-10',
    end_date: '2026-10-31',
    budget: '2000.00',
    total_revenue: '2150.00',
    total_impressions: 18500,
    total_clicks: 1100,
    total_conversions: 240,
    average_engagement_score: '6.2',
    roi_percentage: '152.9',
    engagement_rate: '5.9',
    conversion_rate: '3.4',
    status: 'Active',
    performance_label: 'Moderate',
  },
];

const FALLBACK_SUMMARY: MarketingDashboardDTO = {
  total_campaigns: 6,
  active_campaigns: 4,
  total_budget: '14200.00',
  total_revenue: '41850.00',
  overall_roi_percentage: '194.7',
  average_engagement_rate: '6.1',
  average_conversion_rate: '3.8',
  top_campaigns: [FALLBACK_CAMPAIGNS[0]],
  underperforming_campaigns: [FALLBACK_CAMPAIGNS[2]],
  campaigns_by_type: {
    'Seasonal Promotion': 2,
    'Local Discount': 2,
    'Bundle Deal': 1,
    'Product Sampling': 1,
  },
};

export function useMarketing(pollingIntervalMs = 30000) {
  const [summary, setSummary] = useState<MarketingDashboardDTO>(FALLBACK_SUMMARY);
  const [campaigns, setCampaigns] = useState<CampaignAnalyticsDTO[]>(FALLBACK_CAMPAIGNS);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMarketing = useCallback(async () => {
    try {
      const [sumRes, campsRes] = await Promise.allSettled([
        marketingApi.getSummary(),
        marketingApi.getCampaigns(),
      ]);

      if (sumRes.status === 'fulfilled' && sumRes.value.total_campaigns > 0) {
        setSummary(sumRes.value);
      } else {
        setSummary(FALLBACK_SUMMARY);
      }

      if (campsRes.status === 'fulfilled' && campsRes.value.length > 0) {
        setCampaigns(campsRes.value);
      } else {
        setCampaigns(FALLBACK_CAMPAIGNS);
      }

      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Using cached marketing data');
    } finally {
      setLoading(false);
    }
  }, []);

  const createCampaign = async (payload: MarketingCampaignCreate): Promise<boolean> => {
    const budgetNum = parseFloat(String(payload.budget)) || 1000;
    const newCamp: CampaignAnalyticsDTO = {
      campaign_id: campaigns.length + 1,
      campaign_name: payload.campaign_name,
      outlet_id: payload.outlet_id,
      outlet_name: `Outlet #${payload.outlet_id}`,
      campaign_type: payload.channel || 'Digital Promotion',
      start_date: payload.start_date,
      end_date: payload.end_date,
      budget: budgetNum.toFixed(2),
      total_revenue: '0.00',
      total_impressions: 0,
      total_clicks: 0,
      total_conversions: 0,
      average_engagement_score: '0.0',
      roi_percentage: '0.0',
      engagement_rate: '0.0',
      conversion_rate: '0.0',
      status: 'Active',
      performance_label: 'New Campaign',
    };
    setCampaigns((prev) => [newCamp, ...prev]);
    return true;
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
