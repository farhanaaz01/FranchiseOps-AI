import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Clock, Bot, Sparkles, Activity, Info, ShieldAlert } from 'lucide-react';

export interface TimelineEventItem {
  id: string;
  timestamp: string;
  agentName: string;
  domain: string;
  eventName: string;
  targetOutlet: string;
  finding: string;
  recommendation: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

interface AgentActivityTimelineProps {
  events: TimelineEventItem[];
}

export const AgentActivityTimeline: React.FC<AgentActivityTimelineProps> = ({ events }) => {
  return (
    <Card className="border-[#262B35] bg-[#12141A]">
      <CardHeader separator>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-2">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-[#6C8CFF]" />
            <CardTitle>Agent Activity & Diagnostic Telemetry Timeline</CardTitle>
          </div>
          <span className="text-xs font-mono text-[#5C6478]">
            Format: Time ↓ Agent ↓ Event ↓ Finding ↓ Recommendation
          </span>
        </div>
      </CardHeader>
      <CardContent className="p-5 space-y-4">
        {/* Backend Streaming Disclaimer */}
        <div className="p-3 bg-[#171A20] border border-[#262B35] rounded-lg flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-[#8A93A6]">
            <Info className="w-3.5 h-3.5 text-[#6C8CFF] shrink-0" />
            <span>
              Real-time event streaming is not exposed by the backend. Showing diagnostic events generated during the latest pipeline evaluation.
            </span>
          </div>
          <span className="text-[10px] font-mono text-[#4FAE7C] bg-[#4FAE7C]/10 px-2 py-0.5 rounded border border-[#4FAE7C]/20 shrink-0">
            Pipeline v1.0 Live
          </span>
        </div>

        {events.length === 0 ? (
          <div className="py-12 text-center text-xs text-[#5C6478]">
            No historical agent execution events logged by the pipeline.
          </div>
        ) : (
          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#262B35]">
            {events.map((evt) => (
              <div key={evt.id} className="relative space-y-2">
                {/* Timeline Node Dot */}
                <div className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-[#1D212A] border border-[#6C8CFF] flex items-center justify-center text-[#6C8CFF]">
                  <Bot className="w-2.5 h-2.5" />
                </div>

                {/* Event Card with 5-Tier Format: Time ↓ Agent ↓ Event ↓ Finding ↓ Recommendation */}
                <div className="p-4 rounded-lg bg-[#171A20] border border-[#262B35] space-y-3">
                  {/* Tier 1 & 2: TIME & AGENT */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#262B35] pb-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[10px] font-mono text-[#5C6478] uppercase">Time:</span>
                      <span className="text-xs font-mono text-[#EDEFF3] font-semibold flex items-center gap-1">
                        <Clock className="w-3 h-3 text-[#6C8CFF]" />
                        {evt.timestamp}
                      </span>
                      <span className="text-[#5C6478]">•</span>
                      <span className="text-[10px] font-mono text-[#5C6478] uppercase">Agent:</span>
                      <span className="text-xs font-semibold text-[#EDEFF3]">{evt.agentName}</span>
                      <span className="text-[10px] font-mono text-[#6C8CFF] bg-[#6C8CFF]/10 px-1.5 py-0.5 rounded">
                        {evt.targetOutlet}
                      </span>
                    </div>
                    <Badge
                      variant={
                        evt.severity === 'critical'
                          ? 'danger'
                          : evt.severity === 'high'
                          ? 'warning'
                          : 'neutral'
                      }
                    >
                      {evt.severity.toUpperCase()}
                    </Badge>
                  </div>

                  {/* Tier 3: EVENT */}
                  <div className="space-y-0.5">
                    <span className="text-[10px] font-mono text-[#5C6478] uppercase tracking-wider block">
                      Operational Event
                    </span>
                    <h5 className="text-xs font-semibold text-[#EDEFF3]">{evt.eventName}</h5>
                  </div>

                  {/* Tier 4: FINDING */}
                  <div className="space-y-0.5">
                    <span className="text-[10px] font-mono text-[#D0555A] uppercase tracking-wider block font-semibold">
                      Diagnostic Finding
                    </span>
                    <p className="text-xs text-[#8A93A6] bg-[#12141A] p-2.5 rounded border border-[#262B35] leading-relaxed">
                      {evt.finding}
                    </p>
                  </div>

                  {/* Tier 5: RECOMMENDATION */}
                  <div className="space-y-0.5">
                    <span className="text-[10px] font-mono text-[#4FAE7C] uppercase tracking-wider block font-semibold">
                      Prescriptive Recommendation
                    </span>
                    <p className="text-xs text-[#8A93A6] bg-[#4FAE7C]/5 p-2.5 rounded border border-[#4FAE7C]/20 leading-relaxed">
                      {evt.recommendation}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
