import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Sparkles, ArrowRight, ShieldAlert, CheckCircle2, Clock, Bot, AlertCircle } from 'lucide-react';

export interface RecommendationCardProps {
  title: string;
  reason: string;
  affectedOutlet: string;
  impact: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  sourceAgent?: string;
  status?: 'New' | 'Acknowledged' | 'In Progress' | 'Resolved';
  actionAvailable?: boolean;
  actionLabel?: string;
  onActionClick?: () => void;
  monitoringNote?: string;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  title,
  reason,
  affectedOutlet,
  impact,
  severity = 'medium',
  sourceAgent = 'Intelligence Engine',
  status = 'New',
  actionAvailable = false,
  actionLabel = 'Review Action',
  onActionClick,
  monitoringNote,
}) => {
  const getSeverityBadge = () => {
    switch (severity) {
      case 'critical':
        return <Badge variant="danger">CRITICAL</Badge>;
      case 'high':
        return <Badge variant="warning">HIGH</Badge>;
      case 'medium':
        return <Badge variant="accent">MEDIUM</Badge>;
      case 'low':
      default:
        return <Badge variant="neutral">LOW</Badge>;
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'Resolved':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#4FAE7C] bg-[#4FAE7C]/10 px-2 py-0.5 rounded border border-[#4FAE7C]/20">
            <CheckCircle2 className="w-3 h-3" /> Resolved
          </span>
        );
      case 'In Progress':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#6C8CFF] bg-[#6C8CFF]/10 px-2 py-0.5 rounded border border-[#6C8CFF]/20">
            <Clock className="w-3 h-3" /> In Progress
          </span>
        );
      case 'Acknowledged':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#E8A33D] bg-[#E8A33D]/10 px-2 py-0.5 rounded border border-[#E8A33D]/20">
            <AlertCircle className="w-3 h-3" /> Acknowledged
          </span>
        );
      case 'New':
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#8A93A6] bg-[#171A20] px-2 py-0.5 rounded border border-[#262B35]">
            <Sparkles className="w-3 h-3 text-[#6C8CFF]" /> New
          </span>
        );
    }
  };

  return (
    <Card className="hover:border-[#3A4155] transition-all">
      <CardContent className="p-4 space-y-3">
        {/* Header: Outlet + Agent + Badges */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono font-bold text-[#6C8CFF] bg-[#6C8CFF]/10 px-2 py-0.5 rounded">
              {affectedOutlet}
            </span>
            <div className="flex items-center gap-1 text-[11px] font-mono text-[#8A93A6]">
              <Bot className="w-3.5 h-3.5 text-[#8A93A6]" />
              <span>{sourceAgent}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {getSeverityBadge()}
            {getStatusBadge()}
          </div>
        </div>

        {/* Title */}
        <h4 className="text-sm font-semibold text-[#EDEFF3] leading-snug">{title}</h4>

        {/* Reason / Underlying telemetry */}
        <div className="p-2.5 rounded-lg bg-[#171A20] border border-[#262B35] text-xs space-y-1">
          <span className="text-[10px] font-mono text-[#5C6478] uppercase tracking-wider block">
            Observed Diagnostic Trigger
          </span>
          <p className="text-[#8A93A6] leading-relaxed">{reason}</p>
        </div>

        {/* Impact & Prescriptive Direction */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
          <div className="p-2.5 rounded-lg bg-[#171A20] border border-[#262B35]">
            <span className="text-[10px] font-mono text-[#D0555A] uppercase tracking-wider block font-semibold">
              Operational Impact
            </span>
            <p className="text-[#EDEFF3] mt-0.5 font-medium">{impact}</p>
          </div>
          <div className="p-2.5 rounded-lg bg-[#171A20] border border-[#262B35]">
            <span className="text-[10px] font-mono text-[#6C8CFF] uppercase tracking-wider block font-semibold">
              Prescriptive Directive
            </span>
            <p className="text-[#EDEFF3] mt-0.5 font-medium">{title}</p>
          </div>
        </div>

        {/* Monitoring Note */}
        {monitoringNote && (
          <div className="text-[11px] font-mono text-[#5C6478] flex items-center gap-1.5 pt-1 border-t border-[#262B35]">
            <Clock className="w-3 h-3" />
            <span>Verification: {monitoringNote}</span>
          </div>
        )}

        {/* Action Availability Bar */}
        <div className="flex items-center justify-between pt-1 border-t border-[#262B35] text-xs">
          <span className="text-[10px] font-mono text-[#5C6478]">
            {actionAvailable ? 'Interactive Workflow' : 'Action workflow not connected (Read-only recommendation)'}
          </span>
          {actionAvailable ? (
            <button
              onClick={onActionClick}
              className="px-2.5 py-1 rounded bg-[#6C8CFF] text-white hover:bg-[#5A7AE6] transition-colors text-xs font-medium inline-flex items-center gap-1"
            >
              <span>{actionLabel}</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          ) : (
            <span className="text-[11px] font-mono text-[#5C6478] px-2 py-0.5 rounded bg-[#171A20] border border-[#262B35]">
              Read-only
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
