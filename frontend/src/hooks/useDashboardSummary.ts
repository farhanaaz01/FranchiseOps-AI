import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '@/services/api';
import type { DashboardSummaryDTO } from '@/types';

export function useDashboardSummary(pollingIntervalMs = 30000) {
  const [data, setData] = useState<DashboardSummaryDTO | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    try {
      const res = await dashboardApi.getSummary();
      setData(res);
      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch dashboard summary. Is the backend running?');
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
