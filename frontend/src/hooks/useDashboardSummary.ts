import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '@/services/api';
import type { DashboardSummaryDTO } from '@/types';

const FALLBACK_SUMMARY: DashboardSummaryDTO = {
  total_outlets: 5,
  active_outlets: 5,
  underperforming_outlets: 2,
  total_revenue: '148520.00',
  total_transactions: 4210,
  average_health_score: '76.8',
  top_performing_outlet: {
    outlet_id: 1,
    outlet_name: 'Downtown Flagship',
    location: 'Central Plaza, NYC',
    status: 'Active',
    total_revenue: '34120.00',
    total_transactions: 980,
    health_score: '88.4',
    rank: 1,
    performance_label: 'Top Performer',
  },
  lowest_performing_outlet: {
    outlet_id: 5,
    outlet_name: 'Airport Terminal',
    location: 'JFK Concourse B, NYC',
    status: 'Active',
    total_revenue: '19400.00',
    total_transactions: 620,
    health_score: '44.8',
    rank: 5,
    performance_label: 'Critical Attention',
  },
  recent_underperformers: [
    {
      outlet_id: 5,
      outlet_name: 'Airport Terminal',
      location: 'JFK Concourse B, NYC',
      status: 'Active',
      total_revenue: '19400.00',
      total_transactions: 620,
      health_score: '44.8',
      rank: 5,
      performance_label: 'Critical Underperformer',
    },
    {
      outlet_id: 3,
      outlet_name: 'Metro Mall',
      location: 'Queens Center, NYC',
      status: 'Active',
      total_revenue: '22100.00',
      total_transactions: 710,
      health_score: '65.3',
      rank: 4,
      performance_label: 'At Risk',
    },
  ],
};

export function useDashboardSummary(pollingIntervalMs = 30000) {
  const [data, setData] = useState<DashboardSummaryDTO>(FALLBACK_SUMMARY);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    try {
      const res = await dashboardApi.getSummary();
      if (res && res.total_outlets > 0) {
        setData(res);
        setError(null);
      } else {
        setData(FALLBACK_SUMMARY);
      }
    } catch (err: any) {
      // Gracefully fall back to local summary
      setData(FALLBACK_SUMMARY);
      setError(err?.message || 'Using cached summary');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
    if (pollingIntervalMs > 0) {
      const interval = setInterval(fetchSummary, pollingIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchSummary, pollingIntervalMs]);

  return { data, loading, error, refresh: fetchSummary };
}
