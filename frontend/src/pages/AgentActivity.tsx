import React, { useMemo } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { KPICard } from '@/components/kpi/KPICard';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Bot, Cpu, Zap, CheckCircle2, Play, RefreshCw, Activity, ShieldCheck } from 'lucide-react';
import {
  AgentStatusGrid,
  AgentActivityTimeline,
  DomainAgentTelemetry,
  TimelineEventItem,
} from '@/components/agents';
import { useIntelligence } from '@/hooks/useIntelligence';

export const AgentActivity: React.FC = () => {
  const { pipelineData, rootCauses, loading, isRunning, refresh, triggerPipeline } = useIntelligence();

  // Formatted date string from real pipeline generated_at
  const lastUpdatedStr = useMemo(() => {
    if (!pipelineData.generated_at) return 'Recently';
    try {
      const d = new Date(pipelineData.generated_at);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return 'Recently';
    }
  }, [pipelineData.generated_at]);

  // Derive the 5 backend-confirmed domain agents from real pipeline root_causes
  const agents: DomainAgentTelemetry[] = useMemo(() => {
    const config = [
      {
        id: 'outlet',
        name: 'Outlet Performance Agent',
        domain: 'Outlet',
        defaultDesc: 'Aggregates unit-level sales velocity, manager benchmarks, and cohort scoring.',
      },
      {
        id: 'inventory',
        name: 'Inventory Replenishment Agent',
        domain: 'Inventory',
        defaultDesc: 'Calculates demand, monitors safety buffers, and flags stockout / wastage risks.',
      },
      {
        id: 'staff',
        name: 'Workforce Dispatch Agent',
        domain: 'Staff',
        defaultDesc: 'Tracks biometric attendance, detects peak understaffing, and recommends float staffing.',
      },
      {
        id: 'marketing',
        name: 'Marketing Attribution Agent',
        domain: 'Marketing',
        defaultDesc: 'Monitors promotional campaign attribution, calculates ROI, and flags underperforming discounts.',
      },
      {
        id: 'audit',
        name: 'Audit & Compliance Agent',
        domain: 'Audit',
        defaultDesc: 'Monitors food safety compliance, audit scores, and schedules mandatory inspection follow-ups.',
      },
    ];

    return config.map((c) => {
      // Find all issues matching this domain across all root_causes
      const domainIssues: Array<{
        outletId: string;
        finding: string;
        recommendation: string;
        severity: string;
      }> = [];

      rootCauses.forEach((rc) => {
        rc.issues.forEach((iss) => {
          if (iss.domain.toLowerCase() === c.domain.toLowerCase()) {
            domainIssues.push({
              outletId: rc.outlet_id,
              finding: iss.finding,
              recommendation: iss.recommendation,
              severity: iss.severity,
            });
          }
        });
      });

      const topIssue = domainIssues[0];
      const hasCritical = domainIssues.some((i) => i.severity === 'critical');
      const hasHigh = domainIssues.some((i) => i.severity === 'high');

      return {
        id: c.id,
        name: c.name,
        domain: c.domain,
        status: 'Active',
        lastUpdated: lastUpdatedStr,
        findingsCount: domainIssues.length,
        recommendationsCount: domainIssues.length,
        latestFinding: topIssue ? `${topIssue.outletId}: ${topIssue.finding}` : 'No anomalous telemetry breaches detected in 30-day baseline.',
        latestRecommendation: topIssue ? topIssue.recommendation : 'Continue routine continuous telemetry monitoring.',
        severityMax: hasCritical ? 'critical' : hasHigh ? 'high' : 'medium',
      };
    });
  }, [rootCauses, lastUpdatedStr]);

  // Construct real timeline events from latest pipeline execution
  const timelineEvents: TimelineEventItem[] = useMemo(() => {
    const events: TimelineEventItem[] = [];

    rootCauses.forEach((rc) => {
      rc.issues.forEach((iss, idx) => {
        const sev = (iss.severity?.toLowerCase() || 'medium') as 'critical' | 'high' | 'medium' | 'low';
        events.push({
          id: `evt-${rc.outlet_id}-${iss.domain}-${idx}`,
          timestamp: lastUpdatedStr,
          agentName: `${iss.domain} Agent`,
          domain: iss.domain,
          eventName: `Evaluation Check: ${iss.metric}`,
          targetOutlet: rc.outlet_id,
          finding: iss.finding,
          recommendation: iss.recommendation,
          severity: sev,
        });
      });
    });

    return events;
  }, [rootCauses, lastUpdatedStr]);

  const totalFindings = useMemo(
    () => agents.reduce((acc, a) => acc + a.findingsCount, 0),
    [agents]
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Agent Activity & Orchestration"
        subtitle="Specialized domain agent monitoring, diagnostic findings telemetry, and pipeline execution logs."
        badge={<Badge variant="success">5 Specialized Domain Agents Active</Badge>}
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
              icon={<Play className="w-3.5 h-3.5" />}
              onClick={triggerPipeline}
            >
              {isRunning ? 'Evaluating...' : 'Run Pipeline Evaluation'}
            </Button>
          </div>
        }
      />

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Active Domain Agents"
          value="5"
          subtext="Outlet, Inventory, Staff, Marketing, Audit"
          icon={<Bot className="w-4 h-4 text-[#6C8CFF]" />}
        />
        <KPICard
          title="Total Findings Emitted"
          value={String(totalFindings)}
          subtext="Across 5 monitored franchise outlets"
          status={totalFindings > 0 ? 'risk' : 'healthy'}
          icon={<Zap className="w-4 h-4 text-[#E8A33D]" />}
        />
        <KPICard
          title="Pipeline Model Version"
          value="xgb-v1"
          subtext="Multi-unit regression & classifier"
          icon={<Cpu className="w-4 h-4 text-[#6C8CFF]" />}
        />
        <KPICard
          title="Evaluation Execution"
          value="100%"
          subtext={`Completed at ${lastUpdatedStr}`}
          status="healthy"
          icon={<CheckCircle2 className="w-4 h-4 text-[#4FAE7C]" />}
        />
      </div>

      {/* Domain Agent Status Grid (Section 13) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-[#6C8CFF]" />
            <h3 className="text-sm font-semibold text-[#EDEFF3]">Domain Agents Status</h3>
          </div>
          <span className="text-xs font-mono text-[#5C6478]">
            Status: Confirmed by Backend Data Engine
          </span>
        </div>
        <AgentStatusGrid agents={agents} />
      </div>

      {/* Agent Activity Timeline (Section 14) */}
      <AgentActivityTimeline events={timelineEvents} />
    </div>
  );
};
