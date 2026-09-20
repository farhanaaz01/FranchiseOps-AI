import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  Bot,
  Package,
  Users,
  Megaphone,
  ShieldCheck,
  Cpu,
  Store,
  Clock,
  ArrowRight,
  AlertCircle,
  Sparkles,
} from 'lucide-react';

export interface DomainAgentTelemetry {
  id: string;
  name: string;
  domain: string;
  status: 'Active' | 'Idle' | 'Unavailable' | 'Error';
  lastUpdated: string;
  findingsCount: number;
  recommendationsCount: number;
  currentTask?: string;
  description?: string;
  latestFinding: string;
  latestRecommendation: string;
  severityMax?: 'critical' | 'high' | 'medium' | 'low';
}

export type AgentInfo = DomainAgentTelemetry;



interface AgentStatusGridProps {
  agents: DomainAgentTelemetry[];
  onSelectAgent?: (agent: DomainAgentTelemetry) => void;
}

export const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({
  agents,
  onSelectAgent,
}) => {
  const getIcon = (id: string) => {
    switch (id) {
      case 'inventory':
        return <Package className="w-5 h-5 text-[#6C8CFF]" />;
      case 'staff':
        return <Users className="w-5 h-5 text-[#E8A33D]" />;
      case 'marketing':
        return <Megaphone className="w-5 h-5 text-[#9D7BFF]" />;
      case 'audit':
        return <ShieldCheck className="w-5 h-5 text-[#4FAE7C]" />;
      case 'outlet':
      default:
        return <Store className="w-5 h-5 text-[#6C8CFF]" />;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {agents.map((agent) => {
        const isCritical = agent.severityMax === 'critical';
        const isHigh = agent.severityMax === 'high';

        return (
          <Card
            key={agent.id}
            className={`transition-all ${
              isCritical
                ? 'border-[#D0555A]/40 bg-[#12141A]'
                : isHigh
                ? 'border-[#E8A33D]/40 bg-[#12141A]'
                : 'border-[#262B35] bg-[#12141A] hover:border-[#3A4155]'
            }`}
          >
            <CardContent className="p-5 space-y-4">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-[#171A20] border border-[#262B35]">
                    {getIcon(agent.id)}
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-[#EDEFF3]">{agent.name}</h4>
                    <span className="text-[11px] text-[#5C6478] font-mono">
                      Domain: {agent.domain}
                    </span>
                  </div>
                </div>
                <Badge
                  variant={
                    agent.status === 'Active'
                      ? 'success'
                      : agent.status === 'Idle'
                      ? 'accent'
                      : 'neutral'
                  }
                >
                  {agent.status.toUpperCase()}
                </Badge>
              </div>

              {/* Status & Last Activity */}
              <div className="flex items-center justify-between text-[11px] font-mono text-[#8A93A6] py-1.5 px-2 rounded bg-[#171A20] border border-[#262B35]">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3 h-3 text-[#5C6478]" />
                  <span>Last Evaluated:</span>
                </span>
                <span className="text-[#EDEFF3] font-semibold">{agent.lastUpdated}</span>
              </div>

              {/* Latest Finding */}
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-[#5C6478] uppercase tracking-wider block font-semibold">
                  Latest Diagnostic Finding
                </span>
                <p className="text-xs text-[#EDEFF3] bg-[#171A20] p-2.5 rounded border border-[#262B35] leading-relaxed line-clamp-2">
                  {agent.latestFinding}
                </p>
              </div>

              {/* Latest Recommendation */}
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-[#4FAE7C] uppercase tracking-wider block font-semibold">
                  Latest Recommendation
                </span>
                <p className="text-xs text-[#8A93A6] bg-[#4FAE7C]/5 p-2.5 rounded border border-[#4FAE7C]/20 leading-relaxed line-clamp-2">
                  {agent.latestRecommendation}
                </p>
              </div>

              {/* Findings & Recommendations Count */}
              <div className="flex items-center justify-between text-xs py-2 border-t border-[#262B35] font-mono text-[#8A93A6]">
                <span>Findings: <strong className="text-[#EDEFF3]">{agent.findingsCount}</strong></span>
                <span>Recommendations: <strong className="text-[#4FAE7C]">{agent.recommendationsCount}</strong></span>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
