import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  X,
  Store,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  Layers,
  FileText,
  Settings,
  Bot,
  ShieldCheck,
  TrendingUp,
  Package,
  Users,
  LayoutDashboard,
  CornerDownLeft,
} from 'lucide-react';
import { useOutlets } from '@/hooks/useOutlets';
import { useAlerts } from '@/hooks/useAlerts';
import { useIntelligence } from '@/hooks/useIntelligence';
import { cn } from '@/utils/cn';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface QuickNavAction {
  title: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  badge?: string;
  desc: string;
}

const QUICK_ACTIONS: QuickNavAction[] = [
  { title: 'Overview', path: '/', icon: LayoutDashboard, color: '#6C8CFF', desc: 'Main network executive view' },
  { title: 'Outlets Directory', path: '/outlets', icon: Store, color: '#6C8CFF', desc: 'Multi-unit operational registry' },
  { title: 'Inventory Replenishment', path: '/inventory', icon: Package, color: '#F2A73B', desc: 'Stock health & automated POs' },
  { title: 'Workforce & Rostering', path: '/workforce', icon: Users, color: '#3AA99F', desc: 'Staff shifts, attendance & wage ratio' },
  { title: 'Marketing Attribution', path: '/marketing', icon: TrendingUp, color: '#A78BFA', desc: 'Campaign ROAS, CAC & budget telemetry' },
  { title: 'Audit & Compliance', path: '/audit', icon: ShieldCheck, color: '#3AA99F', desc: 'Inspection audits & safety checklist' },
  { title: 'AI Insights & Predictions', path: '/ai-insights', icon: Sparkles, color: '#6C8CFF', desc: 'Feature importance & predictive scoring' },
  { title: 'Decision Center', path: '/decision-center', icon: Layers, color: '#F2A73B', desc: 'Prioritized operational action queue' },
  { title: 'Alerts & Incidents', path: '/alerts', icon: AlertTriangle, color: '#D0555A', desc: 'Real-time telemetry breach events' },
  { title: 'Agent Activity Center', path: '/agent-activity', icon: Bot, color: '#6C8CFF', desc: 'Domain orchestrator telemetry & run logs' },
  { title: 'Enterprise Reports', path: '/reports', icon: FileText, color: '#3AA99F', desc: 'Network CSV exports & executive summaries' },
  { title: 'System Settings', path: '/settings', icon: Settings, color: '#8A93A6', desc: 'Session preferences & API gateway telemetry' },
];

const PREDEFINED_REPORTS = [
  { title: 'Network Performance Matrix', category: 'Operations', path: '/reports' },
  { title: 'Inventory Wastage & Stockout Report', category: 'Operations', path: '/reports' },
  { title: 'Labour Productivity & Overtime Report', category: 'Finance', path: '/reports' },
  { title: 'Marketing CAC & ROAS Attribution', category: 'Finance', path: '/reports' },
  { title: 'Regulatory Compliance & Food Safety Audit', category: 'Risk & Compliance', path: '/reports' },
  { title: 'Critical Risk & Failure Prevention Log', category: 'Risk & Compliance', path: '/reports' },
];

