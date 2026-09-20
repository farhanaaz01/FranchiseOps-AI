import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Button } from '@/components/ui/Button';
import { MapPin, ArrowRight, UserCheck, TrendingUp, TrendingDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { EnrichedOutlet } from '@/hooks/useOutlets';

interface OutletCardProps {
  outlet: EnrichedOutlet;
}

export const OutletCard: React.FC<OutletCardProps> = ({ outlet }) => {
  const navigate = useNavigate();
  const isPositiveGrowth = !outlet.growth.startsWith('-');

  return (
    <Card className="hover:border-[#6C8CFF]/50 transition-all duration-200">
      <CardContent className="p-5 space-y-4">
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-[#6C8CFF] bg-[#6C8CFF]/10 px-2 py-0.5 rounded">
              {outlet.id}
            </span>
            <h3 className="text-base font-semibold text-[#EDEFF3] mt-1">{outlet.name}</h3>
            <div className="flex items-center gap-1 text-xs text-[#8A93A6] mt-0.5">
              <MapPin className="w-3 h-3 text-[#5C6478]" />
              <span>{outlet.location}</span>
            </div>
          </div>
          <StatusBadge status={outlet.status} size="sm" />
        </div>

        <div className="grid grid-cols-2 gap-3 py-3 border-y border-[#262B35] bg-[#171A20]/40 rounded-lg px-3">
          <div>
            <span className="text-[11px] text-[#5C6478] block">Health Score</span>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-lg font-bold font-mono text-[#EDEFF3]">{outlet.healthScore}</span>
              <span className="text-[10px] text-[#5C6478]">/ 100</span>
            </div>
          </div>
          <div>
            <span className="text-[11px] text-[#5C6478] block">Revenue & Growth</span>
            <div className="flex items-baseline gap-1.5 mt-0.5">
              <span className="text-sm font-bold font-mono text-[#EDEFF3]">{outlet.revenue}</span>
              <span className={`text-xs font-mono flex items-center ${isPositiveGrowth ? 'text-[#4FAE7C]' : 'text-[#D0555A]'}`}>
                {isPositiveGrowth ? <TrendingUp className="w-3 h-3 mr-0.5" /> : <TrendingDown className="w-3 h-3 mr-0.5" />}
                {outlet.growth}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-[#8A93A6] pt-1">
          <div className="flex items-center gap-1.5">
            <UserCheck className="w-3.5 h-3.5 text-[#5C6478]" />
            <span className="truncate max-w-[140px]">{outlet.manager}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/outlets/${outlet.outlet_id || outlet.id}`)}
            className="text-[#6C8CFF] hover:text-[#8EAEFF] p-0 h-auto font-medium text-xs flex items-center gap-1"
          >
            Details <ArrowRight className="w-3 h-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
