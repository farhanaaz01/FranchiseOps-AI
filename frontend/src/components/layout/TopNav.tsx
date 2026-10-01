import React, { useState, useEffect, useMemo } from 'react';
import { cn } from '@/utils/cn';
import {
  Menu,
  Search,
  Bell,
  RefreshCw,
  ChevronDown,
  Building2,
  Activity,
} from 'lucide-react';
import { SearchModal } from './SearchModal';
import { NotificationDrawer } from './NotificationDrawer';
import { SystemHealthModal } from './SystemHealthModal';
import { useSystemHealth } from '@/hooks/useSystemHealth';
import { useAlerts } from '@/hooks/useAlerts';
import { useOutlets } from '@/hooks/useOutlets';

interface TopNavProps {
  onOpenMobileMenu: () => void;
  selectedOutlet?: string;
  onSelectOutlet?: (outletId: string) => void;
}

const DEFAULT_OUTLETS = [
  { id: 'all', name: 'All Outlets (Network)' },
  { id: 'OUT-01', name: 'OUT-01 • Downtown Flagship' },
  { id: 'OUT-02', name: 'OUT-02 • Westside Hub' },
  { id: 'OUT-03', name: 'OUT-03 • Metro Mall' },
  { id: 'OUT-04', name: 'OUT-04 • Uptown Express' },
  { id: 'OUT-05', name: 'OUT-05 • Airport Terminal' },
];

