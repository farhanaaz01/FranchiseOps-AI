import { useState, useEffect, useCallback } from 'react';
import { outletApi, intelligenceApi, workforceApi } from '@/services/api';
import type { OutletResponse, OutletCreate, PipelineOutput, EmployeeResponse } from '@/types';

export interface EnrichedOutlet {
  id: string;
  outlet_id: number;
  name: string;
  location: string;
  status: 'Healthy' | 'At Risk' | 'Critical' | 'Pending';
  healthScore: number;
  revenue: string;
  growth: string;
  riskLevel: 'Low' | 'Medium' | 'High';
  manager: string;
}

export function useOutlets(pollingIntervalMs = 30000) {
  const [outlets, setOutlets] = useState<EnrichedOutlet[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOutlets = useCallback(async () => {
    try {
      const [outletRes, pipelineRes, employeeRes] = await Promise.allSettled([
        outletApi.getAllOutlets(),
        intelligenceApi.getLatest(),
        workforceApi.getEmployees(),
      ]);

      if (outletRes.status !== 'fulfilled' || !outletRes.value?.length) {
        setOutlets([]);
        setError('Failed to fetch outlets from backend.');
        setLoading(false);
        return;
      }

      const rawOutlets: OutletResponse[] = outletRes.value;
      let pipeline: PipelineOutput | null = null;
      if (pipelineRes.status === 'fulfilled' && pipelineRes.value?.kpis?.length) {
        pipeline = pipelineRes.value;
      }

      // Build employee manager map by outlet_id
      const managerMap = new Map<number, string>();
      if (employeeRes.status === 'fulfilled' && Array.isArray(employeeRes.value)) {
        employeeRes.value.forEach((emp: EmployeeResponse) => {
          if (emp.role?.toLowerCase().includes('manager')) {
            managerMap.set(emp.outlet_id, emp.full_name);
          } else if (!managerMap.has(emp.outlet_id)) {
            managerMap.set(emp.outlet_id, emp.full_name);
          }
        });
      }

      // Build lookup maps from pipeline data
      const kpiMap = new Map<string, any>();
      const scoreMap = new Map<string, any>();
      if (pipeline) {
        pipeline.kpis.forEach((k) => kpiMap.set(k.outlet_id, k));
        pipeline.performance_scores.forEach((s) => scoreMap.set(s.outlet_id, s));
      }

      const enriched: EnrichedOutlet[] = rawOutlets.map((item) => {
        const outletKey = `OUT-${String(item.outlet_id).padStart(2, '0')}`;
        const kpi = kpiMap.get(outletKey);
        const perf = scoreMap.get(outletKey);

        const healthScore = perf?.performance_score ?? 0;
        const healthStatus: EnrichedOutlet['status'] = perf
          ? perf.health_status
          : 'Pending';

        const revenue = kpi
          ? `$${Math.round(kpi.avg_daily_revenue * 30).toLocaleString()}`
          : '—';

        const growth = kpi
          ? `${kpi.revenue_growth_pct >= 0 ? '+' : ''}${kpi.revenue_growth_pct.toFixed(1)}%`
          : '—';

        const riskLevel: EnrichedOutlet['riskLevel'] =
          healthScore >= 70 ? 'Low' : healthScore >= 50 ? 'Medium' : 'High';

        const manager = managerMap.get(item.outlet_id) || 'Unassigned';

        return {
          id: outletKey,
          outlet_id: item.outlet_id,
          name: item.outlet_name,
          location: item.location || '—',
          status: healthStatus,
          healthScore,
          revenue,
          growth,
          riskLevel,
          manager,
        };
      });

      setOutlets(enriched);
      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch outlets');
    } finally {
      setLoading(false);
    }
  }, []);

  const createOutlet = async (data: OutletCreate): Promise<boolean> => {
    try {
      await outletApi.createOutlet(data);
      await fetchOutlets();
      return true;
    } catch (err: any) {
      setError(err?.message || 'Failed to create outlet');
      return false;
    }
  };

  useEffect(() => {
    fetchOutlets();
    if (pollingIntervalMs > 0) {
      const interval = setInterval(fetchOutlets, pollingIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchOutlets, pollingIntervalMs]);

  return { outlets, loading, error, refresh: fetchOutlets, createOutlet };
}
