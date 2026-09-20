import React from 'react';
import { cn } from '@/utils/cn';
import type { HealthStatus } from '@/types';

type StatusType =
  | HealthStatus                      // Healthy | At Risk | Critical
  | 'Low Stock' | 'Overstock' | 'Normal' | 'Critical' // Inventory
  | 'SHORTAGE' | 'OVERSTAFFED'        // Workforce
  | 'LOW_STOCK' | 'CRITICAL' | 'OVERSTOCK'  // Inventory alerts
  | 'Active' | 'Completed' | 'Cancelled' | 'Planned'  // Marketing
  | 'online' | 'degraded' | 'offline'; // System status

const STATUS_CONFIG: Record<string, { label: string; className: string; dot?: string }> = {
  // Health
  Healthy: {
    label: 'Healthy',
    className: 'bg-[rgba(79,174,124,0.12)] text-[#4FAE7C] border border-[rgba(79,174,124,0.25)]',
    dot: 'bg-[#4FAE7C]',
  },
  'At Risk': {
    label: 'At Risk',
    className: 'bg-[rgba(232,163,61,0.12)] text-[#E8A33D] border border-[rgba(232,163,61,0.25)]',
    dot: 'bg-[#E8A33D]',
  },
  Critical: {
    label: 'Critical',
    className: 'bg-[rgba(208,85,90,0.14)] text-[#D0555A] border border-[rgba(208,85,90,0.25)]',
    dot: 'bg-[#D0555A]',
  },
  // Inventory
  'Low Stock': {
    label: 'Low Stock',
    className: 'bg-[rgba(232,163,61,0.12)] text-[#E8A33D] border border-[rgba(232,163,61,0.25)]',
    dot: 'bg-[#E8A33D]',
  },
  Overstock: {
    label: 'Overstock',
    className: 'bg-[rgba(108,140,255,0.12)] text-[#6C8CFF] border border-[rgba(108,140,255,0.25)]',
    dot: 'bg-[#6C8CFF]',
  },
  Normal: {
    label: 'Normal',
    className: 'bg-[rgba(79,174,124,0.12)] text-[#4FAE7C] border border-[rgba(79,174,124,0.25)]',
    dot: 'bg-[#4FAE7C]',
  },
  // Alert types
  LOW_STOCK: {
    label: 'Low Stock',
    className: 'bg-[rgba(232,163,61,0.12)] text-[#E8A33D] border border-[rgba(232,163,61,0.25)]',
    dot: 'bg-[#E8A33D]',
  },
  OVERSTOCK: {
    label: 'Overstock',
    className: 'bg-[rgba(108,140,255,0.12)] text-[#6C8CFF] border border-[rgba(108,140,255,0.25)]',
    dot: 'bg-[#6C8CFF]',
  },
  // Lowercase & custom aliases
  critical: {
    label: 'Critical',
    className: 'bg-[rgba(208,85,90,0.14)] text-[#D0555A] border border-[rgba(208,85,90,0.25)]',
    dot: 'bg-[#D0555A]',
  },
  low: {
    label: 'Low Stock',
    className: 'bg-[rgba(232,163,61,0.12)] text-[#E8A33D] border border-[rgba(232,163,61,0.25)]',
    dot: 'bg-[#E8A33D]',
  },
  optimal: {
    label: 'Optimal',
    className: 'bg-[rgba(79,174,124,0.12)] text-[#4FAE7C] border border-[rgba(79,174,124,0.25)]',
    dot: 'bg-[#4FAE7C]',
  },
  on_duty: {
    label: 'On Duty',
    className: 'bg-[rgba(79,174,124,0.12)] text-[#4FAE7C] border border-[rgba(79,174,124,0.25)]',
    dot: 'bg-[#4FAE7C]',
  },
  absent: {
    label: 'Absenteeism Alert',
    className: 'bg-[rgba(208,85,90,0.14)] text-[#D0555A] border border-[rgba(208,85,90,0.25)]',
    dot: 'bg-[#D0555A]',
  },
  // Workforce
  SHORTAGE: {
    label: 'Shortage',
    className: 'bg-[rgba(208,85,90,0.14)] text-[#D0555A] border border-[rgba(208,85,90,0.25)]',
    dot: 'bg-[#D0555A]',
  },
  OVERSTAFFED: {
    label: 'Overstaffed',
    className: 'bg-[rgba(108,140,255,0.12)] text-[#6C8CFF] border border-[rgba(108,140,255,0.25)]',
    dot: 'bg-[#6C8CFF]',
  },
  // Campaign
  Active: {
    label: 'Active',
    className: 'bg-[rgba(79,174,124,0.12)] text-[#4FAE7C] border border-[rgba(79,174,124,0.25)]',
    dot: 'bg-[#4FAE7C]',
  },
  Completed: {
    label: 'Completed',
    className: 'bg-[#262B35] text-[#8992A6] border border-[#262B35]',
    dot: 'bg-[#8992A6]',
  },
  Cancelled: {
    label: 'Cancelled',
    className: 'bg-[rgba(208,85,90,0.14)] text-[#D0555A] border border-[rgba(208,85,90,0.25)]',
    dot: 'bg-[#D0555A]',
  },
  Planned: {
    label: 'Planned',
    className: 'bg-[rgba(108,140,255,0.12)] text-[#6C8CFF] border border-[rgba(108,140,255,0.25)]',
    dot: 'bg-[#6C8CFF]',
  },
  // System
  online: {
    label: 'Online',
    className: 'bg-[rgba(79,174,124,0.12)] text-[#4FAE7C] border border-[rgba(79,174,124,0.25)]',
    dot: 'bg-[#4FAE7C]',
  },
  degraded: {
    label: 'Degraded',
    className: 'bg-[rgba(232,163,61,0.12)] text-[#E8A33D] border border-[rgba(232,163,61,0.25)]',
    dot: 'bg-[#E8A33D]',
  },
  offline: {
    label: 'Offline',
    className: 'bg-[rgba(208,85,90,0.14)] text-[#D0555A] border border-[rgba(208,85,90,0.25)]',
    dot: 'bg-[#D0555A]',
  },
};

const FALLBACK = {
  label: 'Unknown',
  className: 'bg-[#262B35] text-[#8992A6]',
  dot: 'bg-[#5C6478]',
};

export interface StatusBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: StatusType | string;
  type?: string;
  showDot?: boolean;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  type: _type,
  showDot = true,
  size = 'sm',
  className,
  ...props
}) => {
  const config = STATUS_CONFIG[status] ?? { ...FALLBACK, label: status };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-semibold leading-none',
        size === 'sm' ? 'text-[10px] px-2 py-1 tracking-wide uppercase' : 'text-xs px-2.5 py-1',
        config.className,
        className
      )}
      {...props}
    >
      {showDot && (
        <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', config.dot)} />
      )}
      {config.label}
    </span>
  );
};
