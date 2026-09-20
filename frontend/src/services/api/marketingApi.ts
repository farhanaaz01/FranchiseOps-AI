import { apiGet } from './apiClient';
import type { MarketingDashboardDTO, CampaignAnalyticsDTO } from '@/types';

export const marketingApi = {
  /**
   * Fetch marketing dashboard summary (campaigns, spend, revenue, ROI)
   */
  getSummary: (): Promise<MarketingDashboardDTO> => {
    return apiGet<MarketingDashboardDTO>('/api/marketing/dashboard/summary');
  },

  /**
   * Fetch analytics for all active campaigns
   */
  getCampaigns: (): Promise<CampaignAnalyticsDTO[]> => {
    return apiGet<CampaignAnalyticsDTO[]>('/api/marketing/dashboard/campaigns');
  },

  /**
   * Fetch analytics for a single campaign
   */
  getCampaignById: (campaignId: number | string): Promise<CampaignAnalyticsDTO> => {
    return apiGet<CampaignAnalyticsDTO>(`/api/marketing/dashboard/campaigns/${campaignId}`);
  },
};
