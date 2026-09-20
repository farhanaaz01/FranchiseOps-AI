import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import {
  Target,
  AlertTriangle,
  Sparkles,
  Bot,
  ArrowRight,
  ShieldAlert,
  Activity,
  CheckCircle2,
  Clock,
  RefreshCw,
  Eye,
  Layers,
  ChevronRight,
  SlidersHorizontal,
  ExternalLink,
  Info,
} from 'lucide-react';
import { useIntelligence } from '@/hooks/useIntelligence';
import { useOutlets } from '@/hooks/useOutlets';
import { RecommendationCard } from '@/components/ai/RecommendationCard';

export interface DecisionItem {
  id: string;
  outletId: string;
  outletName: string;
  domain: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  metric: string;
  value: number | null;
  threshold: number | null;
  finding: string;
  recommendation: string;
  overallRecommendation?: string;
  priorityIssue?: string | null;
  performanceScore: number;
  healthStatus: string;
  acknowledged?: boolean;
}

const SEVERITY_WEIGHT: Record<string, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
};

export const DecisionCenter: React.FC = () => {
  const navigate = useNavigate();
  const { pipelineData, rootCauses, loading, isRunning, refresh, triggerPipeline } = useIntelligence();
  const { outlets } = useOutlets();

  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [domainFilter, setDomainFilter] = useState<string>('ALL');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [acknowledgedMap, setAcknowledgedMap] = useState<Record<string, boolean>>({});

  // Flatten and sort findings by backend severity
  const decisionItems: DecisionItem[] = useMemo(() => {
    const items: DecisionItem[] = [];

    rootCauses.forEach((rc) => {
      const outletMeta = outlets.find((o) => o.id === rc.outlet_id || String(o.outlet_id) === rc.outlet_id);
      const outletName = outletMeta?.name || `Outlet ${rc.outlet_id}`;

      rc.issues.forEach((issue, idx) => {
        const id = `${rc.outlet_id}-${issue.domain}-${idx}`;
        const sev = (issue.severity?.toLowerCase() || 'medium') as 'critical' | 'high' | 'medium' | 'low';

        items.push({
          id,
          outletId: rc.outlet_id,
          outletName,
          domain: issue.domain,
          severity: sev,
          metric: issue.metric,
          value: issue.value ?? null,
          threshold: issue.threshold ?? null,
          finding: issue.finding,
          recommendation: issue.recommendation,
          overallRecommendation: rc.overall_recommendation,
          priorityIssue: rc.priority_issue,
          performanceScore: rc.performance_score,
          healthStatus: rc.health_status,
          acknowledged: !!acknowledgedMap[id],
        });
      });
    });

    // Sort strictly by backend severity weight (descending)
    return items.sort((a, b) => {
      const wA = SEVERITY_WEIGHT[a.severity] || 0;
      const wB = SEVERITY_WEIGHT[b.severity] || 0;
      return wB - wA;
    });
  }, [rootCauses, outlets, acknowledgedMap]);

  // Filtered queue
  const filteredQueue = useMemo(() => {
    return decisionItems.filter((item) => {
      if (severityFilter !== 'ALL' && item.severity.toUpperCase() !== severityFilter) return false;
      if (domainFilter !== 'ALL' && item.domain.toUpperCase() !== domainFilter) return false;
      return true;
    });
  }, [decisionItems, severityFilter, domainFilter]);

  // Active selected item (or first in queue)
  const activeItem = useMemo(() => {
    if (selectedId) {
      const found = decisionItems.find((d) => d.id === selectedId);
      if (found) return found;
    }
    return filteredQueue[0] || decisionItems[0] || null;
  }, [selectedId, decisionItems, filteredQueue]);

  const handleAcknowledge = (id: string) => {
    setAcknowledgedMap((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const getDomainNavigation = (domain: string) => {
    switch (domain.toLowerCase()) {
      case 'inventory':
        return '/inventory';
      case 'staff':
      case 'workforce':
        return '/workforce';
      case 'marketing':
        return '/marketing';
      case 'audit':
        return '/audit';
      case 'outlet':
      default:
        return '/outlets';
    }
  };

  const criticalCount = decisionItems.filter((d) => d.severity === 'critical').length;
  const highCount = decisionItems.filter((d) => d.severity === 'high').length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Operational Decision Center"
        subtitle="Convert cross-domain intelligence signals into prioritized managerial decisions and monitoring workflows."
        badge={
          <Badge variant={criticalCount > 0 ? 'danger' : 'accent'}>
            {decisionItems.length} Issues Under Supervised Review
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
              Sync Telemetry
            </Button>
            <Button
              variant="primary"
              size="sm"
              loading={isRunning}
              icon={<Target className="w-3.5 h-3.5" />}
              onClick={triggerPipeline}
            >
              {isRunning ? 'Evaluating...' : 'Re-Evaluate Network'}
            </Button>
          </div>
        }
      />

      {/* Decision Workflow Overview Bar */}
      <Card className="bg-[#12141A] border-[#262B35]">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-[#5C6478] uppercase tracking-wider font-semibold">
                Managerial Decision Workflow:
              </span>
            </div>
            <div className="flex items-center gap-2 flex-wrap flex-1 justify-start md:justify-end">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#6C8CFF]/10 text-[#6C8CFF] border border-[#6C8CFF]/30 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>1. Finding Detected</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#5C6478]" />
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#6C8CFF]/10 text-[#6C8CFF] border border-[#6C8CFF]/30 font-medium">
                <Eye className="w-3.5 h-3.5" />
                <span>2. Review Root Cause</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#5C6478]" />
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#E8A33D]/10 text-[#E8A33D] border border-[#E8A33D]/30 font-medium">
                <Clock className="w-3.5 h-3.5" />
                <span>3. Acknowledge</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#5C6478]" />
              <div
                className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#171A20] text-[#5C6478] border border-[#262B35] font-mono cursor-not-allowed"
                title="Action workflow not connected"
              >
                <span>4. Action (Not Connected)</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-[#5C6478]" />
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#4FAE7C]/10 text-[#4FAE7C] border border-[#4FAE7C]/30 font-medium">
                <Activity className="w-3.5 h-3.5" />
                <span>5. Monitor KPIs</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Grid: Left 5 cols Queue, Right 7 cols Active Decision Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Prioritized Attention Queue */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="h-[740px] flex flex-col">
            <CardHeader separator>
              <div className="space-y-3 w-full">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-[#D0555A]" />
                    <CardTitle>Requires Attention</CardTitle>
                  </div>
                  <span className="text-xs font-mono text-[#8A93A6]">
                    {filteredQueue.length} prioritized
                  </span>
                </div>

                {/* Filter Tabs */}
                <div className="flex items-center gap-1 flex-wrap text-[11px] font-mono">
                  {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
                    <button
                      key={sev}
                      onClick={() => setSeverityFilter(sev)}
                      className={`px-2 py-0.5 rounded transition-colors ${
                        severityFilter === sev
                          ? 'bg-[#6C8CFF] text-white'
                          : 'bg-[#171A20] text-[#8A93A6] hover:text-[#EDEFF3] border border-[#262B35]'
                      }`}
                    >
                      {sev}
                    </button>
                  ))}
                  <div className="w-px h-4 bg-[#262B35] mx-1" />
                  {['ALL', 'INVENTORY', 'STAFF', 'AUDIT', 'OUTLET'].map((dom) => (
                    <button
                      key={dom}
                      onClick={() => setDomainFilter(dom)}
                      className={`px-2 py-0.5 rounded transition-colors ${
                        domainFilter === dom
                          ? 'bg-[#1D212A] text-[#EDEFF3] border border-[#6C8CFF]'
                          : 'bg-[#171A20] text-[#5C6478] hover:text-[#EDEFF3] border border-transparent'
                      }`}
                    >
                      {dom}
                    </button>
                  ))}
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-3 overflow-y-auto flex-1 space-y-2">
              {filteredQueue.length === 0 ? (
                <div className="py-16 text-center text-xs text-[#5C6478]">
                  No operational issues matching selected filters.
                </div>
              ) : (
                filteredQueue.map((item) => {
                  const isSelected = activeItem?.id === item.id;
                  const isCrit = item.severity === 'critical';

                  return (
                    <div
                      key={item.id}
                      onClick={() => setSelectedId(item.id)}
                      className={`p-3 rounded-lg border transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-[#1D212A] border-[#6C8CFF] shadow-sm'
                          : isCrit
                          ? 'bg-[#D0555A]/5 border-[#D0555A]/25 hover:border-[#D0555A]/50'
                          : 'bg-[#171A20] border-[#262B35] hover:border-[#3A4155]'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold text-[#6C8CFF] bg-[#6C8CFF]/10 px-1.5 py-0.5 rounded">
                            {item.outletId}
                          </span>
                          <span className="text-xs font-semibold text-[#EDEFF3] truncate max-w-[150px]">
                            {item.outletName}
                          </span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Badge
                            variant={
                              item.severity === 'critical'
                                ? 'danger'
                                : item.severity === 'high'
                                ? 'warning'
                                : 'neutral'
                            }
                          >
                            {item.severity.toUpperCase()}
                          </Badge>
                          {item.acknowledged && (
                            <span className="text-[10px] font-mono text-[#4FAE7C] bg-[#4FAE7C]/10 px-1 py-0.5 rounded border border-[#4FAE7C]/20">
                              ACK
                            </span>
                          )}
                        </div>
                      </div>

                      <p className="text-xs text-[#EDEFF3] font-medium mt-1.5 line-clamp-2">
                        {item.finding}
                      </p>

                      <div className="flex items-center justify-between mt-2 pt-2 border-t border-[#262B35]/60 text-[10px] font-mono text-[#5C6478]">
                        <span className="text-[#8A93A6]">{item.domain} Agent</span>
                        {item.threshold !== null && (
                          <span>
                            Value: {item.value} (Limit: {item.threshold})
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Structured Decision Workspace */}
        <div className="lg:col-span-7 space-y-4">
          {activeItem ? (
            <Card className="h-[740px] flex flex-col">
              <CardHeader separator>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono font-bold text-[#6C8CFF] bg-[#6C8CFF]/10 px-2 py-0.5 rounded">
                      {activeItem.outletId}
                    </span>
                    <div>
                      <CardTitle>{activeItem.outletName}</CardTitle>
                      <span className="text-xs text-[#5C6478]">
                        Domain: {activeItem.domain} Agent • Health Score: {activeItem.performanceScore}/100
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={activeItem.healthStatus} size="sm" />
                    <Button
                      variant={activeItem.acknowledged ? 'secondary' : 'outline'}
                      size="sm"
                      icon={<CheckCircle2 className="w-3.5 h-3.5" />}
                      onClick={() => handleAcknowledge(activeItem.id)}
                    >
                      {activeItem.acknowledged ? 'Acknowledged' : 'Acknowledge Finding'}
                    </Button>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="p-6 overflow-y-auto flex-1 space-y-5">
                {/* 1. SIGNAL */}
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-xs font-mono text-[#6C8CFF] uppercase tracking-wider font-semibold">
                    <Activity className="w-4 h-4" />
                    <span>1. Telemetry Signal Detected</span>
                  </div>
                  <div className="p-3.5 rounded-lg bg-[#171A20] border border-[#262B35] space-y-2">
                    <p className="text-sm font-medium text-[#EDEFF3]">{activeItem.finding}</p>
                    <div className="flex items-center gap-4 text-xs font-mono text-[#8A93A6]">
                      <span>Metric: <strong className="text-[#EDEFF3]">{activeItem.metric}</strong></span>
                      {activeItem.value !== null && (
                        <span>Observed: <strong className="text-[#D0555A]">{activeItem.value}</strong></span>
                      )}
                      {activeItem.threshold !== null && (
                        <span>Operational Limit: <strong className="text-[#4FAE7C]">{activeItem.threshold}</strong></span>
                      )}
                    </div>
                  </div>
                </div>

                {/* 2. ROOT CAUSE */}
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-xs font-mono text-[#E8A33D] uppercase tracking-wider font-semibold">
                    <Bot className="w-4 h-4" />
                    <span>2. Root Cause Diagnostic</span>
                  </div>
                  <div className="p-3.5 rounded-lg bg-[#171A20] border border-[#262B35] space-y-2">
                    <p className="text-xs text-[#EDEFF3] leading-relaxed">
                      {activeItem.priorityIssue || activeItem.finding}
                    </p>
                    <p className="text-[11px] text-[#8A93A6]">
                      Identified by {activeItem.domain} Agent through deterministic threshold analysis evaluated against 30-day baseline telemetry.
                    </p>
                  </div>
                </div>

                {/* 3. BUSINESS IMPACT */}
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-xs font-mono text-[#D0555A] uppercase tracking-wider font-semibold">
                    <ShieldAlert className="w-4 h-4" />
                    <span>3. Operational & Business Impact</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                      <span className="text-[10px] font-mono text-[#5C6478] uppercase block">
                        Affected Operational Area
                      </span>
                      <span className="text-xs font-semibold text-[#EDEFF3] mt-0.5 block">
                        {activeItem.domain} Operations
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                      <span className="text-[10px] font-mono text-[#5C6478] uppercase block">
                        Unit Health Classification
                      </span>
                      <span className="text-xs font-semibold text-[#D0555A] mt-0.5 block">
                        {activeItem.healthStatus} ({activeItem.performanceScore}/100)
                      </span>
                    </div>
                  </div>
                </div>

                {/* 4. RECOMMENDATION */}
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-xs font-mono text-[#4FAE7C] uppercase tracking-wider font-semibold">
                    <Sparkles className="w-4 h-4" />
                    <span>4. Prescriptive AI Recommendation</span>
                  </div>
                  <div className="p-3.5 rounded-lg bg-[#4FAE7C]/5 border border-[#4FAE7C]/20 space-y-2">
                    <p className="text-xs font-medium text-[#EDEFF3] leading-relaxed">
                      {activeItem.recommendation}
                    </p>
                    {activeItem.overallRecommendation && (
                      <div className="pt-2 border-t border-[#4FAE7C]/20 text-[11px] text-[#8A93A6]">
                        <span className="text-[#4FAE7C] font-semibold">Consolidated Directive: </span>
                        {activeItem.overallRecommendation}
                      </div>
                    )}
                  </div>
                </div>

                {/* 5. ACTION */}
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-xs font-mono text-[#5C6478] uppercase tracking-wider font-semibold">
                    <Target className="w-4 h-4" />
                    <span>5. Manager Action Workflow</span>
                  </div>
                  <div className="p-3.5 rounded-lg bg-[#171A20] border border-[#262B35] space-y-3">
                    <div className="p-2 rounded bg-[#12141A] border border-[#262B35] flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2 text-[#5C6478]">
                        <Info className="w-3.5 h-3.5 shrink-0" />
                        <span className="font-mono text-[11px]">
                          Action workflow not connected (Supervised Review Mode)
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-[#8A93A6] bg-[#171A20] px-2 py-0.5 rounded border border-[#262B35]">
                        Read-Only
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="primary"
                        size="sm"
                        icon={<ExternalLink className="w-3.5 h-3.5" />}
                        onClick={() => navigate(getDomainNavigation(activeItem.domain))}
                      >
                        Navigate to {activeItem.domain} Module
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/outlets/${activeItem.outletId}`)}
                      >
                        View Outlet Full Profile
                      </Button>
                    </div>
                  </div>
                </div>

                {/* 6. MONITORING */}
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-xs font-mono text-[#6C8CFF] uppercase tracking-wider font-semibold">
                    <Clock className="w-4 h-4" />
                    <span>6. Verification & Monitoring</span>
                  </div>
                  <div className="p-3.5 rounded-lg bg-[#171A20] border border-[#262B35] text-xs text-[#8A93A6] space-y-1">
                    <p>
                      Monitor <strong>{activeItem.metric}</strong> on the next scheduled pipeline run (generated daily or triggered on demand).
                    </p>
                    <p className="font-mono text-[11px] text-[#5C6478]">
                      Baseline threshold target: {activeItem.threshold ?? 'SOP Compliance'} • Status logged in session audit trail.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="h-[740px] flex items-center justify-center p-8 text-center text-xs text-[#5C6478]">
              No active issue selected. Choose an item from the queue to review decision details.
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
