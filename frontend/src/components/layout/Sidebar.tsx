import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { cn } from '@/utils/cn';
import {
  LayoutDashboard,
  Store,
  Package,
  Users,
  Megaphone,
  ClipboardCheck,
  Sparkles,
  AlertTriangle,
  Bot,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
  Layers,
  Target,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

interface NavItemConfig {
  id: string;
  label: string;
  path: string;
  icon: React.ElementType;
  badge?: string | number;
  badgeColor?: 'accent' | 'warning' | 'critical';
}

const mainNav: NavItemConfig[] = [
  { id: 'overview', label: 'Overview', path: '/', icon: LayoutDashboard },
];

const operationsNav: NavItemConfig[] = [
  { id: 'outlets', label: 'Outlets', path: '/outlets', icon: Store },
  { id: 'inventory', label: 'Inventory', path: '/inventory', icon: Package },
  { id: 'workforce', label: 'Workforce', path: '/workforce', icon: Users },
  { id: 'marketing', label: 'Marketing', path: '/marketing', icon: Megaphone },
  { id: 'audit', label: 'Audit & Compliance', path: '/audit', icon: ClipboardCheck },
];

const intelligenceNav: NavItemConfig[] = [
  { id: 'ai-insights', label: 'AI Insights', path: '/ai-insights', icon: Sparkles, badge: 'AI', badgeColor: 'accent' },
  { id: 'decision-center', label: 'Decision Center', path: '/decision-center', icon: Target, badge: 'NEW', badgeColor: 'accent' },
  { id: 'alerts', label: 'Alerts', path: '/alerts', icon: AlertTriangle, badge: '3', badgeColor: 'warning' },
  { id: 'agent-activity', label: 'Agent Activity', path: '/agent-activity', icon: Bot },
];

const systemNav: NavItemConfig[] = [
  { id: 'reports', label: 'Reports', path: '/reports', icon: FileText },
  { id: 'settings', label: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  onToggleCollapse,
  mobileOpen = false,
  onCloseMobile,
}) => {
  const location = useLocation();

  const renderNavGroup = (title: string | null, items: NavItemConfig[]) => (
    <div className="py-2">
      {title && !collapsed && (
        <div className="px-4 pb-2 text-[10px] font-semibold tracking-wider text-[#5C6478] uppercase font-mono">
          {title}
        </div>
      )}
      <div className="space-y-0.5 px-2">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = item.path === '/'
            ? location.pathname === '/'
            : location.pathname.startsWith(item.path);

          return (
            <NavLink
              key={item.id}
              to={item.path}
              onClick={onCloseMobile}
              title={collapsed ? item.label : undefined}
              className={cn(
                'group flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 relative',
                isActive
                  ? 'bg-[#1D212A] text-[#EDEFF3] font-semibold shadow-sm border border-[#262B35]'
                  : 'text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#171A20]'
              )}
            >
              {isActive && (
                <span className="absolute left-0 top-1.5 bottom-1.5 w-1 bg-[#6C8CFF] rounded-r" />
              )}
              <Icon
                className={cn(
                  'w-4 h-4 flex-shrink-0 transition-colors',
                  isActive ? 'text-[#6C8CFF]' : 'text-[#8A93A6] group-hover:text-[#EDEFF3]'
                )}
              />
              {!collapsed && (
                <span className="truncate flex-1">{item.label}</span>
              )}
              {!collapsed && item.badge && (
                <span
                  className={cn(
                    'px-1.5 py-0.5 text-[10px] font-mono rounded font-medium',
                    item.badgeColor === 'accent' && 'bg-[#6C8CFF]/15 text-[#6C8CFF] border border-[#6C8CFF]/30',
                    item.badgeColor === 'warning' && 'bg-[#E8A33D]/15 text-[#E8A33D] border border-[#E8A33D]/30',
                    item.badgeColor === 'critical' && 'bg-[#D0555A]/15 text-[#D0555A] border border-[#D0555A]/30'
                  )}
                >
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-xs lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={cn(
          'fixed lg:sticky top-0 left-0 z-50 h-screen flex flex-col bg-[#12141A] border-r border-[#262B35] transition-all duration-200 select-none',
          collapsed ? 'w-16' : 'w-64',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between h-14 px-4 border-b border-[#262B35]">
          {!collapsed ? (
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-lg bg-linear-to-br from-[#6C8CFF] to-[#3B5BDB] flex items-center justify-center text-white shadow-md shadow-[#6C8CFF]/20 flex-shrink-0">
                <Layers className="w-4 h-4" />
              </div>
              <div className="flex flex-col truncate">
                <span className="text-sm font-bold text-[#EDEFF3] font-display tracking-tight leading-tight">
                  FranchiseOps <span className="text-[#6C8CFF]">AI</span>
                </span>
                <span className="text-[10px] text-[#5C6478] tracking-wider uppercase font-mono leading-none">
                  Intelligence Platform
                </span>
              </div>
            </div>
          ) : (
            <div className="w-full flex justify-center">
              <div className="w-8 h-8 rounded-lg bg-linear-to-br from-[#6C8CFF] to-[#3B5BDB] flex items-center justify-center text-white shadow-md shadow-[#6C8CFF]/20">
                <Layers className="w-4 h-4" />
              </div>
            </div>
          )}

          {/* Desktop Collapse Toggle */}
          <button
            onClick={onToggleCollapse}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className={cn(
              'hidden lg:flex items-center justify-center w-6 h-6 rounded text-[#5C6478] hover:text-[#EDEFF3] hover:bg-[#1D212A] transition-colors',
              collapsed && 'mx-auto'
            )}
          >
            {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Navigation Groups */}
        <div className="flex-1 overflow-y-auto py-2 divide-y divide-[#262B35]/50">
          {renderNavGroup(null, mainNav)}
          {renderNavGroup('Operations', operationsNav)}
          {renderNavGroup('Intelligence', intelligenceNav)}
          {renderNavGroup('Platform', systemNav)}
        </div>

        {/* System Health / Status Indicator Footer */}
        <div className="p-3 border-t border-[#262B35]">
          {!collapsed ? (
            <div className="flex items-center justify-between px-2 py-1.5 rounded-lg bg-[#171A20] border border-[#262B35]">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-[#4FAE7C] animate-pulse" />
                <span className="text-[11px] font-mono text-[#8A93A6]">Pipeline v1.0</span>
              </div>
              <span className="text-[10px] font-mono text-[#4FAE7C] bg-[#4FAE7C]/10 px-1.5 py-0.5 rounded border border-[#4FAE7C]/20">
                Live
              </span>
            </div>
          ) : (
            <div className="flex justify-center" title="Pipeline Status: Live">
              <span className="w-2.5 h-2.5 rounded-full bg-[#4FAE7C] animate-pulse" />
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
