import { apiGet } from './apiClient';
import type {
  DashboardSummaryDTO,
  FranchiseComparisonDTO,
  OutletPerformanceDTO,
  UnderperformingOutletDTO,
} from '@/types';

function buildQuery(startDate?: string | null, endDate?: string | null): string {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const q = params.toString();
  return q ? `?${q}` : '';
}

export const dashboardApi = {
  /**
   * Fetch executive summary across all outlets
   */
  getSummary: (startDate?: string | null, endDate?: string | null): Promise<DashboardSummaryDTO> => {
    return apiGet<DashboardSummaryDTO>(`/api/dashboard/summary${buildQuery(startDate, endDate)}`);
  },

  /**
   * Fetch underperforming outlets (revenue < 70% of franchise average)
   */
  getUnderperforming: (startDate?: string | null, endDate?: string | null): Promise<UnderperformingOutletDTO[]> => {
    return apiGet<UnderperformingOutletDTO[]>(`/api/dashboard/underperforming${buildQuery(startDate, endDate)}`);
  },

  /**
   * Fetch individual outlet performance with daily revenue trend
   */
  getOutletPerformance: (
    outletId: number | string,
    startDate?: string | null,
    endDate?: string | null
  ): Promise<OutletPerformanceDTO> => {
    return apiGet<OutletPerformanceDTO>(`/api/dashboard/outlets/${outletId}${buildQuery(startDate, endDate)}`);
  },

  /**
   * Compare outlets within a specific franchise
   */
  compareFranchiseOutlets: (
    franchiseId: number | string,
    startDate?: string | null,
    endDate?: string | null
  ): Promise<FranchiseComparisonDTO[]> => {
    return apiGet<FranchiseComparisonDTO[]>(
      `/api/dashboard/franchises/${franchiseId}/compare${buildQuery(startDate, endDate)}`
    );
  },
};
