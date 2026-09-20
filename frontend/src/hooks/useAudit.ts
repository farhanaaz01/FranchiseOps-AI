import { useState, useEffect, useCallback } from 'react';
import { auditApi, AuditRecord, ComplianceOutletRecord } from '@/services/api/auditApi';

const FALLBACK_COMPLIANCE: ComplianceOutletRecord[] = [
  {
    outlet_id: 'OUT-02',
    performance_score: 0.0,
    health_status: 'Critical',
    compliance_score: 57.65,
    wastage_rate: 6.1,
    absenteeism_rate: 1.52,
    campaign_roi: -11.11,
    audit_issues: [
      {
        domain: 'Audit', severity: 'high', metric: 'compliance_score',
        value: 57.65, threshold: 75.0,
        finding: 'Audit Agent: compliance 57.6 below threshold (75.0)',
        recommendation: 'Close compliance gaps: retrain on SOPs and schedule a follow-up audit within 7 days.',
      },
    ],
    priority_issue: 'Audit Agent: compliance 57.6 below threshold (75.0)',
    overall_recommendation: 'Close compliance gaps: retrain on SOPs and schedule a follow-up audit within 7 days.',
  },
  {
    outlet_id: 'OUT-05',
    performance_score: 40.6,
    health_status: 'Critical',
    compliance_score: 69.75,
    wastage_rate: 2.91,
    absenteeism_rate: 1.31,
    campaign_roi: 20.55,
    audit_issues: [
      {
        domain: 'Audit', severity: 'high', metric: 'compliance_score',
        value: 69.75, threshold: 75.0,
        finding: 'Audit Agent: compliance 69.8 below threshold (75.0)',
        recommendation: 'Close compliance gaps: retrain on SOPs and schedule a follow-up audit within 7 days.',
      },
    ],
    priority_issue: 'Audit Agent: compliance 69.8 below threshold (75.0)',
    overall_recommendation: 'Close compliance gaps: retrain on SOPs and schedule a follow-up audit within 7 days.',
  },
  {
    outlet_id: 'OUT-03',
    performance_score: 46.8,
    health_status: 'Critical',
    compliance_score: 76.9,
    wastage_rate: 2.44,
    absenteeism_rate: 1.45,
    campaign_roi: 25.01,
    audit_issues: [],
    priority_issue: null,
    overall_recommendation: 'Operations are within acceptable compliance thresholds.',
  },
  {
    outlet_id: 'OUT-04',
    performance_score: 83.8,
    health_status: 'Healthy',
    compliance_score: 85.3,
    wastage_rate: 1.96,
    absenteeism_rate: 0.50,
    campaign_roi: 41.96,
    audit_issues: [],
    priority_issue: null,
    overall_recommendation: 'No critical compliance issues detected. Continue current practices.',
  },
  {
    outlet_id: 'OUT-01',
    performance_score: 99.4,
    health_status: 'Healthy',
    compliance_score: 94.55,
    wastage_rate: 1.48,
    absenteeism_rate: 0.49,
    campaign_roi: 65.12,
    audit_issues: [],
    priority_issue: null,
    overall_recommendation: 'Excellent compliance and operational performance. Benchmark outlet.',
  },
];

export function useAudit() {
  const [audits, setAudits] = useState<AuditRecord[]>([]);
  const [complianceRecords, setComplianceRecords] = useState<ComplianceOutletRecord[]>(FALLBACK_COMPLIANCE);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAudits = useCallback(async () => {
    try {
      const [auditRes, complianceRes] = await Promise.allSettled([
        auditApi.getAudits(),
        auditApi.getComplianceFromIntelligence(),
      ]);

      if (auditRes.status === 'fulfilled') {
        setAudits(auditRes.value);
      }

      if (complianceRes.status === 'fulfilled' && complianceRes.value.length > 0) {
        setComplianceRecords(complianceRes.value);
      } else {
        setComplianceRecords(FALLBACK_COMPLIANCE);
      }

      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Using cached audit data');
    } finally {
      setLoading(false);
    }
  }, []);

  const recordAudit = async (newAudit: Omit<AuditRecord, 'id'>): Promise<AuditRecord> => {
    const created = await auditApi.recordAudit(newAudit);
    setAudits((prev) => [created, ...prev]);
    return created;
  };

  // Computed KPIs from compliance records
  const avgComplianceScore = complianceRecords.length
    ? complianceRecords.reduce((sum, r) => sum + r.compliance_score, 0) / complianceRecords.length
    : 0;

  const openIssues = complianceRecords.reduce((sum, r) => sum + r.audit_issues.length, 0);

  const criticalOutlets = complianceRecords.filter(
    (r) => r.health_status === 'Critical' && r.audit_issues.length > 0
  ).length;

  const outletsBelowThreshold = complianceRecords.filter(
    (r) => r.compliance_score < 75
  ).length;

  useEffect(() => {
    fetchAudits();
  }, [fetchAudits]);

  return {
    audits,
    complianceRecords,
    loading,
    error,
    refresh: fetchAudits,
    recordAudit,
    avgComplianceScore,
    openIssues,
    criticalOutlets,
    outletsBelowThreshold,
  };
}
