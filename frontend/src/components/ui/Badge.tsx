import React from 'react';
import { cn } from '@/utils/cn';

type BadgeVariant = 'default' | 'accent' | 'success' | 'warning' | 'danger' | 'outline' | 'neutral';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-[#262B35] text-[#8992A6]',
  neutral: 'bg-[#262B35] text-[#8992A6]',
  accent: 'bg-[rgba(108,140,255,0.12)] text-[#6C8CFF] border border-[rgba(108,140,255,0.25)]',
  success: 'bg-[rgba(79,174,124,0.12)] text-[#4FAE7C] border border-[rgba(79,174,124,0.25)]',
  warning: 'bg-[rgba(232,163,61,0.12)] text-[#E8A33D] border border-[rgba(232,163,61,0.25)]',
  danger: 'bg-[rgba(208,85,90,0.14)] text-[#D0555A] border border-[rgba(208,85,90,0.25)]',
  outline: 'bg-transparent text-[#8992A6] border border-[#262B35]',
};

const sizeClasses = {
  sm: 'text-[10px] px-2 py-0.5 font-semibold tracking-wide',
  md: 'text-xs px-2.5 py-1 font-medium',
};

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = 'default', size = 'sm', className, children, ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        'inline-flex items-center gap-1 rounded-full leading-none',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  )
);
Badge.displayName = 'Badge';
