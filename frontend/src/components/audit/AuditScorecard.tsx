import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ShieldCheck, AlertTriangle, CheckCircle2, FileText } from 'lucide-react';
import type { AuditRecord } from '@/services/api/auditApi';

interface AuditScorecardProps {
  audits: AuditRecord[];
}

export const AuditScorecard: React.FC<AuditScorecardProps> = ({ audits }) => {
  const avgScore = audits.length
    ? (audits.reduce((acc, a) => acc + a.score, 0) / audits.length).toFixed(1)
    : '85.0';

  const totalViolations = audits.reduce(
    (acc, a) => acc + a.criticalViolations + a.minorViolations,
    0
  );

  return (
    <div className="space-y-6">
      {/* Top metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-[#4FAE7C]/10 text-[#4FAE7C]">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs text-[#8A93A6]">Network Compliance</span>
              <div className="text-xl font-bold font-mono text-[#EDEFF3]">
                {avgScore} <span className="text-xs text-[#5C6478]">/ 100</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-[#6C8CFF]/10 text-[#6C8CFF]">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs text-[#8A93A6]">Audits Logged</span>
              <div className="text-xl font-bold font-mono text-[#EDEFF3]">
                {audits.length}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-[#E8A33D]/10 text-[#E8A33D]">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs text-[#8A93A6]">Active Violations</span>
              <div className="text-xl font-bold font-mono text-[#EDEFF3]">
                {totalViolations}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Audit List */}
      <Card>
        <CardHeader separator>
          <CardTitle>Recent Food Safety & Health Inspection Records</CardTitle>
        </CardHeader>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#1D212A] text-[#8A93A6] font-mono border-b border-[#262B35]">
              <tr>
                <th className="px-5 py-3">Audit ID</th>
                <th className="px-5 py-3">Outlet</th>
                <th className="px-5 py-3">Inspection Date</th>
                <th className="px-5 py-3">Inspector</th>
                <th className="px-5 py-3">Score</th>
                <th className="px-5 py-3">Violations</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Findings & Remediation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#262B35]">
              {audits.map((audit) => (
                <tr key={audit.id} className="hover:bg-[#1D212A]/50 transition-colors">
                  <td className="px-5 py-3.5 font-mono text-[#6C8CFF] font-medium">{audit.id}</td>
                  <td className="px-5 py-3.5 font-medium text-[#EDEFF3]">{audit.outletName}</td>
                  <td className="px-5 py-3.5 font-mono text-[#8A93A6]">{audit.inspectionDate}</td>
                  <td className="px-5 py-3.5 text-[#8A93A6]">{audit.auditorName}</td>
                  <td className="px-5 py-3.5 font-mono font-bold text-[#EDEFF3]">
                    {audit.score}
                    <span className="text-[10px] text-[#5C6478] font-normal ml-0.5">/100</span>
                  </td>
                  <td className="px-5 py-3.5 font-mono">
                    <span className={audit.criticalViolations > 0 ? 'text-[#D0555A]' : 'text-[#8A93A6]'}>
                      {audit.criticalViolations} Crit • {audit.minorViolations} Min
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge
                      status={
                        audit.status === 'Passed'
                          ? 'Healthy'
                          : audit.status === 'Warning'
                          ? 'At Risk'
                          : 'Critical'
                      }
                      size="sm"
                    />
                  </td>
                  <td className="px-5 py-3.5 text-[#8A93A6] max-w-xs truncate" title={audit.notes}>
                    {audit.notes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
