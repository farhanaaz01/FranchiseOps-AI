import React from 'react';
import { cn } from '@/utils/cn';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title?: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title = 'No data found',
  description = 'There is nothing to display here yet.',
  action,
  className,
}) => (
  <div
    className={cn(
      'flex flex-col items-center justify-center gap-4 py-16 px-6 text-center',
      className
    )}
  >
    {icon && (
      <div className="w-12 h-12 rounded-full bg-[#1D212A] flex items-center justify-center text-[#5C6478]">
        {icon}
      </div>
    )}
    <div>
      <p className="text-sm font-semibold text-[#8992A6] mb-1">{title}</p>
      <p className="text-xs text-[#5C6478] max-w-xs leading-relaxed">{description}</p>
    </div>
    {action && <div className="mt-1">{action}</div>}
  </div>
);
