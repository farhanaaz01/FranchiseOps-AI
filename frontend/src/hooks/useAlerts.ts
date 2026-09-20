import { useState, useEffect, useCallback } from 'react';
import { alertsApi, UnifiedAlert } from '@/services/api/alertsApi';

export function useAlerts(pollingIntervalMs = 20000) {
  const [alerts, setAlerts] = useState<UnifiedAlert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    try {
      const res = await alertsApi.getAllAlerts();
      setAlerts(res);
      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Using cached alerts');
    } finally {
      setLoading(false);
    }
  }, []);

  const acknowledgeAlert = (id: string) => {
    alertsApi.acknowledgeAlert(id);
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'acknowledged' } : a))
    );
  };

  const resolveAlert = (id: string, note?: string) => {
    alertsApi.resolveAlert(id, note);
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'resolved' } : a))
    );
  };

  useEffect(() => {
    fetchAlerts();
    if (pollingIntervalMs > 0) {
      const interval = setInterval(fetchAlerts, pollingIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchAlerts, pollingIntervalMs]);

  return { alerts, loading, error, refresh: fetchAlerts, acknowledgeAlert, resolveAlert };
}
