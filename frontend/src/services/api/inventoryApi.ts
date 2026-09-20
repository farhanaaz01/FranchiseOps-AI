import { apiGet } from './apiClient';
import type {
  InventoryDashboardDTO,
  InventoryStatusDTO,
  StockAlertDTO,
  ReplenishmentRecommendationDTO,
  DemandForecastDTO,
} from '@/types';

export const inventoryApi = {
  /**
   * Fetch inventory dashboard summary
   */
  getDashboardSummary: (): Promise<InventoryDashboardDTO> => {
    return apiGet<InventoryDashboardDTO>('/api/inventory/dashboard/summary');
  },

  /**
   * Fetch inventory status across all outlets
   */
  getStatus: (): Promise<InventoryStatusDTO[]> => {
    return apiGet<InventoryStatusDTO[]>('/api/inventory/dashboard/status');
  },

  /**
   * Fetch stock alerts (LOW_STOCK, CRITICAL, OVERSTOCK)
   */
  getAlerts: (): Promise<StockAlertDTO[]> => {
    return apiGet<StockAlertDTO[]>('/api/inventory/dashboard/alerts');
  },

  /**
   * Fetch automated replenishment recommendations
   */
  getReplenishmentRecommendations: (): Promise<ReplenishmentRecommendationDTO[]> => {
    return apiGet<ReplenishmentRecommendationDTO[]>('/api/inventory/dashboard/replenishment');
  },

  /**
   * Fetch demand forecast for an outlet and product
   */
  getDemandForecast: (outletId: number | string, productId: number | string): Promise<DemandForecastDTO> => {
    return apiGet<DemandForecastDTO>(`/api/inventory/dashboard/forecast/${outletId}/${productId}`);
  },
};
