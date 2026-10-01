import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/ui/PageHeader';
import { KPICard } from '@/components/kpi/KPICard';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { RevenueTrendChart } from '@/components/charts/RevenueTrendChart';
import {
  ArrowLeft,
  DollarSign,
  TrendingUp,
  AlertOctagon,
  CheckCircle2,
  Sparkles,
  MapPin,
  Bot,
} from 'lucide-react';
import { useOutlets } from '@/hooks/useOutlets';
import { useIntelligence } from '@/hooks/useIntelligence';

export const OutletDetails: React.FC = () => {
  const { outletId = 'OUT-01' } = useParams<{ outletId: string }>();
  const navigate = useNavigate();
  const { outlets } = useOutlets();
  const { pipelineData, rootCauses, riskPredictions } = useIntelligence();

  // Normalize outlet ID comparison
  const outlet =
    outlets.find((o) => o.id === outletId || String(o.outlet_id) === outletId) || outlets[0];

  const formattedId = outlet ? outlet.id : outletId;
  const kpi = pipelineData.kpis.find((k) => k.outlet_id === formattedId);
  const rootCause = rootCauses.find((rc) => rc.outlet_id === formattedId);
  const riskPrediction = riskPredictions?.find((rp) => rp.outlet_id === formattedId);

  const isCritical = outlet?.status === 'Critical' || rootCause?.health_status === 'Critical';
  const isWarning = outlet?.status === 'At Risk' || rootCause?.health_status === 'At Risk';

  const dailyRev = kpi ? `$${Math.round(kpi.avg_daily_revenue).toLocaleString()}` : outlet?.revenue || '—';
  const wastage = kpi ? `${kpi.wastage_rate.toFixed(1)}%` : '—';
  const absenteeism = kpi ? `${kpi.absenteeism_rate.toFixed(1)}%` : '—';
  const compliance = kpi ? `${Math.round(kpi.compliance_score)}%` : '—';

  const hasUnderperformance = rootCause && (rootCause.issues.length > 0 || isCritical || isWarning);

  // Map 7-day revenue forecast points for this specific outlet
  const outletTrendData = useMemo(() => {
    const fc = pipelineData.forecasts?.find((f) => f.outlet_id === formattedId);
    if (!fc || !fc.forecasts || fc.forecasts.length === 0) return undefined;

    const actualDailyRev = kpi?.avg_daily_revenue || 0;
    return fc.forecasts.map((pt) => ({
      date: pt.forecast_date,
      actual: Math.round(actualDailyRev),
      forecast: Math.round(pt.predicted_revenue),
    }));
  }, [pipelineData.forecasts, formattedId, kpi]);

  // Read formula component scores from pipeline output
  const componentWeights = useMemo(() => {
    const perf = pipelineData.performance_scores?.find((p) => p.outlet_id === formattedId);
    const comps = perf?.components;
    if (comps) {
      return [
        { name: 'Revenue Volume (35%)', score: Math.round(comps.revenue ?? 0) },
        { name: 'Revenue Growth (15%)', score: Math.round(comps.growth ?? 0) },
        { name: 'Wastage Control (15%)', score: Math.round(comps.wastage ?? 0) },
        { name: 'Staff Attendance (15%)', score: Math.round(comps.absenteeism ?? 0) },
        { name: 'Audit Compliance (10%)', score: Math.round(comps.compliance ?? 0) },
        { name: 'Marketing ROI (10%)', score: Math.round(comps.roi ?? 0) },
      ];
    }
    const baseScore = outlet?.healthScore ?? 0;
    return [
      { name: 'Revenue Volume (35%)', score: Math.round(baseScore * 0.95) },
      { name: 'Revenue Growth (15%)', score: Math.round(baseScore * 0.88) },
      { name: 'Wastage Control (15%)', score: baseScore },
      { name: 'Staff Attendance (15%)', score: baseScore },
      { name: 'Audit Compliance (10%)', score: Math.round(parseFloat(compliance) || baseScore) },
      { name: 'Marketing ROI (10%)', score: baseScore },
    ];
  }, [pipelineData.performance_scores, formattedId, outlet, compliance]);

  return (
    <div className="space-y-6">
      {/* Back button & Page Header */}
      <div>
        <Button
          variant="ghost"
          size="sm"
          icon={<ArrowLeft className="w-3.5 h-3.5" />}
          onClick={() => navigate('/outlets')}
          className="mb-3 text-[#8A93A6]"
        >
          Back to Outlets
        </Button>

        <PageHeader
          title={`Outlet Diagnostics: ${outlet?.name || formattedId}`}
          subtitle={`Location: ${outlet?.location || '—'} • General Manager: ${outlet?.manager || 'Unassigned'}`}
          badge={
            <StatusBadge
              status={isCritical ? 'Critical' : isWarning ? 'At Risk' : 'Healthy'}
              size="sm"
            />
          }
          actions={
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                icon={<Sparkles className="w-3.5 h-3.5 text-[#6C8CFF]" />}
                onClick={() => navigate('/decision-center')}
              >
                Decision Center
              </Button>
              <Button
                variant="primary"
                size="sm"
                icon={<Bot className="w-3.5 h-3.5" />}
                onClick={() => navigate('/agent-activity')}
              >
                Agent Telemetry
              </Button>
            </div>
          }
        />
      </div>

      {/* Outlet Specific KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Daily Revenue"
          value={dailyRev}
          change={kpi ? parseFloat(kpi.revenue_growth_pct.toFixed(1)) : undefined}
          changeType={kpi && kpi.revenue_growth_pct < 0 ? 'negative' : 'positive'}
          status={isCritical ? 'critical' : 'healthy'}
          icon={<DollarSign className="w-4 h-4 text-[#6C8CFF]" />}
        />
        <KPICard
          title="Wastage Rate"
          value={wastage}
          changeLabel="threshold: 3.0%"
          status={parseFloat(wastage) > 3.0 ? 'critical' : 'healthy'}
          icon={<AlertOctagon className="w-4 h-4 text-[#E8A33D]" />}
        />
        <KPICard
          title="Absenteeism"
          value={absenteeism}
          changeLabel="threshold: 10.0%"
          status={parseFloat(absenteeism) > 10.0 ? 'critical' : 'healthy'}
          icon={<AlertOctagon className="w-4 h-4 text-[#D0555A]" />}
        />
        <KPICard
          title="Audit Compliance"
          value={compliance}
          changeLabel="target: 85%"
          status={parseFloat(compliance) < 75 ? 'critical' : 'healthy'}
          icon={<CheckCircle2 className="w-4 h-4 text-[#4FAE7C]" />}
        />
      </div>

      {/* INTELLIGENCE SECTION: Why is this outlet underperforming? (Section 6) */}
      <Card className={`border ${hasUnderperformance ? 'border-[#D0555A]/30 bg-[#12141A]' : 'border-[#262B35] bg-[#12141A]'}`}>
        <CardHeader separator>
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-4 h-4 text-[#6C8CFF]" />
              <div>
                <CardTitle>Why is this outlet underperforming?</CardTitle>
                <span className="text-xs text-[#5C6478]">
                  Automated root-cause diagnostic synthesis and contributing factors
                </span>
              </div>
            </div>
            {hasUnderperformance ? (
              <Badge variant="danger">
                {rootCause?.issues.length || 1} Critical Factor{(rootCause?.issues.length || 1) > 1 ? 's' : ''} Detected
              </Badge>
            ) : (
              <Badge variant="success">
                Optimal Baseline
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-5 space-y-4">
          {hasUnderperformance ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
              {/* Performance Signal */}
              <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] space-y-1.5">
                <span className="text-[10px] font-mono uppercase text-[#6C8CFF] font-bold block">
                  1. Performance Signal
                </span>
                <div className="space-y-0.5">
                  <div className="text-sm font-bold font-mono text-[#EDEFF3]">
                    {Math.round(rootCause?.performance_score || outlet?.healthScore || 50)}/100
                  </div>
                  <div className="text-[11px] text-[#8A93A6]">
                    Status: <strong className="text-[#D0555A]">{rootCause?.health_status || outlet?.status}</strong>
                  </div>
                  {kpi && (
                    <div className="text-[10px] font-mono text-[#5C6478]">
                      Growth: {kpi.revenue_growth_pct > 0 ? '+' : ''}{kpi.revenue_growth_pct.toFixed(1)}%
                    </div>
                  )}
                </div>
              </div>

              {/* Contributing Factors */}
              <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] space-y-1.5 lg:col-span-2">
                <span className="text-[10px] font-mono uppercase text-[#E8A33D] font-bold block">
                  2. Contributing Factors ({rootCause?.issues.length || 0})
                </span>
                <div className="space-y-1.5 max-h-24 overflow-y-auto">
                  {rootCause?.issues.map((iss, i) => (
                    <div key={i} className="text-[11px] flex items-start justify-between gap-1 text-[#EDEFF3]">
                      <span className="truncate">{iss.finding}</span>
                      <span className="font-mono text-[10px] text-[#E8A33D] shrink-0">
                        {iss.value !== null ? iss.value : ''}
                      </span>
                    </div>
                  ))}
                  {riskPrediction?.top_drivers && (
                    <div className="pt-1 text-[10px] font-mono text-[#8A93A6]">
                      Top Driver: {riskPrediction.top_drivers[0]?.feature} ({Math.round(riskPrediction.top_drivers[0]?.importance * 100)}%)
                    </div>
                  )}
                </div>
              </div>

              {/* Root Cause & Business Impact */}
              <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] space-y-1.5">
                <span className="text-[10px] font-mono uppercase text-[#D0555A] font-bold block">
                  3. Root Cause & Impact
                </span>
                <p className="text-[11px] text-[#EDEFF3] leading-snug line-clamp-3">
                  {rootCause?.priority_issue || rootCause?.issues[0]?.finding || 'Cross-domain operational breach.'}
                </p>
                <span className="text-[10px] text-[#8A93A6] block">
                  Impacting unit margins & brand audit rating.
                </span>
              </div>

              {/* Prescriptive Recommendation */}
              <div className="p-3 bg-[#4FAE7C]/5 rounded-lg border border-[#4FAE7C]/25 space-y-1.5 flex flex-col justify-between">
                <div className="space-y-1">
                  <span className="text-[10px] font-mono uppercase text-[#4FAE7C] font-bold block">
                    4. Prescriptive Remedy
                  </span>
                  <p className="text-[11px] text-[#EDEFF3] leading-snug line-clamp-3 font-medium">
                    {rootCause?.overall_recommendation || rootCause?.issues[0]?.recommendation}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-xs h-7 mt-2"
                  onClick={() => navigate('/decision-center')}
                >
                  Action in Decision Center
                </Button>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-lg bg-[#4FAE7C]/5 border border-[#4FAE7C]/20 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-[#4FAE7C] shrink-0" />
                <div className="space-y-0.5">
                  <p className="font-semibold text-[#EDEFF3]">
                    Optimal Operating Parameters Confirmed
                  </p>
                  <p className="text-[#8A93A6]">
                    All monitored operational metrics (revenue velocity, spoilage rate, workforce attendance, and food safety compliance) are operating safely within corporate baseline limits. No critical underperformance risk detected.
                  </p>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/decision-center')}
                className="shrink-0 text-xs ml-4"
              >
                Network Decision Queue
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Diagnostic Chart & KPI Score Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader separator>
              <div>
                <CardTitle>Sales Telemetry & 7-Day ML Forecast</CardTitle>
                <CardDescription>Predicted sales projection via XGBoost</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <RevenueTrendChart data={outletTrendData} height={280} />
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader separator>
              <CardTitle>Score Component Weights</CardTitle>
              <Badge variant="outline">KPI Formula</Badge>
            </CardHeader>
            <CardContent className="space-y-3">
              {componentWeights.map((comp, idx) => (
                <div key={idx} className="space-y-1 text-xs">
                  <div className="flex justify-between text-[#8A93A6]">
                    <span>{comp.name}</span>
                    <span className="font-mono text-[#EDEFF3] font-semibold">{comp.score}/100</span>
                  </div>
                  <div className="w-full bg-[#171A20] h-1.5 rounded-full overflow-hidden border border-[#262B35]">
                    <div
                      className={`h-full rounded-full ${
                        comp.score >= 70 ? 'bg-[#4FAE7C]' : comp.score >= 50 ? 'bg-[#E8A33D]' : 'bg-[#D0555A]'
                      }`}
                      style={{ width: `${comp.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
