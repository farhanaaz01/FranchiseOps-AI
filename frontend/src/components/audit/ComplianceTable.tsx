import React, { useState, useMemo } from 'react';
import { Badge } from '@/components/ui/Badge';
import { Search, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import type { ComplianceOutletRecord } from '@/services/api/auditApi';

type HealthStatus = 'All' | 'Healthy' | 'At Risk' | 'Critical';

const HEALTH_BADGE: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
  Healthy: 'success',
  'At Risk': 'warning',
  Critical: 'danger',
};

interface ComplianceTableProps {
  records: ComplianceOutletRecord[];
}

export const ComplianceTable: React.FC<ComplianceTableProps> = ({ records }) => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<HealthStatus>('All');
  const [expanded, setExpanded] = useState<string | null>(null);

  const filtered = useMemo(() =>
    records.filter((r) => {
      const matchSearch = !search || r.outlet_id.toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === 'All' || r.health_status === statusFilter;
      return matchSearch && matchStatus;
    }), [records, search, statusFilter]);

  return (
    <div>
      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-2 px-5 py-3 border-b border-[#262B35]">
        <div className="relative flex-1 min-w-[140px] max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-[#5C6478]" />
          <input
            type="text"
            placeholder="Search outlet..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-7 pr-3 py-1 bg-[#171A20] border border-[#262B35] rounded text-[11px] text-[#EDEFF3] placeholder-[#5C6478] focus:outline-none focus:border-[#6C8CFF]/50"
          />
        </div>
        {(['All', 'Healthy', 'At Risk', 'Critical'] as HealthStatus[]).map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
              statusFilter === s
                ? 'bg-[#6C8CFF] text-white'
                : 'bg-[#1D212A] text-[#8A93A6] border border-[#262B35] hover:border-[#6C8CFF]/50'
            }`}
          >
            {s}
          </button>
        ))}
        <span className="text-xs text-[#5C6478] ml-auto">{filtered.length} outlets</span>
      </div>

      {filtered.length === 0 ? (
        <div className="py-10 text-center text-sm text-[#5C6478]">No outlets match the current filters.</div>
      ) : (
        <div className="divide-y divide-[#262B35]">
          {filtered.map((rec) => {
            const isExpanded = expanded === rec.outlet_id;
            const hasIssues = rec.audit_issues.length > 0;
            const scoreColor = rec.compliance_score >= 80 ? '#4FAE7C' : rec.compliance_score >= 65 ? '#E8A33D' : '#D0555A';

            return (
              <div key={rec.outlet_id}>
                <div
                  className={`flex items-center gap-4 px-5 py-4 hover:bg-[#1D212A]/50 transition-colors ${hasIssues ? 'cursor-pointer' : ''}`}
                  onClick={() => hasIssues && setExpanded(isExpanded ? null : rec.outlet_id)}
                >
                  {/* Outlet ID */}
                  <div className="w-24 flex-shrink-0">
                    <span className="font-semibold text-[#EDEFF3] text-sm block">{rec.outlet_id}</span>
                    <span className="text-[10px] font-mono text-[#5C6478]">Score: <span style={{ color: scoreColor }}>{rec.performance_score.toFixed(1)}</span></span>
                  </div>

                  {/* Compliance Score */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] text-[#5C6478]">Compliance</span>
                      <span className="font-mono font-bold text-sm" style={{ color: scoreColor }}>
                        {rec.compliance_score.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-[#171A20] h-1.5 rounded-full overflow-hidden border border-[#262B35]">
                      <div
                        className="h-full rounded-full transition-all duration-300"
                        style={{ width: `${rec.compliance_score}%`, backgroundColor: scoreColor }}
                      />
                    </div>
                  </div>

                  {/* KPI chips */}
                  <div className="hidden sm:flex items-center gap-3 text-[11px]">
                    <div className="text-center">
                      <span className="text-[#5C6478] block">Wastage</span>
                      <span className={`font-mono font-bold ${rec.wastage_rate > 4 ? 'text-[#D0555A]' : 'text-[#8A93A6]'}`}>
                        {rec.wastage_rate.toFixed(2)}%
                      </span>
                    </div>
                    <div className="text-center">
                      <span className="text-[#5C6478] block">Absent.</span>
                      <span className={`font-mono font-bold ${rec.absenteeism_rate > 1 ? 'text-[#E8A33D]' : 'text-[#8A93A6]'}`}>
                        {rec.absenteeism_rate.toFixed(2)}%
                      </span>
                    </div>
                    <div className="text-center">
                      <span className="text-[#5C6478] block">Camp. ROI</span>
                      <span className={`font-mono font-bold ${rec.campaign_roi >= 0 ? 'text-[#4FAE7C]' : 'text-[#D0555A]'}`}>
                        {rec.campaign_roi.toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {/* Health badge */}
                  <Badge variant={HEALTH_BADGE[rec.health_status] || 'default'} size="sm">
                    {rec.health_status}
                  </Badge>

                  {/* Issues indicator */}
                  {hasIssues && (
                    <div className="flex items-center gap-1 text-[#D0555A]">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span className="text-[11px]">{rec.audit_issues.length}</span>
                    </div>
                  )}

                  {hasIssues && (
                    <div className="text-[#5C6478]">
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </div>
                  )}
                </div>

                {/* Expanded issues */}
                {isExpanded && hasIssues && (
                  <div className="px-5 pb-4 space-y-2">
                    {rec.audit_issues.map((issue, idx) => (
                      <div key={idx} className="p-3 bg-[#171A20] border border-[#262B35] rounded-lg text-xs">
                        <div className="flex items-start gap-2">
                          <Badge
                            variant={issue.severity === 'critical' || issue.severity === 'high' ? 'danger' : 'warning'}
                            size="sm"
                          >
                            {issue.severity}
                          </Badge>
                          <div className="flex-1">
                            <p className="text-[#EDEFF3] mb-1">{issue.finding}</p>
                            <p className="text-[#8A93A6]">→ {issue.recommendation}</p>
                            {issue.value !== null && issue.threshold !== null && (
                              <p className="font-mono text-[#5C6478] mt-1">
                                {issue.metric}: {issue.value.toFixed(1)} (threshold: {issue.threshold})
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                    {rec.overall_recommendation && (
                      <div className="p-3 bg-[#6C8CFF]/05 border border-[#6C8CFF]/20 rounded-lg text-[11px] text-[#8A93A6]">
                        <span className="text-[#6C8CFF] font-semibold">Recommended Action: </span>
                        {rec.overall_recommendation}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
