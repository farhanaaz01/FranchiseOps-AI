import { useState, useEffect, useCallback } from 'react';
import { auditApi, ComplianceOutletRecord } from '@/services/api/auditApi';
import { apiGet, apiPost } from '@/services/api/apiClient';

// Backend audit inspection record mapped from AuditInspectionResponse
export interface AuditRecord {
  id: string;
  audit_id: number;
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

// Backend response shape from /api/audits/inspections
interface BackendInspection {
  audit_id: number;
  outlet_id: number;
  outlet_name?: string | null;
  inspection_date: string;
  auditor_name: string;
  score: string | number;
  status: string;
  critical_violations: number;
  minor_violations: number;
  notes?: string | null;
}

function mapInspection(item: BackendInspection): AuditRecord {
  return {
    id: `AUD-${item.audit_id}`,
    audit_id: item.audit_id,
    outletId: `OUT-${String(item.outlet_id).padStart(2, '0')}`,
    outletName: item.outlet_name || `Outlet #${item.outlet_id}`,
    inspectionDate: item.inspection_date,
    auditorName: item.auditor_name,
    score: typeof item.score === 'string' ? parseFloat(item.score) : item.score,
    status: item.status as 'Passed' | 'Warning' | 'Failed',
    criticalViolations: item.critical_violations,
    minorViolations: item.minor_violations,
    notes: item.notes || '',
  };
}

export function useAudit() {
  const [audits, setAudits] = useState<AuditRecord[]>([]);
  const [complianceRecords, setComplianceRecords] = useState<ComplianceOutletRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAudits = useCallback(async () => {
    try {
      const [inspectionsRes, complianceRes] = await Promise.allSettled([
        apiGet<BackendInspection[]>('/api/audits/inspections'),
        auditApi.getComplianceFromIntelligence(),
      ]);

      if (inspectionsRes.status === 'fulfilled') {
        setAudits(inspectionsRes.value.map(mapInspection));
      } else {
        setAudits([]);
      }

      if (complianceRes.status === 'fulfilled' && complianceRes.value.length > 0) {
        setComplianceRecords(complianceRes.value);
      } else {
        setComplianceRecords([]);
      }

      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch audit data');
    } finally {
      setLoading(false);
    }
  }, []);

  const recordAudit = async (
    newAudit: Omit<AuditRecord, 'id' | 'audit_id'>
  ): Promise<AuditRecord> => {
    // Extract numeric outlet_id from "OUT-01" format
    const outletIdNum = parseInt(newAudit.outletId.replace(/\D/g, ''), 10) || 1;

    const backendPayload = {
      outlet_id: outletIdNum,
      inspection_date: newAudit.inspectionDate,
      auditor_name: newAudit.auditorName,
      score: newAudit.score,
      status: newAudit.status,
      critical_violations: newAudit.criticalViolations,
      minor_violations: newAudit.minorViolations,
      notes: newAudit.notes || null,
    };

    const created = await apiPost<BackendInspection>(
      '/api/audits/inspections',
      backendPayload
    );

    const mapped = mapInspection(created);
    setAudits((prev) => [mapped, ...prev]);
    return mapped;
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
