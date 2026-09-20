import React from 'react';
import { cn } from '@/utils/cn';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  icon?: React.ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-[#6C8CFF] hover:bg-[#7A9AFF] text-white border border-transparent ' +
    'focus-visible:ring-2 focus-visible:ring-[#6C8CFF] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0E1013]',
  secondary:
    'bg-[#1D212A] hover:bg-[#262B35] text-[#EDEFF3] border border-[#262B35] ' +
    'focus-visible:ring-2 focus-visible:ring-[#6C8CFF] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0E1013]',
  outline:
    'bg-transparent hover:bg-[#1D212A] text-[#EDEFF3] border border-[#262B35] ' +
    'focus-visible:ring-2 focus-visible:ring-[#6C8CFF] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0E1013]',
  ghost:
    'bg-transparent hover:bg-[#1D212A] text-[#8992A6] hover:text-[#EDEFF3] border border-transparent ' +
    'focus-visible:ring-2 focus-visible:ring-[#6C8CFF] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0E1013]',
  danger:
    'bg-[#D0555A]/10 hover:bg-[#D0555A]/20 text-[#D0555A] border border-[#D0555A]/25 ' +
    'focus-visible:ring-2 focus-visible:ring-[#D0555A] focus-visible:ring-offset-2 focus-visible:ring-offset-[#0E1013]',
};

const sizeClasses: Record<ButtonSize, string> = {
  xs: 'h-6 px-2.5 text-xs gap-1',
  sm: 'h-8 px-3 text-xs gap-1.5',
  md: 'h-9 px-4 text-sm gap-2',
  lg: 'h-10 px-5 text-sm gap-2',
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'secondary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      icon,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;
    const leadingIcon = leftIcon || icon;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={cn(
          'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 select-none outline-none',
          variantClasses[variant],
          sizeClasses[size],
          isDisabled && 'opacity-50 cursor-not-allowed pointer-events-none',
          className
        )}
        {...props}
      >
        {loading ? (
          <svg
            className="animate-spin w-4 h-4 shrink-0"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        ) : (
          leadingIcon && <span className="shrink-0">{leadingIcon}</span>
        )}
        {children}
        {!loading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
