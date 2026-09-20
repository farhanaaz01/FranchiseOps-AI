import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import {
  Play,
  RefreshCw,
  Cpu,
  BrainCircuit,
  Activity,
  AlertTriangle,
  TrendingUp,
  ShieldAlert,
  Sparkles,
  Bot,
  ArrowRight,
  ChevronRight,
  Calendar,
  Layers,
  CheckCircle2,
} from 'lucide-react';
import { useIntelligence } from '@/hooks/useIntelligence';
import {
  OperationalCopilotChat,
  DriverImportanceChart,
  RootCauseRecommendationCard,
  RecommendationCard,
} from '@/components/ai';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export const AIInsights: React.FC = () => {
  const navigate = useNavigate();
  const {
    pipelineData,
    featureImportances,
    rootCauses,
    forecasts,
    riskPredictions,
    loading,
    isRunning,
    refresh,
    triggerPipeline,
  } = useIntelligence();

  const [forecastOutlet, setForecastOutlet] = useState<string>('ALL');

  // Network Summary calculations
  const networkMetrics = useMemo(() => {
    const scores = pipelineData.performance_scores || [];
    const avgScore =
      scores.length > 0
        ? Math.round(scores.reduce((acc, s) => acc + s.performance_score, 0) / scores.length)
        : 76;

    const criticalCount = scores.filter((s) => s.health_status === 'Critical').length;
    const atRiskCount = scores.filter((s) => s.health_status === 'At Risk').length;
    const healthyCount = scores.filter((s) => s.health_status === 'Healthy').length;

    let totalIssues = 0;
    rootCauses.forEach((rc) => {
      totalIssues += rc.issues?.length || 0;
    });

    return {
      avgScore,
      criticalCount,
      atRiskCount,
      healthyCount,
      totalIssues,
      outletCount: pipelineData.outlet_count || scores.length || 5,
    };
  }, [pipelineData, rootCauses]);

  // Combined Forecast Chart Data
  const forecastChartData = useMemo(() => {
    if (!forecasts || forecasts.length === 0) return [];

    // 7 days of projections
    const days = ['Day +1', 'Day +2', 'Day +3', 'Day +4', 'Day +5', 'Day +6', 'Day +7'];

    return days.map((dayLabel, dayIdx) => {
      const row: Record<string, any> = { day: dayLabel };

      forecasts.forEach((fc) => {
        const point = fc.forecasts?.[dayIdx];
        if (point) {
          row[fc.outlet_id] = Math.round(point.predicted_revenue);
        }
      });

      return row;
    });
  }, [forecasts]);

  const OUTLET_COLORS: Record<string, string> = {
    'OUT-01': '#4FAE7C',
    'OUT-02': '#D0555A',
    'OUT-03': '#E8A33D',
    'OUT-04': '#6C8CFF',
    'OUT-05': '#9D7BFF',
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="AI Insights"
        subtitle="AI-generated operational intelligence across the franchise network."
        badge={
          <Badge variant="accent">
            Pipeline {networkMetrics.outletCount} Outlets Scored
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={<RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />}
              onClick={refresh}
            >
              Refresh Data
            </Button>
            <Button
              variant="primary"
              size="sm"
              loading={isRunning}
              icon={<Play className="w-3.5 h-3.5" />}
              onClick={triggerPipeline}
            >
              {isRunning ? 'Recalculating...' : 'Retrain & Run Pipeline'}
            </Button>
          </div>
        }
      />

      {/* 1. NETWORK INTELLIGENCE SUMMARY (Section 4) */}
      <Card className="border-[#262B35] bg-[#12141A]">
        <CardHeader separator>
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-[#6C8CFF]" />
              <CardTitle>Network Intelligence Summary</CardTitle>
            </div>
            <span className="text-xs font-mono text-[#5C6478]">
              Updated: {new Date(pipelineData.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </CardHeader>
        <CardContent className="p-5 space-y-4">
          {/* Top KPI row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35]">
              <span className="text-[10px] font-mono text-[#5C6478] uppercase block">
                Network Health Score
              </span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-bold font-mono text-[#EDEFF3]">
                  {networkMetrics.avgScore}
                </span>
                <span className="text-xs text-[#5C6478]">/ 100</span>
              </div>
            </div>
            <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35]">
              <span className="text-[10px] font-mono text-[#4FAE7C] uppercase block font-semibold">
                Healthy Units
              </span>
              <span className="text-2xl font-bold font-mono text-[#4FAE7C] mt-1 block">
                {networkMetrics.healthyCount}
              </span>
            </div>
            <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35]">
              <span className="text-[10px] font-mono text-[#E8A33D] uppercase block font-semibold">
                At Risk Units
              </span>
              <span className="text-2xl font-bold font-mono text-[#E8A33D] mt-1 block">
                {networkMetrics.atRiskCount}
              </span>
            </div>
            <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35]">
              <span className="text-[10px] font-mono text-[#D0555A] uppercase block font-semibold">
                Critical Breaches
              </span>
              <span className="text-2xl font-bold font-mono text-[#D0555A] mt-1 block">
                {networkMetrics.criticalCount}
              </span>
            </div>
          </div>

          {/* Structured Visual Hierarchy: Signal → Impact → Recommended attention */}
          <div className="p-4 rounded-lg bg-[#171A20] border border-[#262B35] space-y-3">
            <div className="text-[10px] font-mono text-[#5C6478] uppercase tracking-wider font-semibold">
              Executive Telemetry Synthesis
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="space-y-1 p-3 rounded bg-[#12141A] border border-[#262B35]">
                <div className="flex items-center gap-1.5 text-[#6C8CFF] font-mono text-[11px] font-semibold">
                  <Activity className="w-3.5 h-3.5" />
                  <span>SIGNAL</span>
                </div>
                <p className="text-[#EDEFF3] font-medium leading-relaxed">
                  {networkMetrics.criticalCount > 0
                    ? `${networkMetrics.criticalCount} outlet(s) operating in Critical status with severe KPI threshold breaches.`
                    : 'Network operational telemetry stable across units.'}
                </p>
                <span className="text-[10px] text-[#8A93A6] font-mono block">
                  {networkMetrics.totalIssues} rule violations logged across {networkMetrics.outletCount} stores.
                </span>
              </div>

              <div className="space-y-1 p-3 rounded bg-[#12141A] border border-[#262B35]">
                <div className="flex items-center gap-1.5 text-[#E8A33D] font-mono text-[11px] font-semibold">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>IMPACT</span>
                </div>
                <p className="text-[#EDEFF3] font-medium leading-relaxed">
                  Perishable dairy spoilage at OUT-02 (6.1% wastage) and peak-hour barista deficits at OUT-05 (10.0% understaffing) directly threaten brand standards and revenue.
                </p>
                <span className="text-[10px] text-[#8A93A6] font-mono block">
                  Estimated revenue variance: -9.6% at affected locations.
                </span>
              </div>

              <div className="space-y-1 p-3 rounded bg-[#12141A] border border-[#262B35]">
                <div className="flex items-center gap-1.5 text-[#4FAE7C] font-mono text-[11px] font-semibold">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>RECOMMENDED ATTENTION</span>
                </div>
                <p className="text-[#EDEFF3] font-medium leading-relaxed">
                  Prioritize HACCP walk-in refrigeration inspection at Westside Hub, followed by flight-schedule aligned roster adjustments at Airport Terminal.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-[11px] mt-1 h-7"
                  onClick={() => navigate('/decision-center')}
                >
                  Review in Decision Center <ChevronRight className="w-3 h-3 ml-1" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 2. KEY RISKS & ML PREDICTIONS */}
      {riskPredictions && riskPredictions.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-[#D0555A]" />
              <h3 className="text-sm font-semibold text-[#EDEFF3]">
                XGBoost Underperformance Risk Predictions
              </h3>
            </div>
            <span className="text-xs font-mono text-[#5C6478]">
              Machine Learning Classification
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {riskPredictions.map((rp) => {
              const pct = Math.round(rp.risk_probability * 100);
              const isAtRisk = rp.predicted_label === 'At Risk';

              return (
                <Card
                  key={rp.outlet_id}
                  className={`border ${
                    isAtRisk ? 'border-[#D0555A]/40 bg-[#12141A]' : 'border-[#262B35] bg-[#12141A]'
                  }`}
                >
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-[#6C8CFF] bg-[#6C8CFF]/10 px-2 py-0.5 rounded">
                        {rp.outlet_id}
                      </span>
                      <Badge variant={isAtRisk ? 'danger' : 'success'}>
                        {rp.predicted_label.toUpperCase()}
                      </Badge>
                    </div>

                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-[#8A93A6]">Underperformance Probability</span>
                        <span
                          className={`font-mono font-bold ${
                            pct >= 70 ? 'text-[#D0555A]' : pct >= 40 ? 'text-[#E8A33D]' : 'text-[#4FAE7C]'
                          }`}
                        >
                          {pct}%
                        </span>
                      </div>
                      <div className="w-full bg-[#171A20] h-2 rounded-full overflow-hidden border border-[#262B35]">
                        <div
                          className={`h-full rounded-full transition-all ${
                            pct >= 70 ? 'bg-[#D0555A]' : pct >= 40 ? 'bg-[#E8A33D]' : 'bg-[#4FAE7C]'
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>

                    {rp.top_drivers && rp.top_drivers.length > 0 && (
                      <div className="space-y-1.5 pt-2 border-t border-[#262B35]">
                        <span className="text-[10px] font-mono text-[#5C6478] uppercase block">
                          Top Risk Drivers:
                        </span>
                        {rp.top_drivers.map((td, i) => (
                          <div key={i} className="flex items-center justify-between text-xs">
                            <span className="text-[#8A93A6] truncate">{td.feature}</span>
                            <span className="font-mono text-[11px] text-[#EDEFF3]">
                              {Math.round(td.importance * 100)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* 3. PERFORMANCE DRIVERS & COPILOT ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 7 cols: Copilot Assistant Shell */}
        <div className="lg:col-span-7">
          <OperationalCopilotChat />
        </div>

        {/* Right 5 cols: XGBoost Driver Feature Importance */}
        <div className="lg:col-span-5 space-y-6">
          <DriverImportanceChart importances={featureImportances} />
        </div>
      </div>

      {/* 4. 7-DAY FORECAST SIGNALS */}
      {forecastChartData.length > 0 && (
        <Card className="border-[#262B35] bg-[#12141A]">
          <CardHeader separator>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-[#6C8CFF]" />
                <div>
                  <CardTitle>7-Day Predictive Revenue Forecast Signals</CardTitle>
                  <span className="text-xs text-[#5C6478]">
                    XGBoost Multi-Unit Regression Projections
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1.5 text-xs font-mono">
                {Object.keys(OUTLET_COLORS).map((oid) => (
                  <span
                    key={oid}
                    className="px-2 py-0.5 rounded text-[11px] flex items-center gap-1 bg-[#171A20] border border-[#262B35]"
                  >
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: OUTLET_COLORS[oid] }}
                    />
                    {oid}
                  </span>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={forecastChartData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#262B35" />
                  <XAxis dataKey="day" stroke="#5C6478" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#5C6478"
                    fontSize={11}
                    tickFormatter={(val) => `$${(val / 1000).toFixed(1)}k`}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#171A20',
                      borderColor: '#262B35',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                  {Object.keys(OUTLET_COLORS).map((oid) => (
                    <Line
                      key={oid}
                      type="monotone"
                      dataKey={oid}
                      stroke={OUTLET_COLORS[oid]}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 5. CROSS-AGENT INTELLIGENCE FLOW (Section 17) */}
      <Card className="border-[#262B35] bg-[#12141A]">
        <CardHeader separator>
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-[#6C8CFF]" />
            <CardTitle>Cross-Agent Intelligence Telemetry Flow</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="p-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {[
              {
                agent: 'Outlet Performance Agent',
                signal: 'Revenue Velocity & Score',
                value: `${networkMetrics.avgScore}/100 Avg`,
                metric: 'Growth: +3.2%',
                color: '#6C8CFF',
              },
              {
                agent: 'Inventory Agent',
                signal: 'Stockout & Spoilage',
                value: '6.1% Max Wastage',
                metric: '3 POs Recommended',
                color: '#E8A33D',
              },
              {
                agent: 'Staff Agent',
                signal: 'Attendance & Roster Coverage',
                value: '10.0% Peak Shortfall',
                metric: '2 Floats Dispatched',
                color: '#9D7BFF',
              },
              {
                agent: 'Marketing Agent',
                signal: 'Campaign Attribution & ROI',
                value: '42.8% Mean ROI',
                metric: '1 Underperforming Discount',
                color: '#4FAE7C',
              },
              {
                agent: 'Audit & Compliance Agent',
                signal: 'HACCP & Inspection Score',
                value: '76.8% Average',
                metric: '1 Store Below Target',
                color: '#D0555A',
              },
            ].map((node, i) => (
              <div
                key={i}
                className="p-3.5 bg-[#171A20] rounded-lg border border-[#262B35] space-y-2 relative"
              >
                <div className="flex items-center justify-between">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: node.color }}
                  />
                  <span className="text-[10px] font-mono text-[#5C6478]">Agent 0{i + 1}</span>
                </div>
                <div>
                  <h5 className="text-xs font-semibold text-[#EDEFF3]">{node.agent}</h5>
                  <span className="text-[10px] text-[#8A93A6] block">{node.signal}</span>
                </div>
                <div className="pt-2 border-t border-[#262B35] text-[11px] font-mono">
                  <div className="text-[#EDEFF3] font-bold">{node.value}</div>
                  <div className="text-[#5C6478] text-[10px]">{node.metric}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 bg-[#171A20] rounded-lg border border-[#262B35] flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#4FAE7C]" />
              <span className="text-[#EDEFF3]">
                Combined Operational Synthesis: Multi-agent telemetry synchronized into deterministic decision queue.
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/decision-center')}
              className="text-xs shrink-0"
            >
              View Prioritized Decisions <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 6. ROOT CAUSES & RECOMMENDATIONS */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-[#6C8CFF]" />
          <h3 className="text-sm font-semibold text-[#EDEFF3]">
            Root Cause Reasoning Engine (All Outlets)
          </h3>
        </div>
        <RootCauseRecommendationCard findings={rootCauses} />
      </div>
    </div>
  );
};
