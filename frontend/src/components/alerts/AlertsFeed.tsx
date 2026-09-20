import React, { useState, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  AlertTriangle,
  AlertCircle,
  Package,
  Users,
  ShieldCheck,
  CheckCircle2,
  Eye,
  Filter,
  Bot,
  Info,
} from 'lucide-react';
import type { UnifiedAlert } from '@/services/api/alertsApi';

interface AlertsFeedProps {
  alerts: UnifiedAlert[];
  onAcknowledge: (id: string) => void;
  onOpenResolve: (alert: UnifiedAlert) => void;
}

export const AlertsFeed: React.FC<AlertsFeedProps> = ({
  alerts,
  onAcknowledge,
  onOpenResolve,
}) => {
  const [selectedDomain, setSelectedDomain] = useState<string>('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedOutlet, setSelectedOutlet] = useState<string>('ALL');

  // Unique outlets for dropdown
  const outletOptions = useMemo(() => {
    const set = new Set<string>();
    alerts.forEach((a) => {
      if (a.outletId) set.add(a.outletId);
    });
    return Array.from(set).sort();
  }, [alerts]);

  const filtered = useMemo(() => {
    return alerts.filter((a) => {
      if (selectedDomain !== 'ALL' && a.domain.toUpperCase() !== selectedDomain) return false;
      if (selectedSeverity !== 'ALL' && a.severity.toUpperCase() !== selectedSeverity) return false;
      if (selectedStatus !== 'ALL' && a.status.toUpperCase() !== selectedStatus) return false;
      if (selectedOutlet !== 'ALL' && a.outletId !== selectedOutlet) return false;
      return true;
    });
  }, [alerts, selectedDomain, selectedSeverity, selectedStatus, selectedOutlet]);

  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'Inventory':
        return <Package className="w-4 h-4 text-[#6C8CFF]" />;
      case 'Workforce':
        return <Users className="w-4 h-4 text-[#E8A33D]" />;
      case 'Audit':
        return <ShieldCheck className="w-4 h-4 text-[#4FAE7C]" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-[#D0555A]" />;
    }
  };

  return (
    <Card>
      <CardHeader separator>
        <div className="space-y-3 w-full">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-[#D0555A]" />
              <CardTitle>Cross-Domain Operational Incidents</CardTitle>
            </div>
            <span className="text-xs font-mono text-[#8A93A6]">
              Showing {filtered.length} of {alerts.length} incidents
            </span>
          </div>

          {/* Filters Bar: Domain, Severity, Status, Outlet */}
          <div className="flex items-center justify-between gap-3 flex-wrap pt-1 text-xs">
            {/* Domain Tabs */}
            <div className="flex items-center gap-1 flex-wrap text-[11px] font-mono">
              {['ALL', 'INVENTORY', 'WORKFORCE', 'AUDIT', 'PERFORMANCE'].map((domain) => (
                <button
                  key={domain}
                  onClick={() => setSelectedDomain(domain)}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    selectedDomain === domain
                      ? 'bg-[#6C8CFF] text-[#FFFFFF]'
                      : 'bg-[#171A20] text-[#8A93A6] hover:text-[#EDEFF3] border border-[#262B35]'
                  }`}
                >
                  {domain}
                </button>
              ))}
            </div>

            {/* Severity, Status & Outlet Dropdowns */}
            <div className="flex items-center gap-2 flex-wrap text-[11px] font-mono">
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="bg-[#171A20] text-[#EDEFF3] border border-[#262B35] rounded-md px-2 py-1 focus:outline-hidden"
              >
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>

              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="bg-[#171A20] text-[#EDEFF3] border border-[#262B35] rounded-md px-2 py-1 focus:outline-hidden"
              >
                <option value="ALL">All Statuses</option>
                <option value="ACTIVE">Active</option>
                <option value="ACKNOWLEDGED">Acknowledged</option>
              </select>

              {outletOptions.length > 0 && (
                <select
                  value={selectedOutlet}
                  onChange={(e) => setSelectedOutlet(e.target.value)}
                  className="bg-[#171A20] text-[#EDEFF3] border border-[#262B35] rounded-md px-2 py-1 focus:outline-hidden"
                >
                  <option value="ALL">All Outlets</option>
                  {outletOptions.map((oid) => (
                    <option key={oid} value={oid}>
                      {oid}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        {filtered.length === 0 ? (
          <div className="py-12 text-center text-xs text-[#5C6478]">
            No operational incidents found matching selected filter criteria.
          </div>
        ) : (
          filtered.map((alert) => {
            const isCritical = alert.severity === 'critical';
            const isAck = alert.status === 'acknowledged';

            return (
              <div
                key={alert.id}
                className={`p-3.5 rounded-lg border transition-all ${
                  isCritical
                    ? 'bg-[#D0555A]/5 border-[#D0555A]/30'
                    : 'bg-[#171A20] border-[#262B35]'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-[#1D212A] border border-[#262B35] mt-0.5">
                      {getDomainIcon(alert.domain)}
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-semibold text-[#EDEFF3]">{alert.title}</span>
                        <span className="text-[10px] font-mono text-[#6C8CFF] bg-[#6C8CFF]/10 px-1.5 py-0.5 rounded">
                          {alert.outletName || alert.outletId}
                        </span>
                        <Badge
                          variant={
                            alert.severity === 'critical'
                              ? 'danger'
                              : alert.severity === 'high'
                              ? 'warning'
                              : 'neutral'
                          }
                        >
                          {alert.severity.toUpperCase()}
                        </Badge>
                        <span className="text-[10px] text-[#5C6478] font-mono">
                          {alert.domain} Agent
                        </span>
                        {isAck && (
                          <span className="text-[10px] font-mono text-[#4FAE7C] bg-[#4FAE7C]/10 px-1.5 py-0.5 rounded border border-[#4FAE7C]/20">
                            ACK
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[#8A93A6]">{alert.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                    {!isAck && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onAcknowledge(alert.id)}
                        icon={<Eye className="w-3 h-3 text-[#8A93A6]" />}
                        className="text-xs"
                      >
                        Ack
                      </Button>
                    )}
                    <Button
                      variant={isCritical ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => onOpenResolve(alert)}
                      className="text-xs"
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
};
