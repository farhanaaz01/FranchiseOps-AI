import { useState, useEffect, useCallback } from 'react';
import { useIntelligence } from './useIntelligence';

export type SubsystemStatus = 'Connected' | 'Available' | 'Unavailable' | 'Checking';

export interface SystemHealthInfo {
  overallStatus: 'online' | 'degraded' | 'offline';
  frontendStatus: SubsystemStatus;
  apiGatewayStatus: SubsystemStatus;
  pipelineStatus: SubsystemStatus;
  latencyMs: number | null;
  lastSyncTime: string;
  modelVersion: string;
  outletCount: number;
  apiBaseUrl: string;
  checking: boolean;
  refetch: () => Promise<void>;
  refreshHealth: () => Promise<void>;
}

export function useSystemHealth(): SystemHealthInfo {
  const { pipelineData } = useIntelligence();
  const [apiGatewayStatus, setApiGatewayStatus] = useState<SubsystemStatus>('Checking');
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [checking, setChecking] = useState<boolean>(false);

  const apiBaseUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

  const checkGateway = useCallback(async () => {
    setChecking(true);
    const start = performance.now();
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);

      const res = await fetch(`${apiBaseUrl}/`, {
        method: 'GET',
        signal: controller.signal,
      }).catch(() => null);

      clearTimeout(timeoutId);
      const elapsed = Math.round(performance.now() - start);

      if (res && (res.ok || res.status === 200)) {
        setApiGatewayStatus('Connected');
        setLatencyMs(elapsed);
      } else {
        setApiGatewayStatus('Unavailable');
        setLatencyMs(null);
      }
    } catch {
      setApiGatewayStatus('Unavailable');
      setLatencyMs(null);
    } finally {
      setChecking(false);
    }
  }, [apiBaseUrl]);

  useEffect(() => {
    checkGateway();
    const interval = setInterval(checkGateway, 45000);
    return () => clearInterval(interval);
  }, [checkGateway]);

  const lastSyncTime = pipelineData.generated_at
    ? new Date(pipelineData.generated_at).toLocaleString([], {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : 'Update time unavailable';

  const isPipelineAvailable = pipelineData.kpis && pipelineData.kpis.length > 0;
  const isGatewayConnected = apiGatewayStatus === 'Connected';

  const overallStatus: 'online' | 'degraded' | 'offline' =
    isGatewayConnected && isPipelineAvailable
      ? 'online'
      : isGatewayConnected || isPipelineAvailable
      ? 'degraded'
      : 'offline';

  return {
    overallStatus,
    frontendStatus: 'Connected',
    apiGatewayStatus,
    pipelineStatus: isPipelineAvailable ? 'Available' : 'Unavailable',
    latencyMs,
    lastSyncTime,
    modelVersion: 'xgb-v1 (Multi-Unit Regressor)',
    outletCount: pipelineData.outlet_count || 5,
    apiBaseUrl,
    checking,
    refetch: checkGateway,
    refreshHealth: checkGateway,
  };
}
