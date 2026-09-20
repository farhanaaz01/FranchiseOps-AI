// ============================================================
// Backend API Types — mapped exactly from app/schemas.py
// ============================================================

// ----- Franchise & Outlet -----
export interface FranchiseResponse {
  franchise_id: number;
  franchise_name: string;
  region: string | null;
  owner_name: string | null;
}

export interface OutletResponse {
  outlet_id: number;
  franchise_id: number;
  outlet_name: string;
  location: string | null;
  status: string | null;
}

export interface OutletCreate {
  franchise_id: number;
  outlet_name: string;
  location?: string | null;
  status?: string;
}

export interface InventoryTransactionCreate {
  inventory_id: number;
  transaction_type: 'IN' | 'OUT' | 'WASTAGE' | 'RETURN';
  quantity: number | string;
  reason?: string | null;
}

export interface ScheduleCreate {
  employee_id: number;
  outlet_id: number;
  shift_date: string;
  start_time: string;
  end_time: string;
  role?: string | null;
}

export interface MarketingCampaignCreate {
  outlet_id: number;
  campaign_name: string;
  start_date: string;
  end_date: string;
  budget: number | string;
  channel?: string | null;
}

// ----- Sales -----
export interface SaleResponse {
  sale_id: number;
  outlet_id: number;
  sale_date: string;
  revenue: string;
  transaction_count: number;
}

// ----- Products & Inventory -----
export interface ProductResponse {
  product_id: number;
  product_name: string;
  category: string | null;
  unit: string | null;
  unit_price: string;
}

export interface InventoryResponse {
  inventory_id: number;
  outlet_id: number;
  product_id: number;
  current_stock: string;
  reorder_point: string;
  reorder_quantity: string;
  max_stock: string | null;
  last_updated: string | null;
  product?: ProductResponse | null;
  outlet?: OutletResponse | null;
}

export interface InventoryTransactionResponse {
  transaction_id: number;
  inventory_id: number;
  transaction_date: string;
  transaction_type: 'IN' | 'OUT' | 'WASTAGE' | 'RETURN';
  quantity: string;
  reason: string | null;
}

// ----- Dashboard / Performance DTOs -----
export interface RevenueTrendDTO {
  date: string;
  revenue: string;
  transactions: number;
}

export interface OutletPerformanceDTO {
  outlet_id: number;
  outlet_name: string;
  location: string | null;
  status: string | null;
  franchise_id: number;
  franchise_name: string | null;
  total_revenue: string;
  total_transactions: number;
  average_revenue_per_day: string;
  average_revenue_per_transaction: string;
  health_score: string;
  performance_label: string;
  revenue_trend: RevenueTrendDTO[];
}

export interface FranchiseComparisonDTO {
  outlet_id: number;
  outlet_name: string;
  location: string | null;
  status: string | null;
  total_revenue: string;
  total_transactions: number;
  health_score: string;
  rank: number | null;
  performance_label: string;
}

export interface DashboardSummaryDTO {
  total_outlets: number;
  active_outlets: number;
  underperforming_outlets: number;
  total_revenue: string;
  total_transactions: number;
  average_health_score: string;
  top_performing_outlet: FranchiseComparisonDTO | null;
  lowest_performing_outlet: FranchiseComparisonDTO | null;
  recent_underperformers: FranchiseComparisonDTO[];
}

export interface UnderperformingOutletDTO {
  outlet_id: number;
  outlet_name: string;
  location: string | null;
  franchise_id: number;
  franchise_name: string | null;
  total_revenue: string;
  franchise_average_revenue: string;
  health_score: string;
  reason: string;
}

// ----- Inventory Dashboard DTOs -----
export interface InventoryStatusDTO {
  inventory_id: number;
  outlet_id: number;
  outlet_name: string | null;
  product_id: number;
  product_name: string | null;
  category: string | null;
  current_stock: string;
  reorder_point: string;
  reorder_quantity: string;
  max_stock: string | null;
  status: 'Critical' | 'Low Stock' | 'Overstock' | 'Normal';
}

export interface DemandForecastDTO {
  outlet_id: number;
  outlet_name: string | null;
  product_id: number;
  product_name: string | null;
  forecasted_daily_demand: string;
  forecast_period_days: number;
  total_historical_demand: string;
}

