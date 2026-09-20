import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Badge } from '@/components/ui/Badge';
import {
  Sparkles,
  AlertTriangle,
  ArrowDown,
  ShieldAlert,
  Activity,
  Layers,
  CheckCircle2,
  Clock,
  Filter,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import type { RootCauseFinding } from '@/types';

interface RootCauseRecommendationCardProps {
  findings: RootCauseFinding[];
}

export const RootCauseRecommendationCard: React.FC<RootCauseRecommendationCardProps> = ({
  findings,
}) => {
  const [selectedOutlet, setSelectedOutlet] = useState<string>('ALL');
  const [expandedOutlet, setExpandedOutlet] = useState<Record<string, boolean>>({});

  const filteredFindings = findings.filter((f) => {
    if (selectedOutlet === 'ALL') return true;
    return f.outlet_id === selectedOutlet;
  });

  const toggleExpand = (outletId: string) => {
    setExpandedOutlet((prev) => ({ ...prev, [outletId]: !prev[outletId] }));
  };

  if (findings.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center text-xs text-[#5C6478]">
          No root-cause diagnostics available from the intelligence pipeline.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex items-center justify-between gap-2 flex-wrap pb-1">
        <div className="flex items-center gap-1.5 flex-wrap text-[11px] font-mono">
          <button
            onClick={() => setSelectedOutlet('ALL')}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              selectedOutlet === 'ALL'
                ? 'bg-[#6C8CFF] text-white'
                : 'bg-[#171A20] text-[#8A93A6] hover:text-[#EDEFF3] border border-[#262B35]'
            }`}
          >
            All ({findings.length})
          </button>
          {findings.map((f) => (
            <button
              key={f.outlet_id}
              onClick={() => setSelectedOutlet(f.outlet_id)}
              className={`px-2 py-1 rounded-md transition-colors ${
                selectedOutlet === f.outlet_id
                  ? 'bg-[#1D212A] text-[#6C8CFF] border border-[#6C8CFF]'
                  : 'bg-[#171A20] text-[#8A93A6] hover:text-[#EDEFF3] border border-[#262B35]'
              }`}
            >
              {f.outlet_id} ({f.issues.length})
            </button>
          ))}
        </div>
      </div>

      {filteredFindings.map((finding) => {
        const isExpanded = expandedOutlet[finding.outlet_id] ?? true;
        const isCritical = finding.health_status === 'Critical';

        return (
          <Card
            key={finding.outlet_id}
            className={`border transition-all ${
              isCritical ? 'border-[#D0555A]/40 bg-[#12141A]' : 'border-[#262B35] bg-[#12141A]'
            }`}
          >
            <CardHeader separator>
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-bold text-[#6C8CFF] bg-[#6C8CFF]/10 px-2 py-0.5 rounded">
                    {finding.outlet_id}
                  </span>
                  <div>
                    <CardTitle>Root Cause Diagnostic Hierarchy</CardTitle>
                    <span className="text-xs text-[#5C6478]">
                      {finding.issues.length} operational factor{finding.issues.length !== 1 ? 's' : ''} detected
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={finding.health_status} size="sm" />
                  <span className="text-xs font-mono font-bold text-[#EDEFF3]">
                    Score: {Math.round(finding.performance_score)}/100
                  </span>
                  <button
                    onClick={() => toggleExpand(finding.outlet_id)}
                    className="p-1 rounded text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#1D212A] transition-colors"
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </CardHeader>

            {isExpanded && (
              <CardContent className="p-5 space-y-6">
                {/* Structure: SIGNAL ↓ DETECTED FACTORS ↓ ROOT CAUSE ↓ BUSINESS IMPACT ↓ RECOMMENDED ACTION ↓ MONITORING */}
                <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#262B35]">
                  {/* 1. SIGNAL */}
                  <div className="relative space-y-1.5">
                    <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#1D212A] border border-[#6C8CFF] flex items-center justify-center text-[#6C8CFF]">
                      <Activity className="w-2.5 h-2.5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-[#6C8CFF] font-bold">
                        1. Signal
                      </span>
                    </div>
                    <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] text-xs space-y-1">
                      <p className="font-semibold text-[#EDEFF3]">
                        {finding.priority_issue || finding.issues[0]?.finding || 'Operational telemetry deviation'}
                      </p>
                      <div className="flex items-center gap-3 text-[11px] font-mono text-[#8A93A6]">
                        <span>Composite Score: {Math.round(finding.performance_score)}/100</span>
                        <span>Health Classification: {finding.health_status}</span>
                      </div>
                    </div>
                  </div>

                  {/* 2. DETECTED FACTORS */}
                  <div className="relative space-y-1.5">
                    <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#1D212A] border border-[#E8A33D] flex items-center justify-center text-[#E8A33D]">
                      <Layers className="w-2.5 h-2.5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-[#E8A33D] font-bold">
                        2. Detected Factors ({finding.issues.length})
                      </span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                      {finding.issues.map((issue, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 bg-[#171A20] rounded-lg border border-[#262B35] space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[11px] text-[#6C8CFF] font-semibold">
                              {issue.domain} Agent
                            </span>
                            <Badge
                              variant={
                                issue.severity === 'critical'
                                  ? 'danger'
                                  : issue.severity === 'high'
                                  ? 'warning'
                                  : 'neutral'
                              }
                            >
                              {issue.severity.toUpperCase()}
                            </Badge>
                          </div>
                          <p className="text-[11px] text-[#EDEFF3] font-medium">{issue.finding}</p>
                          {issue.threshold !== null && (
                            <span className="text-[10px] font-mono text-[#5C6478] block">
                              Observed: {issue.value} (Limit: {issue.threshold})
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 3. ROOT CAUSE */}
                  <div className="relative space-y-1.5">
                    <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#1D212A] border border-[#D0555A] flex items-center justify-center text-[#D0555A]">
                      <ShieldAlert className="w-2.5 h-2.5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-[#D0555A] font-bold">
                        3. Root Cause
                      </span>
                    </div>
                    <div className="p-3 bg-[#D0555A]/5 border border-[#D0555A]/25 rounded-lg text-xs space-y-1">
                      <p className="text-[#EDEFF3] font-medium leading-relaxed">
                        {finding.priority_issue || finding.issues[0]?.finding}
                      </p>
                      <span className="text-[10px] font-mono text-[#8A93A6] block">
                        Grounded in deterministic domain rule engine: threshold exceeded across 30-day moving window.
                      </span>
                    </div>
                  </div>

                  {/* 4. BUSINESS IMPACT */}
                  <div className="relative space-y-1.5">
                    <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#1D212A] border border-[#9D7BFF] flex items-center justify-center text-[#9D7BFF]">
                      <AlertTriangle className="w-2.5 h-2.5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-[#9D7BFF] font-bold">
                        4. Business Impact
                      </span>
                    </div>
                    <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] text-xs space-y-1">
                      <p className="text-[#EDEFF3]">
                        Depressed unit performance to <strong className="text-[#D0555A]">{Math.round(finding.performance_score)}/100</strong> with status <strong>{finding.health_status}</strong>.
                      </p>
                      <p className="text-[11px] text-[#8A93A6]">
                        Directly risks customer retention, perishable inventory write-offs, and compliance penalties.
                      </p>
                    </div>
                  </div>

                  {/* 5. RECOMMENDED ACTION */}
                  <div className="relative space-y-1.5">
                    <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#1D212A] border border-[#4FAE7C] flex items-center justify-center text-[#4FAE7C]">
                      <Sparkles className="w-2.5 h-2.5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-[#4FAE7C] font-bold">
                        5. Recommended Action
                      </span>
                    </div>
                    <div className="p-3.5 bg-[#4FAE7C]/5 border border-[#4FAE7C]/25 rounded-lg text-xs space-y-2">
                      <p className="text-[#EDEFF3] font-medium leading-relaxed">
                        {finding.overall_recommendation}
                      </p>
                      {finding.issues.length > 1 && (
                        <div className="space-y-1 pt-2 border-t border-[#4FAE7C]/20">
                          <span className="text-[10px] font-mono text-[#4FAE7C] uppercase block">
                            Specific Prescriptions:
                          </span>
                          {finding.issues.map((iss, i) => (
                            <div key={i} className="text-[11px] text-[#8A93A6] flex items-start gap-1.5">
                              <span className="text-[#4FAE7C]">•</span>
                              <span><strong>{iss.domain}:</strong> {iss.recommendation}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 6. MONITORING */}
                  <div className="relative space-y-1.5">
                    <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#1D212A] border border-[#5C6478] flex items-center justify-center text-[#5C6478]">
                      <Clock className="w-2.5 h-2.5" />
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-[#5C6478] font-bold">
                        6. Monitoring
                      </span>
                    </div>
                    <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] text-xs text-[#8A93A6] space-y-1">
                      <p>
                        Track corrective trajectory on next pipeline evaluation cycle.
                      </p>
                      <span className="text-[10px] font-mono text-[#5C6478] block">
                        Evaluation targets: compliance &ge; 75.0% • wastage &le; 3.0% • staffing coverage &ge; 90.0%
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>
        );
      })}
    </div>
  );
};
