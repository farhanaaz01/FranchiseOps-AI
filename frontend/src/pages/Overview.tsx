import React, { useMemo } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { KPICard } from '@/components/kpi/KPICard';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Button } from '@/components/ui/Button';
import { RevenueTrendChart } from '@/components/charts/RevenueTrendChart';
import {
  DollarSign,
  Activity,
  AlertTriangle,
  TrendingDown,
  Play,
  ArrowRight,
  ShieldAlert,
  Bot,
  Sparkles,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useDashboardSummary } from '@/hooks/useDashboardSummary';
import { useOutlets } from '@/hooks/useOutlets';
import { useIntelligence } from '@/hooks/useIntelligence';
import { useAlerts } from '@/hooks/useAlerts';
import { formatCurrency, formatPercent } from '@/utils/formatters';

export const Overview: React.FC = () => {
  const navigate = useNavigate();
  const { data: summary, refresh: refreshSummary } = useDashboardSummary();
  const { outlets } = useOutlets();
  const { pipelineData, isRunning, triggerPipeline, rootCauses } = useIntelligence();
  const { alerts } = useAlerts();

  const handleRunPipeline = async () => {
    await triggerPipeline();
    refreshSummary();
  };

  const revenueNum = parseFloat(summary.total_revenue) || 148520;
  const criticalCount = alerts.filter((a) => a.severity === 'critical' && a.status !== 'resolved').length;

  // Aggregate 7-day revenue forecast across all outlets from XGBoost pipeline output
  const networkTrendData = useMemo(() => {
    if (!pipelineData.forecasts || pipelineData.forecasts.length === 0) return undefined;

    const dayMap = new Map<string, number>();
    pipelineData.forecasts.forEach((fc) => {
      fc.forecasts?.forEach((pt) => {
        const current = dayMap.get(pt.forecast_date) || 0;
        dayMap.set(pt.forecast_date, current + pt.predicted_revenue);
      });
    });

    const dates = Array.from(dayMap.keys()).sort();
    if (dates.length === 0) return undefined;

    const totalCohortDailyRevenue = pipelineData.kpis?.reduce((acc, k) => acc + k.avg_daily_revenue, 0) || 28760;

    return dates.map((date) => {
      const forecastVal = Math.round(dayMap.get(date) || 0);
      return {
        date,
        actual: Math.round(totalCohortDailyRevenue),
        forecast: forecastVal,
      };
    });
  }, [pipelineData.forecasts, pipelineData.kpis]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Network Overview"
        subtitle="Real-time multi-unit franchise intelligence, telemetry, and automated operations."
        badge={
          <Badge variant="accent">
            Pipeline Synced:{' '}
            {pipelineData.generated_at
              ? new Date(pipelineData.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              : 'Live'}
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={<Sparkles className="w-3.5 h-3.5 text-[#6C8CFF]" />}
              onClick={() => navigate('/ai-insights')}
            >
              Ask AI Agent
            </Button>
            <Button
              variant="primary"
              size="sm"
              loading={isRunning}
              icon={<Play className="w-3.5 h-3.5" />}
              onClick={handleRunPipeline}
            >
              {isRunning ? 'Running Pipeline...' : 'Run Pipeline'}
            </Button>
          </div>
        }
      />

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Network Revenue"
          value={formatCurrency(revenueNum)}
          change={8.4}
          changeType="positive"
          changeLabel="vs last week"
          status="healthy"
          icon={<DollarSign className="w-4 h-4 text-[#6C8CFF]" />}
        />
        <KPICard
          title="Avg Health Score"
          value={summary.average_health_score || '76.8'}
          change={2.1}
          changeType="positive"
          changeLabel="pts vs 30d avg"
          status="healthy"
          icon={<Activity className="w-4 h-4 text-[#4FAE7C]" />}
        />
        <KPICard
          title="Avg Wastage Rate"
          value="2.4%"
          change={-0.6}
          changeType="positive"
          changeLabel="improvement"
          status="healthy"
          icon={<TrendingDown className="w-4 h-4 text-[#4FAE7C]" />}
        />
        <KPICard
          title="Outlets Requiring Action"
          value={String(summary.underperforming_outlets || 2)}
          subtext={`${criticalCount} Critical • 1 At Risk`}
          status={summary.underperforming_outlets > 0 ? 'critical' : 'healthy'}
          icon={<AlertTriangle className="w-4 h-4 text-[#D0555A]" />}
          onClick={() => navigate('/alerts')}
        />
      </div>

      {/* Main Content Split: Chart + Outlets Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Revenue Forecast & Trend */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader separator>
              <div>
                <CardTitle>Network Revenue & Predictive Forecast</CardTitle>
                <CardDescription>
                  Actual daily revenue vs 7-day XGBoost lag/rolling predictive model
                </CardDescription>
              </div>
              <Badge variant="outline" className="font-mono text-[10px]">
                XGBoost ML v1
              </Badge>
            </CardHeader>
            <CardContent className="pt-4">
              <RevenueTrendChart data={networkTrendData} height={280} />
            </CardContent>
          </Card>

          {/* Network Outlet Matrix */}
          <Card>
            <CardHeader separator>
              <div>
                <CardTitle>Outlet Performance Status</CardTitle>
                <CardDescription>
                  Current operational health scores across all active franchise locations
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                icon={<ArrowRight className="w-3.5 h-3.5" />}
                onClick={() => navigate('/outlets')}
              >
                View All
              </Button>
            </CardHeader>
            <div className="divide-y divide-[#262B35]">
              {outlets.map((outlet) => (
                <div
                  key={outlet.id}
                  onClick={() => navigate(`/outlets/${outlet.outlet_id || outlet.id}`)}
                  className="flex items-center justify-between p-4 hover:bg-[#1D212A]/60 cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-[#1D212A] border border-[#262B35] flex items-center justify-center font-mono text-xs font-semibold text-[#6C8CFF]">
                      {outlet.id.slice(-2)}
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-[#EDEFF3]">
                        {outlet.name}
                      </div>
                      <div className="text-[11px] text-[#5C6478] font-mono">
                        {outlet.id} • Rev: {outlet.revenue} • Mgr: {outlet.manager}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right hidden sm:block">
                      <div className="text-xs font-mono font-bold text-[#EDEFF3]">
                        {outlet.healthScore} <span className="text-[10px] text-[#5C6478]">/ 100</span>
                      </div>
                      <div className="text-[10px] text-[#5C6478]">Composite Score</div>
                    </div>
                    <StatusBadge status={outlet.status} size="sm" />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right 1 Col: AI Root Cause Insights + Agent Actions */}
        <div className="space-y-6">
          {/* Active AI Insights */}
          <Card>
            <CardHeader separator>
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#6C8CFF]" />
                <CardTitle>Root Cause Findings</CardTitle>
              </div>
              <Badge variant="danger" size="sm">
                Action Req.
              </Badge>
            </CardHeader>
            <CardContent className="space-y-3">
              {rootCauses.slice(0, 2).map((rc) => (
                <div
                  key={rc.outlet_id}
                  className="p-3 rounded-lg bg-[#1D212A] border border-[#262B35] space-y-2 hover:border-[#6C8CFF]/40 transition-colors cursor-pointer"
                  onClick={() => navigate('/ai-insights')}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-[#EDEFF3] font-mono">
                      {rc.outlet_id}
                    </span>
                    <Badge variant={rc.health_status === 'Critical' ? 'danger' : 'warning'} size="sm">
                      {rc.health_status}
                    </Badge>
                  </div>
                  <p className="text-xs text-[#8A93A6]">
                    {rc.priority_issue || rc.overall_recommendation}
                  </p>
                  <div className="text-[11px] font-mono text-[#6C8CFF] flex items-center gap-1">
                    <ArrowRight className="w-3 h-3" />
                    <span>View AI diagnostic & XGBoost drivers</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Autonomous Agent Actions */}
          <Card>
            <CardHeader separator>
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-[#4FAE7C]" />
                <CardTitle>Autonomous Agent Feed</CardTitle>
              </div>
              <Badge variant="neutral" size="sm">Live</Badge>
            </CardHeader>
            <div className="divide-y divide-[#262B35] text-xs">
              <div className="p-3.5 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-[#EDEFF3]">PO #4192 Created</span>
                  <span className="text-[10px] text-[#5C6478] font-mono">12m ago</span>
                </div>
                <p className="text-[#8A93A6] text-[11px]">
                  Inventory Agent generated purchase order for OUT-03 milk supplier.
                </p>
              </div>
              <div className="p-3.5 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-[#EDEFF3]">Shift Rebalanced</span>
                  <span className="text-[10px] text-[#5C6478] font-mono">45m ago</span>
                </div>
                <p className="text-[#8A93A6] text-[11px]">
                  Workforce Agent reassigned 2 floater staff to OUT-05.
                </p>
              </div>
              <div className="p-3.5 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-[#EDEFF3]">Audit Check Passed</span>
                  <span className="text-[10px] text-[#5C6478] font-mono">2h ago</span>
                </div>
                <p className="text-[#8A93A6] text-[11px]">
                  HACCP temperature log verified for Downtown Flagship.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
