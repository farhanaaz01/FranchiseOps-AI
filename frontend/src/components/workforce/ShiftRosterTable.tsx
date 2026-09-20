import React, { useState, useMemo } from 'react';
import { Badge } from '@/components/ui/Badge';
import { Clock, User, Search } from 'lucide-react';
import type { EnrichedShiftRecord } from '@/hooks/useWorkforce';

type ShiftStatus = EnrichedShiftRecord['status'] | 'all';

const STATUS_BADGE: Record<string, 'success' | 'danger' | 'warning' | 'default'> = {
  completed: 'success',
  absent: 'danger',
  cancelled: 'warning',
  scheduled: 'default',
};

const STATUS_LABEL: Record<string, string> = {
  completed: 'Completed',
  absent: 'Absent',
  cancelled: 'Cancelled',
  scheduled: 'Scheduled',
};

interface ShiftRosterTableProps {
  shifts: EnrichedShiftRecord[];
}

export const ShiftRosterTable: React.FC<ShiftRosterTableProps> = ({ shifts }) => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ShiftStatus>('all');

  const filtered = useMemo(() => {
    return shifts.filter((s) => {
      const matchSearch =
        !search ||
        s.employeeName.toLowerCase().includes(search.toLowerCase()) ||
        s.outletName.toLowerCase().includes(search.toLowerCase()) ||
        s.role.toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === 'all' || s.status === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [shifts, search, statusFilter]);

  return (
    <div>
      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-2 px-5 py-3 border-b border-[#262B35]">
        <div className="relative flex-1 min-w-[160px] max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-[#5C6478]" />
          <input
            type="text"
            placeholder="Search employee, outlet, role..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-7 pr-3 py-1 bg-[#171A20] border border-[#262B35] rounded text-[11px] text-[#EDEFF3] placeholder-[#5C6478] focus:outline-none focus:border-[#6C8CFF]/50"
          />
        </div>
        {(['all', 'scheduled', 'completed', 'absent', 'cancelled'] as ShiftStatus[]).map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors capitalize ${
              statusFilter === s
                ? 'bg-[#6C8CFF] text-white'
                : 'bg-[#1D212A] text-[#8A93A6] border border-[#262B35] hover:border-[#6C8CFF]/50'
            }`}
          >
            {s === 'all' ? 'All' : STATUS_LABEL[s]}
          </button>
        ))}
        <span className="text-xs text-[#5C6478] ml-auto">{filtered.length} shifts</span>
      </div>

      {filtered.length === 0 ? (
        <div className="py-10 text-center text-sm text-[#5C6478]">No shifts match the current filters.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#1D212A] text-[#8A93A6] font-mono border-b border-[#262B35]">
              <tr>
                <th className="px-5 py-3">Employee</th>
                <th className="px-5 py-3">Outlet</th>
                <th className="px-5 py-3">Role</th>
                <th className="px-5 py-3">Shift Date</th>
                <th className="px-5 py-3">Scheduled Hours</th>
                <th className="px-5 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#262B35]">
              {filtered.map((shift) => (
                <tr key={shift.id} className="hover:bg-[#1D212A]/50 transition-colors">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-[#262B35] flex items-center justify-center text-[#6C8CFF] flex-shrink-0">
                        <User className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <span className="font-semibold text-[#EDEFF3] block">{shift.employeeName}</span>
                        <span className="text-[10px] font-mono text-[#5C6478]">{shift.id}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-[#EDEFF3]">{shift.outletName}</td>
                  <td className="px-5 py-3.5 text-[#8A93A6]">{shift.role}</td>
                  <td className="px-5 py-3.5 font-mono text-[#8A93A6]">{shift.shiftDate}</td>
                  <td className="px-5 py-3.5 font-mono text-[#EDEFF3]">
                    <span className="inline-flex items-center gap-1">
                      <Clock className="w-3 h-3 text-[#5C6478]" />
                      {shift.shiftHours}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <Badge variant={STATUS_BADGE[shift.status] || 'default'} size="sm">
                      {STATUS_LABEL[shift.status] || shift.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