export const TopNav: React.FC<TopNavProps> = ({
  onOpenMobileMenu,
  selectedOutlet = 'all',
  onSelectOutlet,
}) => {
  const [outletDropdownOpen, setOutletDropdownOpen] = useState(false);
  const [currentOutlet, setCurrentOutlet] = useState(selectedOutlet);
  const [searchOpen, setSearchOpen] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [healthModalOpen, setHealthModalOpen] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const { overallStatus, latencyMs, refetch: refetchHealth } = useSystemHealth();
  const { alerts, acknowledgeAlert, refresh: refetchAlerts } = useAlerts();
  const { outlets } = useOutlets();

  const outletOptions = useMemo(() => {
    if (!outlets || outlets.length === 0) return DEFAULT_OUTLETS;
    return [
      { id: 'all', name: 'All Outlets (Network)' },
      ...outlets.map((o) => ({ id: o.id, name: `${o.id} • ${o.name}` })),
    ];
  }, [outlets]);

  // Global Ctrl+K / Cmd+K listener
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  const handleSelectOutlet = (id: string) => {
    setCurrentOutlet(id);
    onSelectOutlet?.(id);
    setOutletDropdownOpen(false);
  };

  const handleManualSync = async () => {
    setIsSyncing(true);
    await Promise.allSettled([refetchHealth(), refetchAlerts()]);
    setTimeout(() => setIsSyncing(false), 600);
  };

  const handleAcknowledgeAll = () => {
    alerts.forEach((a) => {
      if (a.status !== 'resolved' && a.status !== 'acknowledged') {
        acknowledgeAlert(a.id);
      }
    });
  };

  const activeAlerts = alerts.filter((a) => a.status !== 'resolved');
  const criticalCount = activeAlerts.filter((a) => a.severity === 'critical').length;
  const unreadCount = activeAlerts.length;

  const selectedOutletName = outletOptions.find((o) => o.id === currentOutlet)?.name ?? 'All Outlets';

  return (
    <>
      {/* Global Command Search Modal */}
      <SearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />

      {/* Slide-over Notification Drawer */}
      <NotificationDrawer
        isOpen={notificationOpen}
        onClose={() => setNotificationOpen(false)}
        alerts={alerts}
        onAcknowledge={acknowledgeAlert}
        onAcknowledgeAll={handleAcknowledgeAll}
      />

      {/* System Health / Telemetry Modal */}
      <SystemHealthModal
        isOpen={healthModalOpen}
        onClose={() => setHealthModalOpen(false)}
      />

      <header className="sticky top-0 z-30 flex items-center justify-between h-14 px-4 bg-[#12141A]/90 backdrop-blur-md border-b border-[#262B35] select-none">
        {/* Left side: Mobile Hamburger + Outlet Switcher */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenMobileMenu}
            className="lg:hidden p-2 rounded-lg text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#1D212A] transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Outlet Switcher Dropdown */}
          <div className="relative">
            <button
              onClick={() => setOutletDropdownOpen(!outletDropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#171A20] border border-[#262B35] text-xs font-medium text-[#EDEFF3] hover:border-[#3A4155] transition-colors"
            >
              <Building2 className="w-3.5 h-3.5 text-[#6C8CFF]" />
              <span className="font-mono text-[11px] max-w-[160px] truncate">
                {selectedOutletName}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-[#5C6478]" />
            </button>

            {outletDropdownOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setOutletDropdownOpen(false)}
                />
                <div className="absolute left-0 mt-1.5 w-64 z-20 py-1 rounded-xl bg-[#171A20] border border-[#262B35] shadow-xl divide-y divide-[#262B35]/50 animate-in fade-in">
                  <div className="px-3 py-1.5 text-[10px] font-mono text-[#5C6478] uppercase">
                    Select Scope
                  </div>
                  <div className="py-1">
                    {outletOptions.map((outlet) => (
                      <button
                        key={outlet.id}
                        onClick={() => handleSelectOutlet(outlet.id)}
                        className={cn(
                          'w-full text-left px-3 py-1.5 text-xs transition-colors flex items-center justify-between',
                          currentOutlet === outlet.id
                            ? 'bg-[#6C8CFF]/10 text-[#6C8CFF] font-semibold'
                            : 'text-[#8A93A6] hover:bg-[#1D212A] hover:text-[#EDEFF3]'
                        )}
                      >
                        <span className="font-mono">{outlet.name}</span>
                        {currentOutlet === outlet.id && (
                          <span className="w-1.5 h-1.5 rounded-full bg-[#6C8CFF]" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Middle: Search Bar */}
        <div className="hidden md:flex items-center flex-1 max-w-md mx-6">
          <button
            onClick={() => setSearchOpen(true)}
            className="relative w-full text-left cursor-pointer group"
          >
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#5C6478] group-hover:text-[#6C8CFF] transition-colors" />
            <div className="w-full pl-9 pr-4 py-1.5 bg-[#171A20] group-hover:bg-[#1D212A] border border-[#262B35] group-hover:border-[#3A4155] rounded-lg text-xs text-[#5C6478] transition-colors flex items-center justify-between">
              <span>Search outlets, alerts, metrics, reports...</span>
              <kbd className="px-1.5 py-0.5 text-[10px] font-mono text-[#5C6478] bg-[#12141A] rounded border border-[#262B35]">
                ⌘K
              </kbd>
            </div>
          </button>
        </div>

        {/* Right side: Actions, System Health, Notifications & Profile */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Live System Health Pill */}
          <button
            onClick={() => setHealthModalOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#171A20] border border-[#262B35] hover:border-[#3A4155] transition-colors cursor-pointer"
            title="Inspect System Telemetry & Gateway Connectivity"
          >
            <span
              className={cn(
                'w-2 h-2 rounded-full',
                overallStatus === 'online' && 'bg-[#3AA99F] animate-pulse',
                overallStatus === 'degraded' && 'bg-[#F2A73B]',
                overallStatus === 'offline' && 'bg-[#D0555A]'
              )}
            />
            <span className="hidden sm:inline text-[11px] font-mono text-[#8A93A6]">
              {overallStatus === 'online'
                ? latencyMs ? `${latencyMs}ms` : 'Online'
                : overallStatus === 'degraded'
                ? 'Degraded'
                : 'Offline'}
            </span>
            <Activity className="w-3 h-3 text-[#5C6478]" />
          </button>

          {/* Pipeline Refresh Indicator */}
          <button
            onClick={handleManualSync}
            disabled={isSyncing}
            className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#1D212A] border border-transparent hover:border-[#262B35] transition-colors disabled:opacity-50"
            title="Refresh active telemetry from FastAPI gateway"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', isSyncing && 'animate-spin text-[#6C8CFF]')} />
            <span className="font-mono text-[11px]">Sync</span>
          </button>

          {/* Notifications Button with Dynamic Badge */}
          <button
            onClick={() => setNotificationOpen(true)}
            className="relative p-2 rounded-lg text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#1D212A] transition-colors"
            aria-label={`View notifications (${unreadCount} active)`}
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span
                className={cn(
                  'absolute -top-0.5 -right-0.5 min-w-4 h-4 px-1 rounded-full text-[10px] font-mono font-bold flex items-center justify-center text-white ring-2 ring-[#12141A]',
                  criticalCount > 0 ? 'bg-[#D0555A]' : 'bg-[#F2A73B]'
                )}
              >
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* Vertical divider */}
          <div className="h-5 w-px bg-[#262B35]" />

          {/* User / Org badge */}
          <div className="flex items-center gap-2 pl-1">
            <div className="w-7 h-7 rounded-full bg-linear-to-tr from-[#6C8CFF] to-[#A78BFA] flex items-center justify-center text-xs font-semibold text-white shadow-xs">
              HQ
            </div>
            <div className="hidden xl:flex flex-col text-left">
              <span className="text-xs font-semibold text-[#EDEFF3] leading-none">
                Operations Lead
              </span>
              <span className="text-[10px] text-[#5C6478] font-mono leading-none mt-1">
                Corporate HQ
              </span>
            </div>
          </div>
        </div>
      </header>
    </>
  );
};
