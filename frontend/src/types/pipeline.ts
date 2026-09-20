// ============================================================
// Pipeline / Intelligence Types — mapped from data_engine/schemas.py
// These represent the ML pipeline output (PipelineOutput schema)
// ============================================================

export type HealthStatus = 'Healthy' | 'At Risk' | 'Critical';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type AgentDomain = 'Outlet' | 'Inventory' | 'Staff' | 'Marketing' | 'Audit' | 'Overall';
export type PredictedLabel = 'Healthy' | 'At Risk';

/**
 * Per-outlet KPI snapshot — from kpi_engine.py
 * Formula: 0.35*revenue + 0.15*growth + 0.15*wastage + 0.15*absenteeism + 0.10*compliance + 0.10*roi
 */
export interface OutletKPI {
  outlet_id: string;
  avg_daily_revenue: number;
  revenue_growth_pct: number;
  wastage_rate: number;
  absenteeism_rate: number;
  peak_understaffed_pct: number;
  compliance_score: number;
  campaign_roi: number;
  stockout_risk_flag: boolean;
}

/**
 * Composite 0-100 performance score
 * Healthy >= 70, At Risk 50-70, Critical < 50
 */
export interface PerformanceScore {
  outlet_id: string;
  performance_score: number;
  health_status: HealthStatus;
  components: Record<string, number> | null;
}

/** Single forecast day — from ml_models.py XGBRegressor */
export interface ForecastPoint {
  outlet_id: string;
  forecast_date: string;
  predicted_revenue: number;
  model_version: string;
}

/** 7-day revenue forecast for one outlet */
export interface ForecastResult {
  outlet_id: string;
  forecasts: ForecastPoint[];
  trained_on_rows: number | null;
  generated_at: string;
}

/** Feature importance entry from risk classifier */
export interface RiskFeatureImportance {
  feature: string;
  importance: number;
}

/** Underperformance risk prediction — from XGBClassifier */
export interface RiskPrediction {
  outlet_id: string;
  risk_probability: number;
  predicted_label: PredictedLabel;
  top_drivers: RiskFeatureImportance[];
}

/**
 * Single rule-based finding from root_cause_engine.py
 * Thresholds: wastage>3%, understaffed>15%, absenteeism>10%,
 * compliance<75, growth<0%, roi<0%, stockout<3 days
 */
export interface RootCauseIssue {
  domain: AgentDomain;
  severity: Severity;
  metric: string;
  value: number | null;
  threshold: number | null;
  finding: string;
  recommendation: string;
}

/** Per-outlet root cause analysis result */
export interface RootCauseFinding {
  outlet_id: string;
  performance_score: number;
  health_status: HealthStatus;
  issues: RootCauseIssue[];
  priority_issue: string | null;
  overall_recommendation: string;
}

/**
 * Full pipeline output envelope from run_outlet_intelligence_pipeline()
 * Populated from pipeline_output.json structure
 */
export interface PipelineOutput {
  generated_at: string;
  outlet_count: number;
  kpis: OutletKPI[];
  performance_scores: PerformanceScore[];
  forecasts: ForecastResult[];
  risk_predictions: RiskPrediction[];
  feature_importances: RiskFeatureImportance[];
  root_causes: RootCauseFinding[];
}
