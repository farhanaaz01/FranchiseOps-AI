import React from 'react';
import { cn } from '@/utils/cn';
import { Card } from '@/components/ui/Card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { KPICardSkeleton } from '@/components/ui/LoadingState';

export interface KPICardProps {
  title: string;
  value: string | number;
  change?: number | string;
  changeType?: 'positive' | 'negative' | 'neutral';
  changeLabel?: string;
  subtext?: string;
  icon?: React.ReactNode;
  status?: 'healthy' | 'risk' | 'critical' | 'neutral';
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  changeType,
  changeLabel = 'vs last period',
  subtext,
  icon,
  status = 'neutral',
  loading = false,
  className,
  onClick,
}) => {
  if (loading) {
    return <KPICardSkeleton className={className} />;
  }

  // Auto-detect changeType if numeric
  let resolvedChangeType = changeType;
  if (!resolvedChangeType && change !== undefined) {
    const numChange = typeof change === 'string' ? parseFloat(change) : change;
    if (!isNaN(numChange)) {
      if (numChange > 0) resolvedChangeType = 'positive';
      else if (numChange < 0) resolvedChangeType = 'negative';
      else resolvedChangeType = 'neutral';
    }
  }

  const statusBorderColor = {
    healthy: 'border-l-2 border-l-[#4FAE7C]',
    risk: 'border-l-2 border-l-[#E8A33D]',
    critical: 'border-l-2 border-l-[#D0555A]',
    neutral: '',
  }[status];

  return (
    <Card
      className={cn(
        'p-5 transition-all duration-150 hover:border-[#3A4155]',
        statusBorderColor,
        onClick && 'cursor-pointer hover:bg-[#1D212A]',
        className
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium text-[#8A93A6] tracking-wide uppercase font-mono">
          {title}
        </span>
        {icon && (
          <div className="p-2 rounded-lg bg-[#1D212A] text-[#8A93A6] border border-[#262B35]">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold text-[#EDEFF3] font-mono tracking-tight">
          {value}
        </div>

        {(change !== undefined || subtext) && (
          <div className="flex items-center gap-1.5 mt-2 flex-wrap text-xs">
            {change !== undefined && (
              <span
                className={cn(
                  'inline-flex items-center gap-0.5 font-medium font-mono',
                  resolvedChangeType === 'positive' && 'text-[#4FAE7C]',
                  resolvedChangeType === 'negative' && 'text-[#D0555A]',
                  resolvedChangeType === 'neutral' && 'text-[#8A93A6]'
                )}
              >
                {resolvedChangeType === 'positive' && <TrendingUp className="w-3.5 h-3.5" />}
                {resolvedChangeType === 'negative' && <TrendingDown className="w-3.5 h-3.5" />}
                {resolvedChangeType === 'neutral' && <Minus className="w-3.5 h-3.5" />}
                <span>
                  {typeof change === 'number' && change > 0 ? `+${change}%` : `${change}%`}
                </span>
              </span>
            )}

            {changeLabel && (
              <span className="text-[#5C6478]">{changeLabel}</span>
            )}

            {subtext && !changeLabel && (
              <span className="text-[#5C6478]">{subtext}</span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
