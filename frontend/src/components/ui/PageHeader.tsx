import React from 'react';
import { cn } from '@/utils/cn';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  breadcrumbs?: Array<{ label: string; href?: string }>;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  badge,
  actions,
  breadcrumbs,
  className,
}) => (
  <div className={cn('mb-6', className)}>
    {/* Breadcrumbs */}
    {breadcrumbs && breadcrumbs.length > 0 && (
      <nav className="flex items-center gap-1.5 mb-2" aria-label="Breadcrumb">
        {breadcrumbs.map((crumb, i) => (
          <React.Fragment key={crumb.label}>
            {i > 0 && (
              <span className="text-[#5C6478] text-xs">/</span>
            )}
            {crumb.href ? (
              <a
                href={crumb.href}
                className="text-xs text-[#5C6478] hover:text-[#8992A6] transition-colors"
              >
                {crumb.label}
              </a>
            ) : (
              <span className="text-xs text-[#8992A6]">{crumb.label}</span>
            )}
          </React.Fragment>
        ))}
      </nav>
    )}

    {/* Title row */}
    <div className="flex items-start justify-between gap-4">
      <div className="min-w-0">
        <div className="flex items-center gap-2.5 flex-wrap">
          <h1 className="text-2xl font-bold text-[#EDEFF3] tracking-tight font-display leading-tight">
            {title}
          </h1>
          {badge}
        </div>
        {subtitle && (
          <p className="mt-1 text-sm text-[#5C6478] leading-relaxed">{subtitle}</p>
        )}
      </div>

      {actions && (
        <div className="flex items-center gap-2 shrink-0 mt-0.5">{actions}</div>
      )}
    </div>
  </div>
);
