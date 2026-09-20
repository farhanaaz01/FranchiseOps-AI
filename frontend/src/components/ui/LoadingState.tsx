import React from 'react';
import { cn } from '@/utils/cn';

// ---- Skeleton ----
interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number;
  height?: string | number;
  rounded?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height = 16,
  rounded = false,
  className,
  style,
  ...props
}) => (
  <div
    className={cn('skeleton', rounded ? 'rounded-full' : 'rounded', className)}
    style={{ width, height, ...style }}
    {...props}
  />
);

// ---- Full Page Loading Spinner ----
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const spinnerSizes = {
  sm: 'w-5 h-5 border-2',
  md: 'w-8 h-8 border-[3px]',
  lg: 'w-12 h-12 border-4',
};

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className }) => (
  <div
    className={cn(
      'rounded-full border-[#262B35] border-t-[#6C8CFF] animate-spin',
      spinnerSizes[size],
      className
    )}
  />
);

// ---- LoadingState ----
interface LoadingStateProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading data...',
  size = 'md',
  className,
}) => (
  <div className={cn('flex flex-col items-center justify-center gap-3 py-12', className)}>
    <Spinner size={size} />
    <p className="text-sm text-[#5C6478]">{message}</p>
  </div>
);

// ---- Card Skeleton (for dashboard placeholders) ----
interface CardSkeletonProps {
  lines?: number;
  hasHeader?: boolean;
  className?: string;
}

export const CardSkeleton: React.FC<CardSkeletonProps> = ({
  lines = 3,
  hasHeader = true,
  className,
}) => (
  <div className={cn('rounded-[12px] border border-[#262B35] bg-[#171A20] p-5', className)}>
    {hasHeader && (
      <div className="flex items-center justify-between mb-4">
        <Skeleton width={120} height={14} />
        <Skeleton width={60} height={14} />
      </div>
    )}
    <div className="space-y-2.5">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} width={i === 0 ? '100%' : `${70 - i * 12}%`} height={12} />
      ))}
    </div>
  </div>
);

// ---- KPI Skeleton ----
export const KPICardSkeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('rounded-[12px] border border-[#262B35] bg-[#171A20] p-5', className)}>
    <Skeleton width={80} height={11} className="mb-3" />
    <Skeleton width={100} height={32} className="mb-2" />
    <Skeleton width={60} height={11} />
  </div>
);
