import React, { useState, useEffect } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  User,
  Bell,
  Sliders,
  Palette,
  Server,
  Save,
  CheckCircle2,
  RefreshCw,
  Shield,
  Info,
  Building2,
  Globe,
  Clock,
  Cpu,
  Lock,
} from 'lucide-react';
import { useSystemHealth } from '@/hooks/useSystemHealth';
import { cn } from '@/utils/cn';

type SettingsTab = 'profile' | 'notifications' | 'preferences' | 'appearance' | 'api';

export const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [saveFeedback, setSaveFeedback] = useState<string | null>(null);

  const {
    overallStatus,
    apiGatewayStatus,
    latencyMs,
    lastSyncTime,
    modelVersion,
    outletCount,
    apiBaseUrl,
    checking,
    refetch: pingGateway,
  } = useSystemHealth();

  // Notification Preferences State (Client-Side LocalStorage)
  const [notifyCritical, setNotifyCritical] = useState(() => {
    return localStorage.getItem('fo_notify_critical') !== 'false';
  });
  const [notifyWarning, setNotifyWarning] = useState(() => {
    return localStorage.getItem('fo_notify_warning') !== 'false';
  });
  const [notifyAgentActions, setNotifyAgentActions] = useState(() => {
    return localStorage.getItem('fo_notify_agents') !== 'false';
  });
  const [audioPings, setAudioPings] = useState(() => {
    return localStorage.getItem('fo_audio_pings') === 'true';
  });

  // User Preferences State
  const [defaultScope, setDefaultScope] = useState(() => {
    return localStorage.getItem('fo_default_scope') || 'all';
  });
  const [refreshInterval, setRefreshInterval] = useState(() => {
    return localStorage.getItem('fo_refresh_interval') || '30';
  });
  const [currencyFormat, setCurrencyFormat] = useState(() => {
    return localStorage.getItem('fo_currency') || 'USD';
  });

  // Appearance State
  const [density, setDensity] = useState(() => {
    return localStorage.getItem('fo_density') || 'comfortable';
  });

  const triggerSaveNotification = (msg: string) => {
    setSaveFeedback(msg);
    setTimeout(() => setSaveFeedback(null), 3500);
  };

  const handleSaveNotifications = () => {
    localStorage.setItem('fo_notify_critical', String(notifyCritical));
    localStorage.setItem('fo_notify_warning', String(notifyWarning));
    localStorage.setItem('fo_notify_agents', String(notifyAgentActions));
    localStorage.setItem('fo_audio_pings', String(audioPings));
    triggerSaveNotification('Notification preferences saved locally in browser.');
  };

  const handleSavePreferences = () => {
    localStorage.setItem('fo_default_scope', defaultScope);
    localStorage.setItem('fo_refresh_interval', refreshInterval);
    localStorage.setItem('fo_currency', currencyFormat);
    triggerSaveNotification('Operational preferences saved locally in browser.');
  };

  const handleSaveAppearance = () => {
    localStorage.setItem('fo_density', density);
    triggerSaveNotification('Appearance preferences saved locally in browser.');
  };

  return (
    <div className="space-y-6 select-none">
      <PageHeader
        title="Enterprise Settings & Subsystem Configurations"
        subtitle="Manage client-side preferences, operational telemetry polling, notification thresholds, and gateway connection status."
        badge={
          <Badge variant="neutral" className="font-mono">
            Enterprise Console
          </Badge>
        }
      />

      {/* Save Feedback Banner */}
      {saveFeedback && (
        <div className="p-3.5 bg-[#4FAE7C]/10 border border-[#4FAE7C]/30 rounded-xl text-xs text-[#4FAE7C] flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{saveFeedback}</span>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex items-center gap-1 border-b border-[#262B35] pb-px overflow-x-auto">
        {[
          { id: 'profile', label: 'User Profile', icon: User },
          { id: 'notifications', label: 'Notifications', icon: Bell },
          { id: 'preferences', label: 'Preferences', icon: Sliders },
          { id: 'appearance', label: 'Appearance', icon: Palette },
          { id: 'api', label: 'API Connection', icon: Server },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as SettingsTab)}
              className={cn(
                'flex items-center gap-2 px-4 py-2.5 text-xs font-medium rounded-t-lg transition-colors whitespace-nowrap border-b-2',
                isActive
                  ? 'border-[#6C8CFF] text-[#EDEFF3] bg-[#171A20]'
                  : 'border-transparent text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#12141A]'
              )}
            >
              <Icon className={cn('w-3.5 h-3.5', isActive ? 'text-[#6C8CFF]' : 'text-[#5C6478]')} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: Profile */}
      {activeTab === 'profile' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-150">
          <Card className="lg:col-span-2">
            <CardHeader separator>
              <div>
                <CardTitle>Directory Profile</CardTitle>
                <CardDescription>
                  Enterprise identity and assigned operational jurisdiction. Managed via SSO directory.
                </CardDescription>
              </div>
              <Badge variant="success">SSO Verified</Badge>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-mono uppercase text-[#5C6478]">Full Name</label>
                  <div className="p-2.5 bg-[#171A20] rounded-lg border border-[#262B35] text-[#EDEFF3] font-medium">
                    Corporate Operations Lead
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-mono uppercase text-[#5C6478]">Corporate Email</label>
                  <div className="p-2.5 bg-[#171A20] rounded-lg border border-[#262B35] text-[#EDEFF3] font-mono">
                    ops.lead@franchiseops.internal
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-mono uppercase text-[#5C6478]">Access Role</label>
                  <div className="p-2.5 bg-[#171A20] rounded-lg border border-[#262B35] text-[#6C8CFF] font-medium">
                    Corporate Operations Director
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-mono uppercase text-[#5C6478]">Assigned Scope</label>
                  <div className="p-2.5 bg-[#171A20] rounded-lg border border-[#262B35] text-[#EDEFF3]">
                    Network Administrator (5 Stores)
                  </div>
                </div>
              </div>

              <div className="p-3 bg-[#12141A] rounded-lg border border-[#262B35] flex items-start gap-2 text-xs text-[#5C6478] mt-4">
                <Info className="w-4 h-4 shrink-0 mt-0.5 text-[#6C8CFF]" />
                <span>
                  Profile modifications must be requested through your corporate identity provider (Okta/Azure AD).
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader separator>
              <CardTitle>Session Security</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex items-center justify-between py-1.5 border-b border-[#262B35]/50">
                <span className="text-[#8A93A6]">Auth Method</span>
                <span className="font-mono text-[#EDEFF3]">Enterprise Bearer</span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-[#262B35]/50">
                <span className="text-[#8A93A6]">Token Status</span>
                <span className="text-[#4FAE7C] font-mono flex items-center gap-1">
                  <Lock className="w-3 h-3" /> Active
                </span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-[#262B35]/50">
                <span className="text-[#8A93A6]">Session ID</span>
                <span className="font-mono text-[#5C6478]">tok_••••••••e89f</span>
              </div>
              <div className="flex items-center justify-between py-1.5">
                <span className="text-[#8A93A6]">CORS Policy</span>
                <span className="font-mono text-[#4FAE7C]">Strict Origin</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab 2: Notifications */}
      {activeTab === 'notifications' && (
        <Card className="animate-in fade-in duration-150">
          <CardHeader separator>
            <div>
              <CardTitle>Notification Rules & Alerts</CardTitle>
              <CardDescription>
                Configure real-time event triggers and operational breach notifications.
              </CardDescription>
            </div>
            <Button
              variant="primary"
              size="sm"
              icon={<Save className="w-3.5 h-3.5" />}
              onClick={handleSaveNotifications}
            >
              Save Preferences
            </Button>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                <div className="space-y-0.5">
                  <p className="font-semibold text-[#EDEFF3]">Critical Severity Alerts</p>
                  <p className="text-[11px] text-[#8A93A6]">
                    Immediate slide-over notifications for urgent inventory stockouts and high compliance risks.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={notifyCritical}
                  onChange={(e) => setNotifyCritical(e.target.checked)}
                  className="w-4 h-4 rounded accent-[#6C8CFF]"
                />
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                <div className="space-y-0.5">
                  <p className="font-semibold text-[#EDEFF3]">High & Warning Alerts</p>
                  <p className="text-[11px] text-[#8A93A6]">
                    Threshold breaches for labor overtime, understaffing, and CAC spikes.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={notifyWarning}
                  onChange={(e) => setNotifyWarning(e.target.checked)}
                  className="w-4 h-4 rounded accent-[#6C8CFF]"
                />
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                <div className="space-y-0.5">
                  <p className="font-semibold text-[#EDEFF3]">Autonomous Agent Workflow Updates</p>
                  <p className="text-[11px] text-[#8A93A6]">
                    Notify when Inventory, Workforce, or Marketing agents dispatch corrective protocols.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={notifyAgentActions}
                  onChange={(e) => setNotifyAgentActions(e.target.checked)}
                  className="w-4 h-4 rounded accent-[#6C8CFF]"
                />
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                <div className="space-y-0.5">
                  <p className="font-semibold text-[#EDEFF3]">Audio Ping for Critical Events</p>
                  <p className="text-[11px] text-[#8A93A6]">
                    Subtle audio chime when new critical severity anomalies are detected.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={audioPings}
                  onChange={(e) => setAudioPings(e.target.checked)}
                  className="w-4 h-4 rounded accent-[#6C8CFF]"
                />
              </div>
            </div>

            <div className="p-3 bg-[#12141A] rounded-lg border border-[#262B35] flex items-start gap-2 text-[11px] text-[#5C6478]">
              <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
              <span>
                Notification preferences are stored securely in your browser's local profile and do not require server-side state mutations.
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 3: Preferences */}
      {activeTab === 'preferences' && (
        <Card className="animate-in fade-in duration-150">
          <CardHeader separator>
            <div>
              <CardTitle>Operational Preferences</CardTitle>
              <CardDescription>
                Customize telemetry display formats, default store scopes, and polling cadence.
              </CardDescription>
            </div>
            <Button
              variant="primary"
              size="sm"
              icon={<Save className="w-3.5 h-3.5" />}
              onClick={handleSavePreferences}
            >
              Save Preferences
            </Button>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-medium text-[#EDEFF3]">Default Store Scope</label>
                <select
                  value={defaultScope}
                  onChange={(e) => setDefaultScope(e.target.value)}
                  className="w-full bg-[#171A20] border border-[#262B35] rounded-lg p-2.5 text-xs text-[#EDEFF3] focus:outline-none focus:border-[#6C8CFF]"
                >
                  <option value="all">All Outlets (Network-Wide)</option>
                  <option value="OUT-01">OUT-01 • Downtown Flagship</option>
                  <option value="OUT-02">OUT-02 • Westside Hub</option>
                  <option value="OUT-03">OUT-03 • Metro Mall</option>
                  <option value="OUT-04">OUT-04 • Uptown Express</option>
                  <option value="OUT-05">OUT-05 • Airport Terminal</option>
                </select>
                <p className="text-[10px] text-[#5C6478]">Initial outlet filter applied upon session launch.</p>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-medium text-[#EDEFF3]">Telemetry Polling Interval</label>
                <select
                  value={refreshInterval}
                  onChange={(e) => setRefreshInterval(e.target.value)}
                  className="w-full bg-[#171A20] border border-[#262B35] rounded-lg p-2.5 text-xs text-[#EDEFF3] focus:outline-none focus:border-[#6C8CFF]"
                >
                  <option value="15">Every 15 seconds (High Frequency)</option>
                  <option value="30">Every 30 seconds (Standard)</option>
                  <option value="60">Every 60 seconds (Conservative)</option>
                  <option value="manual">Manual Refresh Only</option>
                </select>
                <p className="text-[10px] text-[#5C6478]">Background refresh frequency for alerts and health checks.</p>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-medium text-[#EDEFF3]">Currency Symbol</label>
                <select
                  value={currencyFormat}
                  onChange={(e) => setCurrencyFormat(e.target.value)}
                  className="w-full bg-[#171A20] border border-[#262B35] rounded-lg p-2.5 text-xs text-[#EDEFF3] focus:outline-none focus:border-[#6C8CFF]"
                >
                  <option value="USD">USD ($) — United States Dollar</option>
                  <option value="EUR">EUR (€) — Euro</option>
                  <option value="GBP">GBP (£) — British Pound</option>
                </select>
                <p className="text-[10px] text-[#5C6478]">Currency representation for revenue and inventory values.</p>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-medium text-[#EDEFF3]">Date Representation</label>
                <div className="p-2.5 bg-[#171A20] rounded-lg border border-[#262B35] text-[#EDEFF3] font-mono">
                  YYYY-MM-DD (ISO 8601 Standard)
                </div>
                <p className="text-[10px] text-[#5C6478]">Fixed standard for audit consistency.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 4: Appearance */}
      {activeTab === 'appearance' && (
        <Card className="animate-in fade-in duration-150">
          <CardHeader separator>
            <div>
              <CardTitle>Interface Appearance</CardTitle>
              <CardDescription>
                High-contrast dark mode tailored for continuous operations room viewing.
              </CardDescription>
            </div>
            <Button
              variant="primary"
              size="sm"
              icon={<Save className="w-3.5 h-3.5" />}
              onClick={handleSaveAppearance}
            >
              Save Appearance
            </Button>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="p-4 rounded-xl bg-[#171A20] border border-[#262B35] space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-[#EDEFF3]">Enterprise Dark Mode</span>
                <Badge variant="success">Active System Default</Badge>
              </div>
              <p className="text-[11px] text-[#8A93A6]">
                FranchiseOps AI utilizes an ergonomic deep obsidian theme (#0E1015) designed for prolonged monitoring and minimal eye strain in command room environments.
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-[11px] font-medium text-[#EDEFF3]">Display Density</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setDensity('comfortable')}
                  className={cn(
                    'p-3 rounded-xl border text-left transition-all',
                    density === 'comfortable'
                      ? 'bg-[#1D212A] border-[#6C8CFF]'
                      : 'bg-[#171A20] border-[#262B35] hover:border-[#3A4155]'
                  )}
                >
                  <p className="font-semibold text-[#EDEFF3]">Comfortable</p>
                  <p className="text-[10px] text-[#5C6478] mt-0.5">Spacious paddings, standard metric tiles</p>
                </button>
                <button
                  type="button"
                  onClick={() => setDensity('compact')}
                  className={cn(
                    'p-3 rounded-xl border text-left transition-all',
                    density === 'compact'
                      ? 'bg-[#1D212A] border-[#6C8CFF]'
                      : 'bg-[#171A20] border-[#262B35] hover:border-[#3A4155]'
                  )}
                >
                  <p className="font-semibold text-[#EDEFF3]">Compact</p>
                  <p className="text-[10px] text-[#5C6478] mt-0.5">Denser tables and tighter card spacing</p>
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 5: API Connection */}
      {activeTab === 'api' && (
        <Card className="animate-in fade-in duration-150">
          <CardHeader separator>
            <div>
              <CardTitle>FastAPI Backend Gateway</CardTitle>
              <CardDescription>
                Verifiable connection details and runtime telemetry diagnostics.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              loading={checking}
              icon={<RefreshCw className={cn('w-3.5 h-3.5', checking && 'animate-spin')} />}
              onClick={pingGateway}
            >
              {checking ? 'Pinging...' : 'Ping Gateway'}
            </Button>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="p-3 bg-[#171A20] rounded-xl border border-[#262B35] space-y-1">
                <span className="text-[10px] font-mono uppercase text-[#5C6478]">Connection Status</span>
                <div className="flex items-center gap-1.5 font-bold text-[#EDEFF3]">
                  <span
                    className={cn(
                      'w-2 h-2 rounded-full',
                      overallStatus === 'online' ? 'bg-[#3AA99F]' : 'bg-[#D0555A]'
                    )}
                  />
                  <span>{apiGatewayStatus}</span>
                </div>
              </div>

              <div className="p-3 bg-[#171A20] rounded-xl border border-[#262B35] space-y-1">
                <span className="text-[10px] font-mono uppercase text-[#5C6478]">Round-Trip Latency</span>
                <div className="font-mono font-bold text-[#EDEFF3]">
                  {latencyMs ? `${latencyMs} ms` : '—'}
                </div>
              </div>

              <div className="p-3 bg-[#171A20] rounded-xl border border-[#262B35] space-y-1">
                <span className="text-[10px] font-mono uppercase text-[#5C6478]">Monitored Stores</span>
                <div className="font-mono font-bold text-[#EDEFF3]">
                  {outletCount} Units Active
                </div>
              </div>

              <div className="p-3 bg-[#171A20] rounded-xl border border-[#262B35] space-y-1">
                <span className="text-[10px] font-mono uppercase text-[#5C6478]">Pipeline Freshness</span>
                <div className="font-mono text-[11px] text-[#EDEFF3] truncate">
                  {lastSyncTime}
                </div>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                <div>
                  <span className="font-semibold text-[#EDEFF3]">Backend Gateway Endpoint</span>
                  <p className="text-[11px] text-[#5C6478] font-mono">Standard HTTP REST API</p>
                </div>
                <span className="font-mono text-[#EDEFF3] bg-[#12141A] px-2.5 py-1 rounded border border-[#262B35]">
                  {apiBaseUrl}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                <div>
                  <span className="font-semibold text-[#EDEFF3]">Machine Learning Architecture</span>
                  <p className="text-[11px] text-[#5C6478] font-mono">Ensemble tree regressor for outlet scoring</p>
                </div>
                <span className="font-mono text-[#9D7BFF] bg-[#12141A] px-2.5 py-1 rounded border border-[#262B35]">
                  {modelVersion}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-[#171A20] border border-[#262B35]">
                <div>
                  <span className="font-semibold text-[#EDEFF3]">Pipeline Output Cache</span>
                  <p className="text-[11px] text-[#5C6478] font-mono">Persisted JSON telemetry buffer</p>
                </div>
                <span className="font-mono text-[#EDEFF3] bg-[#12141A] px-2.5 py-1 rounded border border-[#262B35]">
                  data_engine/pipeline_output.json
                </span>
              </div>
            </div>

            <div className="p-3 bg-[#12141A] rounded-lg border border-[#262B35] flex items-start gap-2 text-[11px] text-[#5C6478]">
              <Shield className="w-3.5 h-3.5 shrink-0 mt-0.5 text-[#4FAE7C]" />
              <span>
                Zero credential exposure: No secret database passwords, bearer keys, or sensitive backend environment variables are rendered in the client.
              </span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
