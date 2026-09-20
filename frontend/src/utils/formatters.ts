import type { HealthStatus } from '@/types';

// ---- Currency ----
/**
 * Format a number or decimal string as USD currency.
 * Backend returns Decimal fields as strings.
 */
export function formatCurrency(value: number | string, compact = false): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';

  if (compact) {
    if (Math.abs(num) >= 1_000_000) {
      return `$${(num / 1_000_000).toFixed(1)}M`;
    }
    if (Math.abs(num) >= 1_000) {
      return `$${(num / 1_000).toFixed(1)}K`;
    }
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
}

// ---- Percentage ----
export function formatPercent(value: number | string, decimals = 1): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`;
}

export function formatPercentAbs(value: number | string, decimals = 1): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  return `${num.toFixed(decimals)}%`;
}

// ---- Numbers ----
export function formatNumber(value: number | string, compact = false): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';

  if (compact) {
    if (Math.abs(num) >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (Math.abs(num) >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  }

  return new Intl.NumberFormat('en-US').format(num);
}

// ---- Dates ----
export function formatDate(dateStr: string, style: 'short' | 'medium' | 'long' = 'medium'): string {
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;

    const options: Intl.DateTimeFormatOptions = {
      short: { month: 'short', day: 'numeric' },
      medium: { month: 'short', day: 'numeric', year: 'numeric' },
      long: { month: 'long', day: 'numeric', year: 'numeric' },
    }[style] as Intl.DateTimeFormatOptions;

    return new Intl.DateTimeFormat('en-US', options).format(date);
  } catch {
    return dateStr;
  }
}

export function formatDateTime(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch {
    return dateStr;
  }
}

export function formatRelativeTime(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    const diffMs = Date.now() - date.getTime();
    const diffMins = Math.floor(diffMs / 60_000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs}h ago`;
    const diffDays = Math.floor(diffHrs / 24);
    if (diffDays < 7) return `${diffDays}d ago`;
    return formatDate(dateStr);
  } catch {
    return dateStr;
  }
}

// ---- Health Score ----
export function formatHealthScore(value: number | string): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  return num.toFixed(1);
}

// ---- Performance Label → Status ----
export function performanceLabelToHealth(label: string): HealthStatus {
  const l = label.toLowerCase();
  if (l.includes('healthy') || l.includes('top') || l.includes('excellent')) return 'Healthy';
  if (l.includes('risk') || l.includes('warning') || l.includes('moderate')) return 'At Risk';
  return 'Critical';
}

// ---- Health Score → HealthStatus ----
export function scoreToHealth(score: number | string): HealthStatus {
  const num = typeof score === 'string' ? parseFloat(score) : score;
  if (isNaN(num)) return 'Critical';
  if (num >= 70) return 'Healthy';
  if (num >= 50) return 'At Risk';
  return 'Critical';
}

// ---- Stock quantity ----
export function formatStock(value: number | string, unit = ''): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  const formatted = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(num);
  return unit ? `${formatted} ${unit}` : formatted;
}
