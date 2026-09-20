import React from 'react';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Button } from '@/components/ui/Button';
import { ArrowRight, TrendingUp, TrendingDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { EnrichedOutlet } from '@/hooks/useOutlets';

interface OutletTableProps {
  outlets: EnrichedOutlet[];
}

export const OutletTable: React.FC<OutletTableProps> = ({ outlets }) => {
  const navigate = useNavigate();

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs text-left">
        <thead className="bg-[#1D212A] text-[#8A93A6] font-mono border-b border-[#262B35]">
          <tr>
            <th className="px-5 py-3">Outlet ID</th>
            <th className="px-5 py-3">Outlet Name</th>
            <th className="px-5 py-3">Location</th>
            <th className="px-5 py-3">Health Status</th>
            <th className="px-5 py-3">Health Score</th>
            <th className="px-5 py-3">Revenue</th>
            <th className="px-5 py-3">Growth</th>
            <th className="px-5 py-3">Store Manager</th>
            <th className="px-5 py-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#262B35]">
          {outlets.map((outlet) => {
            const isPositive = !outlet.growth.startsWith('-');
            return (
              <tr key={outlet.id} className="hover:bg-[#1D212A]/50 transition-colors">
                <td className="px-5 py-3.5 font-mono text-[#6C8CFF] font-medium">{outlet.id}</td>
                <td className="px-5 py-3.5 font-medium text-[#EDEFF3]">{outlet.name}</td>
                <td className="px-5 py-3.5 text-[#8A93A6]">{outlet.location}</td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={outlet.status} size="sm" />
                </td>
                <td className="px-5 py-3.5 font-mono font-bold text-[#EDEFF3]">
                  {outlet.healthScore}
                  <span className="text-[10px] text-[#5C6478] font-normal ml-0.5">/100</span>
                </td>
                <td className="px-5 py-3.5 font-mono text-[#EDEFF3] font-medium">{outlet.revenue}</td>
                <td className="px-5 py-3.5 font-mono">
                  <span className={`inline-flex items-center gap-0.5 ${isPositive ? 'text-[#4FAE7C]' : 'text-[#D0555A]'}`}>
                    {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {outlet.growth}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-[#8A93A6]">{outlet.manager}</td>
                <td className="px-5 py-3.5 text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(`/outlets/${outlet.outlet_id || outlet.id}`)}
                    className="text-[#6C8CFF] hover:text-[#8EAEFF] inline-flex items-center gap-1"
                  >
                    View <ArrowRight className="w-3 h-3" />
                  </Button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
