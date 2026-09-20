import { apiGet } from './apiClient';
import type { PipelineOutput, OutletKPI, RootCauseFinding } from '@/types';

// ---- Derived Audit Record based on intelligence pipeline data ----
export interface ComplianceOutletRecord {
  outlet_id: string;
  performance_score: number;
  health_status: 'Healthy' | 'At Risk' | 'Critical';
  compliance_score: number;
  wastage_rate: number;
  absenteeism_rate: number;
  campaign_roi: number;
  audit_issues: AuditIssue[];
  priority_issue: string | null;
  overall_recommendation: string;
}

export interface AuditIssue {
  domain: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  metric: string;
  value: number | null;
  threshold: number | null;
  finding: string;
  recommendation: string;
}

// ---- Legacy in-memory audit records for manual inspections ----
export interface AuditRecord {
  id: string;
  outletId: string;
  outletName: string;
  inspectionDate: string;
  auditorName: string;
  score: number;
  status: 'Passed' | 'Warning' | 'Failed';
  criticalViolations: number;
  minorViolations: number;
  notes: string;
}

const DEFAULT_AUDITS: AuditRecord[] = [
  {
    id: 'AUD-901',
    outletId: 'OUT-01',
    outletName: 'BK Downtown',
    inspectionDate: '2026-09-15',
    auditorName: 'Health Inspector Alvarez',
    score: 96.5,
    status: 'Passed',
    criticalViolations: 0,
    minorViolations: 1,
    notes: 'Impeccable cleanliness. Trace log thermometers verified within 0.1°F calibration.',
  },
  {
    id: 'AUD-902',
    outletId: 'OUT-04',
    outletName: 'BK Mall Annex',
    inspectionDate: '2026-09-12',
    auditorName: 'Corporate Compliance Lead Chen',
    score: 88.0,
    status: 'Passed',
    criticalViolations: 0,
    minorViolations: 2,
    notes: 'Secondary sanitization station was low on test strips. Refilled on site.',
  },
  {
    id: 'AUD-903',
    outletId: 'OUT-03',
    outletName: 'Subway City Center',
    inspectionDate: '2026-09-08',
    auditorName: 'Health Inspector Alvarez',
    score: 76.5,
    status: 'Warning',
    criticalViolations: 1,
    minorViolations: 3,
    notes: 'Handwashing sink temp below standard (95°F vs 100°F). Plumbing contractor dispatched.',
  },
  {
    id: 'AUD-904',
    outletId: 'OUT-02',
    outletName: 'BK Mall',
    inspectionDate: '2026-09-04',
    auditorName: 'Regional Auditor Novak',
    score: 64.0,
    status: 'Failed',
    criticalViolations: 2,
    minorViolations: 4,
    notes: 'Refrigeration unit door gasket damaged; ambient temp spiked to 43°F. Stock discarded.',
  },
];

let inMemoryAudits = [...DEFAULT_AUDITS];

export const auditApi = {
  /**
   * Fetch manual inspection records (in-memory for now, can be extended to backend).
   */
  getAudits: async (): Promise<AuditRecord[]> => {
    return [...inMemoryAudits];
  },

  /**
   * Record a new manual audit inspection.
   */
  recordAudit: async (newAudit: Omit<AuditRecord, 'id'>): Promise<AuditRecord> => {
    const record: AuditRecord = {
      ...newAudit,
      id: `AUD-${Math.floor(1000 + Math.random() * 9000)}`,
    };
    inMemoryAudits.unshift(record);
    return record;
  },

  /**
   * Fetch per-outlet compliance data from the intelligence pipeline.
   * This is the authoritative source for compliance scores and audit issues.
   */
  getComplianceFromIntelligence: async (): Promise<ComplianceOutletRecord[]> => {
    const pipeline = await apiGet<PipelineOutput>('/api/intelligence/latest');
    const kpiMap = new Map<string, OutletKPI>();
    (pipeline.kpis || []).forEach((k: OutletKPI) => kpiMap.set(k.outlet_id, k));

    const rootCauseMap = new Map<string, RootCauseFinding>();
    (pipeline.root_causes || []).forEach((r: RootCauseFinding) => rootCauseMap.set(r.outlet_id, r));

    const scoreMap = new Map<string, { score: number; health_status: string }>();
    (pipeline.performance_scores || []).forEach((ps: any) =>
      scoreMap.set(ps.outlet_id, { score: ps.performance_score, health_status: ps.health_status })
    );

    const records: ComplianceOutletRecord[] = [];
    kpiMap.forEach((kpi, outlet_id) => {
      const rootCause = rootCauseMap.get(outlet_id);
      const perf = scoreMap.get(outlet_id);

      const auditIssues: AuditIssue[] = (rootCause?.issues || [])
        .filter((issue: any) => issue.domain === 'Audit' || issue.metric === 'compliance_score')
        .map((issue: any) => ({
          domain: issue.domain,
          severity: issue.severity,
          metric: issue.metric,
          value: issue.value,
          threshold: issue.threshold,
          finding: issue.finding,
          recommendation: issue.recommendation,
        }));

      records.push({
        outlet_id,
        performance_score: perf?.score ?? 0,
        health_status: (perf?.health_status ?? 'Critical') as 'Healthy' | 'At Risk' | 'Critical',
        compliance_score: kpi.compliance_score,
        wastage_rate: kpi.wastage_rate,
        absenteeism_rate: kpi.absenteeism_rate,
        campaign_roi: kpi.campaign_roi,
        audit_issues: auditIssues,
        priority_issue: rootCause?.priority_issue ?? null,
        overall_recommendation: rootCause?.overall_recommendation ?? '',
      });
    });

    return records.sort((a, b) => a.compliance_score - b.compliance_score);
  },
};
