import React from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  AlertTriangle,
  Bot,
  Store,
  Clock,
  Layers,
  Sparkles,
  Info,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
} from 'lucide-react';
import type { UnifiedAlert } from '@/services/api/alertsApi';

interface AlertDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  alert: UnifiedAlert | null;
  onAcknowledge?: (id: string) => void;
  onResolve?: (id: string) => void;
}

export const AlertDetailModal: React.FC<AlertDetailModalProps> = ({
  isOpen,
  onClose,
  alert,
  onAcknowledge,
  onResolve,
}) => {
  if (!alert) return null;

  const isCritical = alert.severity === 'critical';
  const isAck = alert.status === 'acknowledged';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Operational Incident Details" size="lg">
      <div className="space-y-5">
        {/* 1. ALERT HEADER */}
        <div className="p-4 rounded-lg bg-[#171A20] border border-[#262B35] space-y-2">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-[#6C8CFF] bg-[#6C8CFF]/10 px-2 py-0.5 rounded">
                {alert.outletId}
              </span>
              <span className="text-xs font-semibold text-[#EDEFF3]">{alert.outletName}</span>
            </div>
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
          </div>
          <h3 className="text-sm font-bold text-[#EDEFF3] leading-snug">{alert.title}</h3>
        </div>

        {/* 2. CONTEXT */}
        <div className="space-y-1.5">
          <span className="text-[10px] font-mono text-[#5C6478] uppercase tracking-wider block font-semibold">
            Telemetry Context
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
            <div className="p-2.5 bg-[#171A20] rounded border border-[#262B35]">
              <span className="text-[10px] text-[#5C6478] block">Source Agent</span>
              <span className="text-[#EDEFF3] truncate block mt-0.5">{alert.sourceAgent}</span>
            </div>
            <div className="p-2.5 bg-[#171A20] rounded border border-[#262B35]">
              <span className="text-[10px] text-[#5C6478] block">Domain Area</span>
              <span className="text-[#6C8CFF] truncate block mt-0.5">{alert.domain}</span>
            </div>
            <div className="p-2.5 bg-[#171A20] rounded border border-[#262B35]">
              <span className="text-[10px] text-[#5C6478] block">Timestamp</span>
              <span className="text-[#8A93A6] truncate block mt-0.5">
                {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            <div className="p-2.5 bg-[#171A20] rounded border border-[#262B35]">
              <span className="text-[10px] text-[#5C6478] block">Incident Status</span>
              <span className="text-[#E8A33D] truncate block mt-0.5 capitalize">{alert.status}</span>
            </div>
          </div>
        </div>

        {/* 3. AFFECTED AREA */}
        <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] text-xs space-y-1">
          <span className="text-[10px] font-mono text-[#5C6478] uppercase tracking-wider block font-semibold">
            Affected Operational Area
          </span>
          <p className="text-[#EDEFF3] font-medium">{alert.affectedArea}</p>
          {alert.metric && (
            <div className="flex items-center gap-3 text-[11px] font-mono text-[#8A93A6] pt-1">
              <span>Metric: <strong className="text-[#EDEFF3]">{alert.metric}</strong></span>
              {alert.value !== null && alert.value !== undefined && (
                <span>Value: <strong className="text-[#D0555A]">{alert.value}</strong></span>
              )}
              {alert.threshold !== null && alert.threshold !== undefined && (
                <span>Threshold Limit: <strong className="text-[#4FAE7C]">{alert.threshold}</strong></span>
              )}
            </div>
          )}
        </div>

        {/* 4. RELATED FINDING */}
        <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] text-xs space-y-1">
          <span className="text-[10px] font-mono text-[#D0555A] uppercase tracking-wider block font-semibold">
            Diagnostic Finding Description
          </span>
          <p className="text-[#EDEFF3] leading-relaxed">{alert.description}</p>
        </div>

        {/* 5. RECOMMENDATION */}
        <div className="p-3.5 bg-[#4FAE7C]/5 border border-[#4FAE7C]/25 rounded-lg text-xs space-y-1">
          <span className="text-[10px] font-mono text-[#4FAE7C] uppercase tracking-wider block font-semibold">
            Prescriptive Recommendation
          </span>
          <p className="text-[#EDEFF3] font-medium leading-relaxed">
            {alert.recommendation || 'Initiate corrective review in the Operational Decision Center.'}
          </p>
        </div>

        {/* 6. STATUS & RESOLUTION NOTICE */}
        <div className="p-3 bg-[#12141A] border border-[#262B35] rounded-lg flex items-start gap-2.5 text-xs">
          <Info className="w-4 h-4 text-[#6C8CFF] shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="text-[11px] font-mono text-[#EDEFF3] font-semibold block">
              Incident Management & Telemetry Status
            </span>
            <p className="text-[11px] text-[#8A93A6]">
              Incidents are tracked in real-time across operational agents. Acknowledging or resolving updates the system telemetry status and synchronizes with corporate audit records.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-[#262B35]">
          <span className="text-[11px] font-mono capitalize text-[#5C6478]">
            Status: <strong className={alert.status === 'resolved' ? 'text-[#4FAE7C]' : isAck ? 'text-[#6C8CFF]' : 'text-[#E8A33D]'}>{alert.status}</strong>
          </span>
          <div className="flex items-center gap-2">
            {!isAck && alert.status !== 'resolved' && onAcknowledge && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  onAcknowledge(alert.id);
                  onClose();
                }}
              >
                Acknowledge
              </Button>
            )}
            {alert.status !== 'resolved' && onResolve && (
              <Button
                variant="outline"
                size="sm"
                className="text-[#4FAE7C] border-[#4FAE7C]/30 hover:bg-[#4FAE7C]/10"
                onClick={() => {
                  onResolve(alert.id);
                  onClose();
                }}
              >
                Resolve Incident
              </Button>
            )}
            <Button variant="primary" size="sm" onClick={onClose}>
              Done
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};
