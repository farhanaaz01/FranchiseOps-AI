import { apiGet, apiPost } from './apiClient';
import type { PipelineOutput, RootCauseFinding, ForecastResult } from '@/types';

export const intelligenceApi = {
  /**
   * Fetch the latest computed intelligence pipeline output.
   */
  getLatest: (): Promise<PipelineOutput> => {
    return apiGet<PipelineOutput>('/api/intelligence/latest');
  },

  /**
   * Trigger on-demand recalculation of the Franchise Intelligence Pipeline.
   */
  runPipeline: (): Promise<PipelineOutput> => {
    return apiPost<PipelineOutput>('/api/intelligence/run', {});
  },

  /**
   * Fetch root-cause findings and AI recommendations.
   */
  getRootCauses: (outletId?: string): Promise<RootCauseFinding[]> => {
    const q = outletId ? `?outlet_id=${encodeURIComponent(outletId)}` : '';
    return apiGet<RootCauseFinding[]>(`/api/intelligence/root-causes${q}`);
  },

  /**
   * Fetch 7-day revenue forecasts from XGBoost.
   */
  getForecasts: (outletId?: string): Promise<ForecastResult[]> => {
    const q = outletId ? `?outlet_id=${encodeURIComponent(outletId)}` : '';
    return apiGet<ForecastResult[]>(`/api/intelligence/forecasts${q}`);
  },
};
