// Re-exports and common UI types
export * from './backend';
export * from './pipeline';

// ---- UI / Navigation ----
export type NavSection = 'MAIN' | 'OPERATIONS' | 'INTELLIGENCE' | 'SYSTEM';

export interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  section: NavSection;
  badge?: number | null;
}

// ---- API State ----
export type LoadingStatus = 'idle' | 'loading' | 'success' | 'error';

export interface ApiState<T> {
  data: T | null;
  status: LoadingStatus;
  error: string | null;
}

// ---- System Status ----
export type SystemStatusLevel = 'online' | 'degraded' | 'offline';

export interface SystemStatus {
  level: SystemStatusLevel;
  label: string;
  lastChecked: string;
}

// ---- Date Range ----
export interface DateRange {
  start: string | null;
  end: string | null;
  label: string;
}

// ---- Pagination ----
export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

// ---- Alert Types (UI) ----
export type AlertSeverity = 'info' | 'warning' | 'error' | 'success';

export interface UIAlert {
  id: string;
  severity: AlertSeverity;
  title: string;
  message: string;
  timestamp: string;
  dismissed: boolean;
}