export const SearchModal: React.FC<SearchModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const { outlets } = useOutlets();
  const { alerts } = useAlerts();
  const { rootCauses } = useIntelligence();

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Global keydown handler for Esc and navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const searchResults = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return null;

    const matchedOutlets = outlets
      .filter(
        (o) =>
          o.name.toLowerCase().includes(q) ||
          o.id.toLowerCase().includes(q) ||
          o.location.toLowerCase().includes(q)
      )
      .slice(0, 3);

    const matchedAlerts = alerts
      .filter(
        (a) =>
          a.title.toLowerCase().includes(q) ||
          a.description.toLowerCase().includes(q) ||
          a.outletId.toLowerCase().includes(q) ||
          a.severity.toLowerCase().includes(q)
      )
      .slice(0, 3);

    const matchedFindings: Array<{
      outletId: string;
      finding: string;
      recommendation: string;
      domain: string;
    }> = [];

    rootCauses.forEach((rc) => {
      rc.issues.forEach((issue) => {
        if (
          issue.finding.toLowerCase().includes(q) ||
          issue.recommendation.toLowerCase().includes(q) ||
          issue.domain.toLowerCase().includes(q) ||
          rc.outlet_id.toLowerCase().includes(q)
        ) {
          matchedFindings.push({
            outletId: rc.outlet_id,
            finding: issue.finding,
            recommendation: issue.recommendation,
            domain: issue.domain,
          });
        }
      });
    });

    const matchedPages = QUICK_ACTIONS.filter(
      (p) => p.title.toLowerCase().includes(q) || p.desc.toLowerCase().includes(q)
    ).slice(0, 4);

    const matchedReports = PREDEFINED_REPORTS.filter(
      (r) => r.title.toLowerCase().includes(q) || r.category.toLowerCase().includes(q)
    ).slice(0, 3);

    return {
      outlets: matchedOutlets,
      alerts: matchedAlerts,
      findings: matchedFindings.slice(0, 3),
      pages: matchedPages,
      reports: matchedReports,
    };
  }, [query, outlets, alerts, rootCauses]);

  const flattenedResults = useMemo(() => {
    if (!searchResults) return [];
    const list: Array<{ type: string; title: string; subtitle?: string; path: string }> = [];

    searchResults.pages.forEach((p) => {
      list.push({ type: 'Page', title: p.title, subtitle: p.desc, path: p.path });
    });
    searchResults.outlets.forEach((o) => {
      list.push({ type: 'Outlet', title: o.name, subtitle: `${o.id} • ${o.location}`, path: `/outlets/${o.id}` });
    });
    searchResults.reports.forEach((r) => {
      list.push({ type: 'Report', title: r.title, subtitle: r.category, path: r.path });
    });
    searchResults.alerts.forEach((a) => {
      list.push({ type: 'Alert', title: a.title, subtitle: `${a.severity.toUpperCase()} • ${a.outletId}`, path: '/alerts' });
    });
    searchResults.findings.forEach((f) => {
      list.push({ type: 'AI Finding', title: f.finding, subtitle: `${f.outletId} • ${f.recommendation}`, path: '/decision-center' });
    });

    return list;
  }, [searchResults]);

  // Handle arrow key navigation in results
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!flattenedResults.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % flattenedResults.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + flattenedResults.length) % flattenedResults.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const target = flattenedResults[selectedIndex];
      if (target) {
        navigate(target.path);
        onClose();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 bg-black/75 backdrop-blur-xs select-none">
      <div className="w-full max-w-2xl bg-[#12141A] border border-[#262B35] rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-150">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-[#262B35] bg-[#171A20]">
          <Search className="w-4 h-4 text-[#6C8CFF] shrink-0 mr-3" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleInputKeyDown}
            placeholder="Search outlets, alerts, metrics, reports, or navigate anywhere..."
            className="w-full bg-transparent text-sm text-[#EDEFF3] placeholder-[#5C6478] focus:outline-none"
          />
          <div className="flex items-center gap-1.5 ml-2">
            <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono text-[#8A93A6] bg-[#12141A] rounded border border-[#262B35]">
              ESC
            </kbd>
            <button
              onClick={onClose}
              className="p-1 text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#1D212A] rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Status Bar */}
        <div className="px-4 py-1.5 bg-[#171A20]/80 border-b border-[#262B35] flex items-center justify-between text-[10px] font-mono text-[#5C6478]">
          <span>FranchiseOps AI Unified Command Index</span>
          <span className="flex items-center gap-1.5">
            <span>Navigate</span>
            <kbd className="bg-[#12141A] px-1 rounded border border-[#262B35]">↑↓</kbd>
            <span>Select</span>
            <kbd className="bg-[#12141A] px-1 rounded border border-[#262B35]">↵</kbd>
          </span>
        </div>

        {/* Results / Navigation Body */}
        <div className="overflow-y-auto p-4 space-y-5 flex-1">
          {query.trim() === '' ? (
            <>
              {/* Quick Actions (12 Core Modules) */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono uppercase text-[#5C6478] tracking-wider font-semibold">
                    Quick Navigation (12 Modules)
                  </span>
                  <span className="text-[10px] font-mono text-[#5C6478]">Direct jump</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {QUICK_ACTIONS.map((action) => {
                    const Icon = action.icon;
                    return (
                      <button
                        key={action.path}
                        onClick={() => {
                          navigate(action.path);
                          onClose();
                        }}
                        className="p-2.5 rounded-lg bg-[#171A20] hover:bg-[#1D212A] border border-[#262B35] hover:border-[#3A4155] transition-all text-left flex items-start gap-2.5 group"
                      >
                        <div
                          className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
                          style={{ backgroundColor: `${action.color}15`, color: action.color }}
                        >
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-semibold text-[#EDEFF3] group-hover:text-white truncate">
                            {action.title}
                          </p>
                          <p className="text-[10px] text-[#5C6478] truncate mt-0.5">
                            {action.desc}
                          </p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Suggested Queries */}
              <div className="space-y-2 pt-2 border-t border-[#262B35]/60">
                <span className="text-[10px] font-mono uppercase text-[#5C6478] tracking-wider font-semibold">
                  Suggested Telemetry Queries
                </span>
                <div className="flex flex-wrap gap-2">
                  {['Inventory wastage', 'Downtown Flagship', 'High labour ratio', 'Food safety audit', 'CAC attribution', 'Agent orchestrator'].map(
                    (suggested) => (
                      <button
                        key={suggested}
                        onClick={() => setQuery(suggested)}
                        className="px-2.5 py-1 text-xs font-mono text-[#8A93A6] bg-[#171A20] hover:bg-[#1D212A] hover:text-[#EDEFF3] rounded-lg border border-[#262B35] transition-colors"
                      >
                        "{suggested}"
                      </button>
                    )
                  )}
                </div>
              </div>
            </>
          ) : flattenedResults.length === 0 ? (
            <div className="py-12 text-center text-xs text-[#5C6478] space-y-1">
              <p>No operational records matched "{query}".</p>
              <p className="text-[11px] text-[#3A4155]">Try searching by outlet ID (OUT-01), metric name, or page title.</p>
            </div>
          ) : (
            <div className="space-y-1">
              <div className="text-[10px] font-mono uppercase text-[#5C6478] tracking-wider mb-2">
                Found {flattenedResults.length} matches across operational telemetry
              </div>
              {flattenedResults.map((item, idx) => {
                const isSelected = idx === selectedIndex;
                return (
                  <button
                    key={`${item.type}-${idx}`}
                    onClick={() => {
                      navigate(item.path);
                      onClose();
                    }}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={cn(
                      'w-full text-left p-2.5 rounded-lg border transition-all flex items-center justify-between gap-3 group',
                      isSelected
                        ? 'bg-[#1D212A] border-[#6C8CFF]/50 shadow-xs'
                        : 'bg-[#171A20] border-[#262B35] hover:border-[#3A4155]'
                    )}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span
                        className={cn(
                          'text-[9px] font-mono uppercase px-1.5 py-0.5 rounded shrink-0 font-semibold',
                          item.type === 'Page' && 'bg-[#6C8CFF]/10 text-[#6C8CFF]',
                          item.type === 'Outlet' && 'bg-[#3AA99F]/10 text-[#3AA99F]',
                          item.type === 'Report' && 'bg-[#A78BFA]/10 text-[#A78BFA]',
                          item.type === 'Alert' && 'bg-[#D0555A]/10 text-[#D0555A]',
                          item.type === 'AI Finding' && 'bg-[#F2A73B]/10 text-[#F2A73B]'
                        )}
                      >
                        {item.type}
                      </span>
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-[#EDEFF3] group-hover:text-white truncate">
                          {item.title}
                        </p>
                        {item.subtitle && (
                          <p className="text-[10px] text-[#8A93A6] truncate mt-0.5">
                            {item.subtitle}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {isSelected && (
                        <span className="hidden sm:flex items-center gap-1 text-[10px] font-mono text-[#6C8CFF]">
                          <span>Enter</span>
                          <CornerDownLeft className="w-3 h-3" />
                        </span>
                      )}
                      <ArrowRight className="w-3.5 h-3.5 text-[#5C6478] group-hover:text-[#EDEFF3] transition-colors" />
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
