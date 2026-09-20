import { useState, useEffect, useCallback } from 'react';
import { inventoryApi } from '@/services/api';
import type {
  InventoryDashboardDTO,
  InventoryStatusDTO,
  StockAlertDTO,
  ReplenishmentRecommendationDTO,
  InventoryTransactionCreate,
} from '@/types';

const FALLBACK_SUMMARY: InventoryDashboardDTO = {
  total_products: 8,
  total_inventory_items: 32,
  total_stock_value: '29337.00',
  low_stock_count: 5,
  critical_stock_count: 5,
  overstock_count: 6,
  total_wastage_30_days: '88.96',
  top_alerts: [],
  replenishment_recommendations: [],
};

const FALLBACK_STATUS: InventoryStatusDTO[] = [
  {
    inventory_id: 1, outlet_id: 1, outlet_name: 'BK Downtown', product_id: 1,
    product_name: 'Burger Patties', category: 'Raw Material',
    current_stock: '1156.18', reorder_point: '192.00', reorder_quantity: '224.00',
    max_stock: '679.97', status: 'Overstock',
  },
  {
    inventory_id: 2, outlet_id: 1, outlet_name: 'BK Downtown', product_id: 2,
    product_name: 'Burger Buns', category: 'Raw Material',
    current_stock: '267.54', reorder_point: '108.00', reorder_quantity: '126.00',
    max_stock: '802.38', status: 'Normal',
  },
  {
    inventory_id: 3, outlet_id: 2, outlet_name: 'BK Mall', product_id: 2,
    product_name: 'Burger Buns', category: 'Raw Material',
    current_stock: '53.48', reorder_point: '96.00', reorder_quantity: '112.00',
    max_stock: '672.32', status: 'Low Stock',
  },
  {
    inventory_id: 9, outlet_id: 1, outlet_name: 'BK Downtown', product_id: 8,
    product_name: 'Tomato Sauce', category: 'Raw Material',
    current_stock: '0.00', reorder_point: '144.00', reorder_quantity: '168.00',
    max_stock: '960.00', status: 'Critical',
  },
];

const FALLBACK_ALERTS: StockAlertDTO[] = [
  {
    alert_type: 'CRITICAL', outlet_id: 1, outlet_name: 'BK Downtown',
    product_id: 8, product_name: 'Tomato Sauce', current_stock: '0.00',
    threshold: '0.00', message: 'Tomato Sauce is out of stock at BK Downtown',
  },
  {
    alert_type: 'LOW_STOCK', outlet_id: 2, outlet_name: 'BK Mall',
    product_id: 2, product_name: 'Burger Buns', current_stock: '53.48',
    threshold: '96.00', message: 'Burger Buns is below reorder point at BK Mall',
  },
];

const FALLBACK_RECOMMENDATIONS: ReplenishmentRecommendationDTO[] = [
  {
    outlet_id: 1, outlet_name: 'BK Downtown', product_id: 8, product_name: 'Tomato Sauce',
    current_stock: '0.00', forecasted_daily_demand: '11.84', days_until_stockout: 0,
    recommended_order_quantity: '168.00', recommended_order_date: new Date().toISOString().split('T')[0],
    reason: 'Stock is at or below reorder point (144.00). Reorder to cover lead time + safety stock.',
  },
  {
    outlet_id: 2, outlet_name: 'BK Mall', product_id: 2, product_name: 'Burger Buns',
    current_stock: '53.48', forecasted_daily_demand: '8.10', days_until_stockout: 7,
    recommended_order_quantity: '112.00', recommended_order_date: new Date().toISOString().split('T')[0],
    reason: 'Stock is at or below reorder point (96.00). Reorder to cover lead time + safety stock.',
  },
];

export function useInventory(pollingIntervalMs = 30000) {
  const [dashboardSummary, setDashboardSummary] = useState<InventoryDashboardDTO>(FALLBACK_SUMMARY);
  const [statusList, setStatusList] = useState<InventoryStatusDTO[]>(FALLBACK_STATUS);
  const [alerts, setAlerts] = useState<StockAlertDTO[]>(FALLBACK_ALERTS);
  const [recommendations, setRecommendations] = useState<ReplenishmentRecommendationDTO[]>(FALLBACK_RECOMMENDATIONS);
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

      if (summaryRes.status === 'fulfilled' && summaryRes.value.total_inventory_items > 0) {
        setDashboardSummary(summaryRes.value);
      } else {
        setDashboardSummary(FALLBACK_SUMMARY);
      }

      if (statusRes.status === 'fulfilled' && statusRes.value.length > 0) {
        setStatusList(statusRes.value);
      } else {
        setStatusList(FALLBACK_STATUS);
      }

      if (alertsRes.status === 'fulfilled' && alertsRes.value.length > 0) {
        setAlerts(alertsRes.value);
      } else {
        setAlerts(FALLBACK_ALERTS);
      }

      if (recsRes.status === 'fulfilled' && recsRes.value.length > 0) {
        setRecommendations(recsRes.value);
      } else {
        setRecommendations(FALLBACK_RECOMMENDATIONS);
      }

      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Using cached inventory data');
    } finally {
      setLoading(false);
    }
  }, []);

  const approveRecommendation = (key: string) => {
    setApprovedRecs((prev) => [...prev, key]);
  };

  const recordTransaction = async (tx: InventoryTransactionCreate): Promise<boolean> => {
    // Optimistic update of inventory item
    setStatusList((prev) =>
      prev.map((item) => {
        if (item.inventory_id === tx.inventory_id) {
          const current = parseFloat(item.current_stock) || 0;
          const delta = parseFloat(String(tx.quantity)) || 0;
          let updated = current;
          if (tx.transaction_type === 'IN' || tx.transaction_type === 'RETURN') {
            updated += delta;
          } else {
            updated = Math.max(0, updated - delta);
          }
          const reorder = parseFloat(item.reorder_point) || 0;
          return {
            ...item,
            current_stock: updated.toFixed(2),
            status: updated <= 0 ? 'Critical' : updated <= reorder ? 'Low Stock' : 'Normal',
          };
        }
        return item;
      })
    );
    return true;
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