export interface StockAlertDTO {
  alert_type: 'LOW_STOCK' | 'CRITICAL' | 'OVERSTOCK';
  outlet_id: number;
  outlet_name: string | null;
  product_id: number;
  product_name: string | null;
  current_stock: string;
  threshold: string;
  message: string;
}

export interface ReplenishmentRecommendationDTO {
  outlet_id: number;
  outlet_name: string | null;
  product_id: number;
  product_name: string | null;
  current_stock: string;
  forecasted_daily_demand: string;
  days_until_stockout: number | null;
  recommended_order_quantity: string;
  recommended_order_date: string | null;
  reason: string;
}

export interface InventoryDashboardDTO {
  total_products: number;
  total_inventory_items: number;
  total_stock_value: string;
  low_stock_count: number;
  critical_stock_count: number;
  overstock_count: number;
  total_wastage_30_days: string;
  top_alerts: StockAlertDTO[];
  replenishment_recommendations: ReplenishmentRecommendationDTO[];
}

// ----- Workforce DTOs -----
export interface EmployeeResponse {
  employee_id: number;
  outlet_id: number;
  full_name: string;
  role: string | null;
  email: string | null;
  phone: string | null;
  hourly_rate: string;
  hire_date: string | null;
  status: string | null;
}

export interface EmployeePerformanceDTO {
  employee_id: number;
  full_name: string;
  outlet_id: number;
  outlet_name: string | null;
  role: string | null;
  total_days: number;
  present_days: number;
  absent_days: number;
  late_days: number;
  half_day_days: number;
  attendance_rate: string;
  total_hours_worked: string;
  average_hours_per_day: string;
  productivity_score: string;
  performance_label: string;
}

export interface OutletWorkforceDTO {
  outlet_id: number;
  outlet_name: string | null;
  total_employees: number;
  active_employees: number;
  average_attendance_rate: string;
  total_hours_worked: string;
  staffing_shortage_count: number;
  employee_performances: EmployeePerformanceDTO[];
}

export interface StaffingAlertDTO {
  outlet_id: number;
  outlet_name: string | null;
  alert_type: 'SHORTAGE' | 'OVERSTAFFED';
  scheduled_staff_count: number;
  expected_staff_count: number;
  message: string;
}

export interface WorkforceDashboardDTO {
  total_employees: number;
  active_employees: number;
  total_outlets_with_employees: number;
  average_attendance_rate: string;
  total_hours_worked: string;
  top_performers: EmployeePerformanceDTO[];
  underperformers: EmployeePerformanceDTO[];
  staffing_alerts: StaffingAlertDTO[];
}

// ----- Marketing DTOs -----
export interface MarketingCampaignResponse {
  campaign_id: number;
  outlet_id: number;
  campaign_name: string;
  campaign_type: string | null;
  start_date: string;
  end_date: string;
  budget: string;
  status: string | null;
}

export interface CampaignAnalyticsDTO {
  campaign_id: number;
  campaign_name: string;
  outlet_id: number;
  outlet_name: string | null;
  campaign_type: string | null;
  start_date: string;
  end_date: string;
  budget: string;
  total_revenue: string;
  total_impressions: number;
  total_clicks: number;
  total_conversions: number;
  average_engagement_score: string;
  roi_percentage: string;
  engagement_rate: string;
  conversion_rate: string;
  status: string;
  performance_label: string;
}

export interface MarketingDashboardDTO {
  total_campaigns: number;
  active_campaigns: number;
  total_budget: string;
  total_revenue: string;
  overall_roi_percentage: string;
  average_engagement_rate: string;
  average_conversion_rate: string;
  top_campaigns: CampaignAnalyticsDTO[];
  underperforming_campaigns: CampaignAnalyticsDTO[];
  campaigns_by_type: Record<string, number>;
}

// ----- Attendance & Schedule -----
export interface AttendanceResponse {
  attendance_id: number;
  employee_id: number;
  attendance_date: string;
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'HALF_DAY';
  hours_worked: string;
  notes: string | null;
}

export interface ScheduleResponse {
  schedule_id: number;
  employee_id: number;
  schedule_date: string;
  shift_start: string | null;
  shift_end: string | null;
  status: string | null;
}
