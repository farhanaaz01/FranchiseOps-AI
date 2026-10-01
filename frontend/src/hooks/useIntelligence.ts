import { useState, useEffect, useCallback } from 'react';
import { intelligenceApi } from '@/services/api';
import type {
  PipelineOutput,
  ForecastResult,
  RootCauseFinding,
  RiskPrediction,
  RiskFeatureImportance,
} from '@/types';

const EMPTY_PIPELINE: PipelineOutput = {
  generated_at: '',
  outlet_count: 0,
  kpis: [],
  performance_scores: [],
  forecasts: [],
  risk_predictions: [],
  feature_importances: [],
  root_causes: [],
};

export function useIntelligence(pollingIntervalMs = 30000) {
  const [pipelineData, setPipelineData] = useState<PipelineOutput>(EMPTY_PIPELINE);
  const [loading, setLoading] = useState<boolean>(true);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchIntelligence = useCallback(async () => {
    try {
      const res = await intelligenceApi.getLatest();
      if (res && res.kpis && res.kpis.length > 0) {
        setPipelineData(res);
        setError(null);
      } else {
        setPipelineData(EMPTY_PIPELINE);
        setError('Pipeline returned no data. Run the intelligence pipeline to generate results.');
      }
    } catch (err: any) {
      setPipelineData(EMPTY_PIPELINE);
      setError(err?.message || 'Failed to fetch intelligence data. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  const triggerPipeline = async (): Promise<boolean> => {
    setIsRunning(true);
    setError(null);
    try {
      const updated = await intelligenceApi.runPipeline();
      if (updated && updated.kpis) {
        setPipelineData(updated);
      }
      return true;
    } catch (err: any) {
      setError(err?.message || 'Failed to trigger pipeline recalculation');
      return false;
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    fetchIntelligence();
    if (pollingIntervalMs > 0) {
      const interval = setInterval(fetchIntelligence, pollingIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchIntelligence, pollingIntervalMs]);

  return {
    pipelineData,
    forecasts: pipelineData.forecasts,
    rootCauses: pipelineData.root_causes,
    riskPredictions: pipelineData.risk_predictions,
    featureImportances: pipelineData.feature_importances,
    loading,
    isRunning,
    error,
    refresh: fetchIntelligence,
    triggerPipeline,
  };
}
