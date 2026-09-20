import React from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  Activity,
  Server,
  Cpu,
  Layers,
  Clock,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Info,
} from 'lucide-react';
import { useSystemHealth } from '@/hooks/useSystemHealth';

interface SystemHealthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SystemHealthModal: React.FC<SystemHealthModalProps> = ({ isOpen, onClose }) => {
  const {
    frontendStatus,
    apiGatewayStatus,
    pipelineStatus,
    lastSyncTime,
    modelVersion,
    outletCount,
    apiBaseUrl,
    checking,
    refreshHealth,
  } = useSystemHealth();

  if (!isOpen) return null;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Connected':
      case 'Available':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-[#4FAE7C] bg-[#4FAE7C]/10 px-2 py-0.5 rounded border border-[#4FAE7C]/30">
            <CheckCircle2 className="w-3 h-3" /> {status}
          </span>
        );
      case 'Checking':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-[#6C8CFF] bg-[#6C8CFF]/10 px-2 py-0.5 rounded border border-[#6C8CFF]/30">
            <RefreshCw className="w-3 h-3 animate-spin" /> Checking
          </span>
        );
      case 'Unavailable':
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-[#D0555A] bg-[#D0555A]/10 px-2 py-0.5 rounded border border-[#D0555A]/30">
            <AlertCircle className="w-3 h-3" /> {status}
          </span>
        );
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Subsystem Health & Telemetry" size="md">
      <div className="space-y-4">
        {/* Header telemetry summary */}
        <div className="p-3.5 bg-[#171A20] rounded-lg border border-[#262B35] space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-[#EDEFF3]">
              Enterprise Platform Subsystems
            </span>
            <span className="text-[10px] font-mono text-[#5C6478]">
              {outletCount} Stores Monitored
            </span>
          </div>
          <p className="text-[11px] text-[#8A93A6]">
            Verifiable status checks across the frontend runtime, FastAPI backend gateway, and ML intelligence pipeline.
          </p>
        </div>

        {/* Subsystems List */}
        <div className="space-y-2 text-xs">
          {/* 1. Frontend Runtime */}
          <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Layers className="w-4 h-4 text-[#6C8CFF]" />
              <div>
                <span className="font-semibold text-[#EDEFF3] block">Frontend Client</span>
                <span className="text-[10px] text-[#5C6478] font-mono">React 18 • Vite v6</span>
              </div>
            </div>
            {getStatusBadge(frontendStatus)}
          </div>

          {/* 2. FastAPI Gateway */}
          <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Server className="w-4 h-4 text-[#E8A33D]" />
              <div>
                <span className="font-semibold text-[#EDEFF3] block">FastAPI Backend Gateway</span>
                <span className="text-[10px] text-[#5C6478] font-mono">{apiBaseUrl}</span>
              </div>
            </div>
            {getStatusBadge(apiGatewayStatus)}
          </div>

          {/* 3. ML Intelligence Pipeline */}
          <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Cpu className="w-4 h-4 text-[#9D7BFF]" />
              <div>
                <span className="font-semibold text-[#EDEFF3] block">Intelligence Pipeline</span>
                <span className="text-[10px] text-[#5C6478] font-mono">{modelVersion}</span>
              </div>
            </div>
            {getStatusBadge(pipelineStatus)}
          </div>

          {/* 4. Last Synchronization */}
          <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Clock className="w-4 h-4 text-[#4FAE7C]" />
              <div>
                <span className="font-semibold text-[#EDEFF3] block">Last Synchronized</span>
                <span className="text-[10px] text-[#5C6478] font-mono">Telemetry Freshness</span>
              </div>
            </div>
            <span className="text-[11px] font-mono font-semibold text-[#EDEFF3]">
              {lastSyncTime}
            </span>
          </div>
        </div>

        {/* Honest Disclosure notice */}
        <div className="p-3 bg-[#12141A] border border-[#262B35] rounded-lg flex items-start gap-2 text-xs text-[#5C6478]">
          <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <span>
            Database connection is verified via FastAPI endpoint responses. Direct database socket telemetry is omitted to uphold enterprise data isolation.
          </span>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-[#262B35]">
          <Button
            variant="outline"
            size="sm"
            loading={checking}
            icon={<RefreshCw className={`w-3.5 h-3.5 ${checking ? 'animate-spin' : ''}`} />}
            onClick={refreshHealth}
          >
            {checking ? 'Pinging Gateway...' : 'Ping Gateway'}
          </Button>
          <Button variant="primary" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
};
