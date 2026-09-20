import React from 'react';
import { cn } from '@/utils/cn';

// ---- Card Root ----
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Use the slightly lighter panel-alt background */
  alt?: boolean;
  /** Hover state border highlight */
  hoverable?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ alt, hoverable, className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'rounded-[12px] border border-[#262B35] transition-all duration-150',
        alt ? 'bg-[#1D212A]' : 'bg-[#171A20]',
        hoverable && 'hover:border-[#3A4155] cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);
Card.displayName = 'Card';

// ---- Card Header ----
interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Add bottom border separator */
  separator?: boolean;
}

export const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ separator, className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'flex items-center justify-between px-5 py-4',
        separator && 'border-b border-[#262B35]',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);
CardHeader.displayName = 'CardHeader';

// ---- Card Title ----
export const CardTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, children, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn('text-sm font-semibold text-[#EDEFF3] font-display tracking-tight', className)}
      {...props}
    >
      {children}
    </h3>
  )
);
CardTitle.displayName = 'CardTitle';

// ---- Card Description ----
export const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, children, ...props }, ref) => (
    <p
      ref={ref}
      className={cn('text-xs text-[#5C6478] mt-0.5', className)}
      {...props}
    >
      {children}
    </p>
  )
);
CardDescription.displayName = 'CardDescription';

// ---- Card Content ----
export const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('px-5 py-4', className)}
      {...props}
    >
      {children}
    </div>
  )
);
CardContent.displayName = 'CardContent';

// ---- Card Footer ----
export const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('px-5 py-3 border-t border-[#262B35] flex items-center', className)}
      {...props}
    >
      {children}
    </div>
  )
);
CardFooter.displayName = 'CardFooter';
