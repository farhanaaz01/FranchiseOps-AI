import { apiGet, apiPost, apiPut, apiDelete } from './apiClient';
import type { OutletResponse, OutletCreate } from '@/types';

export const outletApi = {
  /**
   * Fetch all outlets
   */
  getAllOutlets: (): Promise<OutletResponse[]> => {
    return apiGet<OutletResponse[]>('/api/outlets');
  },

  /**
   * Fetch a single outlet by ID
   */
  getOutletById: (outletId: number | string): Promise<OutletResponse> => {
    return apiGet<OutletResponse>(`/api/outlets/${outletId}`);
  },

  /**
   * Fetch all outlets for a specific franchise
   */
  getOutletsByFranchise: (franchiseId: number | string): Promise<OutletResponse[]> => {
    return apiGet<OutletResponse[]>(`/api/outlets/franchise/${franchiseId}`);
  },

  /**
   * Create an outlet
   */
  createOutlet: (data: OutletCreate): Promise<OutletResponse> => {
    return apiPost<OutletResponse>('/api/outlets', data);
  },

  /**
   * Update an outlet
   */
  updateOutlet: (outletId: number | string, data: OutletCreate): Promise<OutletResponse> => {
    return apiPut<OutletResponse>(`/api/outlets/${outletId}`, data);
  },

  /**
   * Delete an outlet
   */
  deleteOutlet: (outletId: number | string): Promise<void> => {
    return apiDelete<void>(`/api/outlets/${outletId}`);
  },
};
