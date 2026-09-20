import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  Bell,
  CheckCircle,
  AlertTriangle,
  AlertOctagon,
  Info,
  ExternalLink,
  Check,
  Building2,
  Cpu,
} from 'lucide-react';
import { UnifiedAlert } from '@/services/api/alertsApi';
import { cn } from '@/utils/cn';

interface NotificationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: UnifiedAlert[];
  onAcknowledge: (id: string) => void;
  onAcknowledgeAll: () => void;
}

type FilterTab = 'all' | 'critical' | 'warning' | 'info';

export const NotificationDrawer: React.FC<NotificationDrawerProps> = ({
  isOpen,
  onClose,
  alerts,
  onAcknowledge,
  onAcknowledgeAll,
}) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<FilterTab>('all');

  // Filter unacknowledged / active alerts first
  const activeAlerts = useMemo(() => {
    return alerts.filter((a) => a.status !== 'resolved');
  }, [alerts]);

  const criticalCount = useMemo(
    () => activeAlerts.filter((a) => a.severity === 'critical').length,
    [activeAlerts]
  );
  const warningCount = useMemo(
    () => activeAlerts.filter((a) => a.severity === 'high').length,
    [activeAlerts]
  );
  const infoCount = useMemo(
    () => activeAlerts.filter((a) => a.severity === 'medium' || a.severity === 'low').length,
    [activeAlerts]
  );

  const filteredAlerts = useMemo(() => {
    if (activeTab === 'critical') {
      return activeAlerts.filter((a) => a.severity === 'critical');
    }
    if (activeTab === 'warning') {
      return activeAlerts.filter((a) => a.severity === 'high');
    }
    if (activeTab === 'info') {
      return activeAlerts.filter((a) => a.severity === 'medium' || a.severity === 'low');
    }
    return activeAlerts;
  }, [activeAlerts, activeTab]);

  const handleInspect = (alert: UnifiedAlert) => {
    onClose();
    if (alert.outletId && alert.outletId !== 'NETWORK') {
      if (alert.domain === 'Inventory') {
        navigate('/inventory');
      } else if (alert.domain === 'Workforce') {
        navigate('/workforce');
      } else if (alert.domain === 'Audit') {
        navigate('/audit');
      } else {
        navigate(`/outlets/${alert.outletId}`);
      }
    } else {
      if (alert.domain === 'Inventory') {
        navigate('/inventory');
      } else if (alert.domain === 'Workforce') {
        navigate('/workforce');
      } else if (alert.domain === 'Audit') {
        navigate('/audit');
      } else {
        navigate('/alerts');
      }
    }
  };

  const formatTime = (ts: string) => {
    try {
      const date = new Date(ts);
      if (isNaN(date.getTime())) return 'Recently';
      const now = new Date();
      const diffMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);
      if (diffMinutes < 1) return 'Just now';
      if (diffMinutes < 60) return `${diffMinutes}m ago`;
      const diffHours = Math.floor(diffMinutes / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      return `${Math.floor(diffHours / 24)}d ago`;
    } catch {
      return 'Recently';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden select-none">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Drawer Panel */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-[#12141A] border-l border-[#262B35] shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-[#262B35] bg-[#171A20] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <Bell className="w-5 h-5 text-[#6C8CFF]" />
                {criticalCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-[#D0555A] animate-ping" />
                )}
              </div>
              <div>
                <h2 className="text-sm font-bold text-[#EDEFF3] font-display">
                  Notifications & Alerts
                </h2>
                <p className="text-[11px] text-[#5C6478] font-mono">
                  {activeAlerts.length} active telemetry events
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {activeAlerts.length > 0 && (
                <button
                  onClick={onAcknowledgeAll}
                  className="px-2.5 py-1 text-[11px] font-medium text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#1D212A] rounded border border-[#262B35] transition-colors"
                  title="Mark all alerts as acknowledged"
                >
                  Clear all
                </button>
              )}
              <button
                onClick={onClose}
                className="p-1.5 text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#1D212A] rounded transition-colors"
                aria-label="Close notification panel"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center gap-1 p-2 bg-[#12141A] border-b border-[#262B35]">
            <button
              onClick={() => setActiveTab('all')}
              className={cn(
                'flex-1 py-1.5 text-[11px] font-medium rounded-lg transition-colors text-center',
                activeTab === 'all'
                  ? 'bg-[#1D212A] text-[#EDEFF3] border border-[#262B35]'
                  : 'text-[#8A93A6] hover:text-[#EDEFF3]'
              )}
            >
              All ({activeAlerts.length})
            </button>
            <button
              onClick={() => setActiveTab('critical')}
              className={cn(
                'flex-1 py-1.5 text-[11px] font-medium rounded-lg transition-colors text-center flex items-center justify-center gap-1',
                activeTab === 'critical'
                  ? 'bg-[#D0555A]/10 text-[#D0555A] border border-[#D0555A]/30'
                  : 'text-[#8A93A6] hover:text-[#EDEFF3]'
              )}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#D0555A]" />
              Critical ({criticalCount})
            </button>
            <button
              onClick={() => setActiveTab('warning')}
              className={cn(
                'flex-1 py-1.5 text-[11px] font-medium rounded-lg transition-colors text-center flex items-center justify-center gap-1',
                activeTab === 'warning'
                  ? 'bg-[#F2A73B]/10 text-[#F2A73B] border border-[#F2A73B]/30'
                  : 'text-[#8A93A6] hover:text-[#EDEFF3]'
              )}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#F2A73B]" />
              Warning ({warningCount})
            </button>
            <button
              onClick={() => setActiveTab('info')}
              className={cn(
                'flex-1 py-1.5 text-[11px] font-medium rounded-lg transition-colors text-center flex items-center justify-center gap-1',
                activeTab === 'info'
                  ? 'bg-[#3AA99F]/10 text-[#3AA99F] border border-[#3AA99F]/30'
                  : 'text-[#8A93A6] hover:text-[#EDEFF3]'
              )}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#3AA99F]" />
              Info ({infoCount})
            </button>
          </div>

          {/* Alert List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {filteredAlerts.length === 0 ? (
              <div className="py-16 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-[#3AA99F]/10 border border-[#3AA99F]/20 flex items-center justify-center text-[#3AA99F] mx-auto">
                  <CheckCircle className="w-6 h-6" />
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-semibold text-[#EDEFF3]">All systems normal</p>
                  <p className="text-[11px] text-[#5C6478] max-w-xs mx-auto">
                    No active {activeTab !== 'all' ? activeTab : ''} alerts across the franchise network.
                  </p>
                </div>
              </div>
            ) : (
              filteredAlerts.map((alert) => {
                const isCritical = alert.severity === 'critical';
                const isWarning = alert.severity === 'high';
                const isAcknowledged = alert.status === 'acknowledged';

                return (
                  <div
                    key={alert.id}
                    className={cn(
                      'p-3 rounded-xl border transition-all space-y-2.5',
                      isCritical
                        ? 'bg-[#D0555A]/5 border-[#D0555A]/30 hover:border-[#D0555A]/50'
                        : isWarning
                        ? 'bg-[#F2A73B]/5 border-[#F2A73B]/30 hover:border-[#F2A73B]/50'
                        : 'bg-[#171A20] border-[#262B35] hover:border-[#3A4155]',
                      isAcknowledged && 'opacity-60'
                    )}
                  >
                    {/* Item Header */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {isCritical ? (
                          <AlertOctagon className="w-4 h-4 text-[#D0555A] shrink-0" />
                        ) : isWarning ? (
                          <AlertTriangle className="w-4 h-4 text-[#F2A73B] shrink-0" />
                        ) : (
                          <Info className="w-4 h-4 text-[#3AA99F] shrink-0" />
                        )}
                        <span
                          className={cn(
                            'text-[10px] font-mono uppercase px-1.5 py-0.5 rounded font-semibold',
                            isCritical
                              ? 'bg-[#D0555A]/20 text-[#D0555A]'
                              : isWarning
                              ? 'bg-[#F2A73B]/20 text-[#F2A73B]'
                              : 'bg-[#3AA99F]/20 text-[#3AA99F]'
                          )}
                        >
                          {alert.severity}
                        </span>
                        <span className="text-[10px] font-mono text-[#8A93A6] bg-[#12141A] px-1.5 py-0.5 rounded border border-[#262B35]">
                          {alert.domain}
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5 text-[10px] font-mono text-[#5C6478]">
                        <Building2 className="w-3 h-3 text-[#6C8CFF]" />
                        <span>{alert.outletId}</span>
                      </div>
                    </div>

                    {/* Title and description */}
                    <div>
                      <h4 className="text-xs font-semibold text-[#EDEFF3] leading-snug">
                        {alert.title}
                      </h4>
                      <p className="text-[11px] text-[#8A93A6] mt-1 leading-relaxed">
                        {alert.description}
                      </p>
                    </div>

                    {/* Footer info & Actions */}
                    <div className="pt-2 border-t border-[#262B35]/50 flex items-center justify-between text-[10px] font-mono">
                      <span className="text-[#5C6478]">{formatTime(alert.timestamp)}</span>

                      <div className="flex items-center gap-2">
                        {!isAcknowledged ? (
                          <button
                            onClick={() => onAcknowledge(alert.id)}
                            className="flex items-center gap-1 text-[#8A93A6] hover:text-[#3AA99F] transition-colors px-1.5 py-0.5 rounded hover:bg-[#1D212A]"
                            title="Acknowledge alert"
                          >
                            <Check className="w-3 h-3" />
                            <span>Ack</span>
                          </button>
                        ) : (
                          <span className="text-[#3AA99F] flex items-center gap-1">
                            <Check className="w-3 h-3" />
                            <span>Acked</span>
                          </span>
                        )}

                        <button
                          onClick={() => handleInspect(alert)}
                          className="flex items-center gap-1 text-[#6C8CFF] hover:text-white transition-colors px-1.5 py-0.5 rounded bg-[#6C8CFF]/10 hover:bg-[#6C8CFF]/20"
                        >
                          <span>Inspect</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Drawer Footer */}
          <div className="p-3 bg-[#171A20] border-t border-[#262B35] flex items-center justify-between">
            <div className="flex items-center gap-2 text-[10px] font-mono text-[#5C6478]">
              <Cpu className="w-3.5 h-3.5 text-[#3AA99F]" />
              <span>Real-time polling: active</span>
            </div>
            <button
              onClick={() => {
                onClose();
                navigate('/alerts');
              }}
              className="text-xs font-medium text-[#6C8CFF] hover:text-white transition-colors flex items-center gap-1 px-2.5 py-1 rounded bg-[#6C8CFF]/10 hover:bg-[#6C8CFF]/20"
            >
              <span>View All Alerts</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
