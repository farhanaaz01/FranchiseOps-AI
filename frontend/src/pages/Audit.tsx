import React, { useState } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { KPICard } from '@/components/kpi/KPICard';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  ShieldCheck, AlertTriangle, CheckCircle, XCircle,
  RefreshCw, Plus, ClipboardList,
} from 'lucide-react';
import { useAudit } from '@/hooks/useAudit';
import { useOutlets } from '@/hooks/useOutlets';
import { AuditScorecard, RecordAuditModal } from '@/components/audit';
import { ComplianceBarChart, WastageRateChart } from '@/components/audit/AuditCharts';
import { ComplianceTable } from '@/components/audit/ComplianceTable';
import { formatPercentAbs } from '@/utils/formatters';

export const Audit: React.FC = () => {
  const {
    audits,
    complianceRecords,
    loading,
    refresh,
    recordAudit,
    avgComplianceScore,
    openIssues,
    criticalOutlets,
    outletsBelowThreshold,
  } = useAudit();
  const { outlets } = useOutlets();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const complianceStatus = avgComplianceScore >= 80 ? 'healthy' : avgComplianceScore >= 65 ? 'risk' : 'critical';

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit & Compliance Control"
        subtitle="HACCP food safety adherence, automated health inspections, and brand standard verification powered by the intelligence pipeline."
        badge={
          <Badge variant={criticalOutlets > 0 ? 'danger' : 'success'}>
            {criticalOutlets > 0 ? `${criticalOutlets} Critical Outlets` : 'HACCP Monitored'}
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={<RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />}
              onClick={refresh}
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={<Plus className="w-3.5 h-3.5" />}
              onClick={() => setIsModalOpen(true)}
            >
              Log Audit Inspection
            </Button>
          </div>
        }
      />

      {/* KPI Cards Row — from intelligence pipeline */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Avg Compliance Score"
          value={`${formatPercentAbs(avgComplianceScore)}`}
          subtext="Across all active outlets"
          status={complianceStatus}
          icon={<ShieldCheck className="w-4 h-4 text-[#4FAE7C]" />}
        />
        <KPICard
          title="Outlets Below Threshold"
          value={String(outletsBelowThreshold)}
          subtext="Compliance < 75% (HACCP threshold)"
          status={outletsBelowThreshold > 0 ? 'critical' : 'healthy'}
          icon={<XCircle className="w-4 h-4 text-[#D0555A]" />}
        />
        <KPICard
          title="Open Compliance Issues"
          value={String(openIssues)}
          subtext="Flagged by intelligence agent"
          status={openIssues > 0 ? 'risk' : 'healthy'}
          icon={<AlertTriangle className="w-4 h-4 text-[#E8A33D]" />}
        />
        <KPICard
          title="Inspection Audits Logged"
          value={String(audits.length)}
          subtext={`${audits.filter((a) => a.status === 'Passed').length} passed · ${audits.filter((a) => a.status === 'Failed').length} failed`}
          status="healthy"
          icon={<CheckCircle className="w-4 h-4 text-[#4FAE7C]" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ComplianceBarChart records={complianceRecords} />
        <WastageRateChart records={complianceRecords} />
      </div>

      {/* Intelligence-powered Compliance Table */}
      <Card>
        <CardHeader separator>
          <div className="flex items-center gap-2">
            <ClipboardList className="w-4 h-4 text-[#6C8CFF]" />
            <CardTitle>Outlet Compliance Intelligence Matrix</CardTitle>
          </div>
          <Badge variant="accent" size="sm">Intelligence Pipeline</Badge>
        </CardHeader>
        <ComplianceTable records={complianceRecords} />
      </Card>

      {/* Manual Inspection Records */}
      <AuditScorecard audits={audits} />

      {/* Record Audit Modal */}
      <RecordAuditModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={recordAudit}
        outlets={outlets}
      />
    </div>
  );
};
