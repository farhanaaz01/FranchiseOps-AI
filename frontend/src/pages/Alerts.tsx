import React, { useState, useMemo } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { KPICard } from '@/components/kpi/KPICard';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { AlertTriangle, AlertOctagon, Info, CheckCircle2, RefreshCw, Eye, Store } from 'lucide-react';
import { useAlerts } from '@/hooks/useAlerts';
import { AlertsFeed, AlertDetailModal } from '@/components/alerts';
import type { UnifiedAlert } from '@/services/api/alertsApi';

export const Alerts: React.FC = () => {
  const { alerts, loading, refresh, acknowledgeAlert } = useAlerts();
  const [selectedAlert, setSelectedAlert] = useState<UnifiedAlert | null>(null);

  const criticalCount = useMemo(
    () => alerts.filter((a) => a.severity === 'critical').length,
    [alerts]
  );
  const highCount = useMemo(
    () => alerts.filter((a) => a.severity === 'high').length,
    [alerts]
  );
  const ackCount = useMemo(
    () => alerts.filter((a) => a.status === 'acknowledged').length,
    [alerts]
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Alerts & Operational Incidents"
        subtitle="Automated threshold breach detections, cross-domain operational signals, and incident response."
        badge={
          <Badge variant={criticalCount > 0 ? 'danger' : 'success'}>
            {criticalCount} Critical Active
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
              Refresh Feed
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => alerts.forEach((a) => acknowledgeAlert(a.id))}
            >
              Acknowledge All
            </Button>
          </div>
        }
      />

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Active Telemetry Incidents"
          value={String(alerts.length)}
          subtext={`${alerts.length - ackCount} pending acknowledgment`}
          status={alerts.length > 0 ? 'risk' : 'healthy'}
          icon={<AlertTriangle className="w-4 h-4 text-[#E8A33D]" />}
        />
        <KPICard
          title="Critical Breaches"
          value={String(criticalCount)}
          subtext="Immediate managerial review required"
          status={criticalCount > 0 ? 'critical' : 'healthy'}
          icon={<AlertOctagon className="w-4 h-4 text-[#D0555A]" />}
        />
        <KPICard
          title="High Severity Warnings"
          value={String(highCount)}
          subtext="Staffing / compliance variances"
          status={highCount > 0 ? 'risk' : 'healthy'}
          icon={<Info className="w-4 h-4 text-[#E8A33D]" />}
        />
        <KPICard
          title="Acknowledged (Session)"
          value={String(ackCount)}
          subtext="Recorded in local audit view"
          status="healthy"
          icon={<CheckCircle2 className="w-4 h-4 text-[#4FAE7C]" />}
        />
      </div>

      {/* Unified Alerts Feed */}
      <AlertsFeed
        alerts={alerts}
        onAcknowledge={acknowledgeAlert}
        onOpenResolve={(alert) => setSelectedAlert(alert)}
      />

      {/* Alert Detail Modal (Section 11) */}
      <AlertDetailModal
        isOpen={Boolean(selectedAlert)}
        onClose={() => setSelectedAlert(null)}
        alert={selectedAlert}
        onAcknowledge={acknowledgeAlert}
      />
    </div>
  );
};
