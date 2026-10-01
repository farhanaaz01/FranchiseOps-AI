import { useState, useEffect, useCallback } from 'react';
import { inventoryApi } from '@/services/api';
import { apiPost } from '@/services/api/apiClient';
import type {
  InventoryDashboardDTO,
  InventoryStatusDTO,
  StockAlertDTO,
  ReplenishmentRecommendationDTO,
  InventoryTransactionCreate,
} from '@/types';

const EMPTY_SUMMARY: InventoryDashboardDTO = {
  total_products: 0,
  total_inventory_items: 0,
  total_stock_value: '0.00',
  low_stock_count: 0,
  critical_stock_count: 0,
  overstock_count: 0,
  total_wastage_30_days: '0.00',
  top_alerts: [],
  replenishment_recommendations: [],
};

export function useInventory(pollingIntervalMs = 30000) {
  const [dashboardSummary, setDashboardSummary] = useState<InventoryDashboardDTO>(EMPTY_SUMMARY);
  const [statusList, setStatusList] = useState<InventoryStatusDTO[]>([]);
  const [alerts, setAlerts] = useState<StockAlertDTO[]>([]);
  const [recommendations, setRecommendations] = useState<ReplenishmentRecommendationDTO[]>([]);
  const [approvedRecs, setApprovedRecs] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInventory = useCallback(async () => {
    try {
      const [summaryRes, statusRes, alertsRes, recsRes] = await Promise.allSettled([
        inventoryApi.getDashboardSummary(),
        inventoryApi.getStatus(),
        inventoryApi.getAlerts(),
        inventoryApi.getReplenishmentRecommendations(),
      ]);

      setDashboardSummary(
        summaryRes.status === 'fulfilled' ? summaryRes.value : EMPTY_SUMMARY
      );
      setStatusList(
        statusRes.status === 'fulfilled' ? statusRes.value : []
      );
      setAlerts(
        alertsRes.status === 'fulfilled' ? alertsRes.value : []
      );
      setRecommendations(
        recsRes.status === 'fulfilled' ? recsRes.value : []
      );

      // Report errors if all failed
      const anyFulfilled = [summaryRes, statusRes, alertsRes, recsRes].some(
        (r) => r.status === 'fulfilled'
      );
      if (!anyFulfilled) {
        setError('Failed to fetch inventory data from backend.');
      } else {
        setError(null);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch inventory data');
    } finally {
      setLoading(false);
    }
  }, []);

  const approveRecommendation = (key: string) => {
    setApprovedRecs((prev) => [...prev, key]);
  };

  const recordTransaction = async (tx: InventoryTransactionCreate): Promise<boolean> => {
    try {
      await apiPost('/api/inventory-transactions', {
        inventory_id: tx.inventory_id,
        transaction_date: new Date().toISOString().split('T')[0],
        transaction_type: tx.transaction_type,
        quantity: tx.quantity,
        reason: tx.reason || null,
      });
      // Refresh inventory data after recording
      await fetchInventory();
      return true;
    } catch (err: any) {
      setError(err?.message || 'Failed to record transaction');
      return false;
    }
  };

  useEffect(() => {
    fetchInventory();
    if (pollingIntervalMs > 0) {
      const interval = setInterval(fetchInventory, pollingIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchInventory, pollingIntervalMs]);

  return {
    dashboardSummary,
    statusList,
    alerts,
    recommendations,
    approvedRecs,
    loading,
    error,
    refresh: fetchInventory,
    approveRecommendation,
    recordTransaction,
  };
}
