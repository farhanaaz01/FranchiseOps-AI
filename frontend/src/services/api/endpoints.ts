// ============================================================
// API Endpoint Constants — derived from actual app/routers/**
// DO NOT invent endpoints. These are verified from source.
// ============================================================

// ---- Core Entities ----
export const ENDPOINTS = {
  // Franchises
  FRANCHISES: '/api/franchises',
  FRANCHISE: (id: number) => `/api/franchises/${id}`,

  // Outlets
  OUTLETS: '/api/outlets',
  OUTLET: (id: number) => `/api/outlets/${id}`,
  OUTLETS_BY_FRANCHISE: (franchiseId: number) => `/api/outlets/franchise/${franchiseId}`,

  // Sales
  SALES: '/api/sales',
  SALE: (id: number) => `/api/sales/${id}`,
  SALES_BY_OUTLET: (outletId: number) => `/api/sales/outlet/${outletId}`,

  // Products
  PRODUCTS: '/api/products',
  PRODUCT: (id: number) => `/api/products/${id}`,

  // Inventory CRUD
  INVENTORY: '/api/inventory',
  INVENTORY_ITEM: (id: number) => `/api/inventory/${id}`,
  INVENTORY_BY_OUTLET: (outletId: number) => `/api/inventory/outlet/${outletId}`,

  // Inventory Transactions
  INVENTORY_TRANSACTIONS: '/api/inventory_transactions',
  INVENTORY_TRANSACTION: (id: number) => `/api/inventory_transactions/${id}`,
  INVENTORY_TRANSACTIONS_BY_INVENTORY: (inventoryId: number) =>
    `/api/inventory_transactions/inventory/${inventoryId}`,

  // Employees
  EMPLOYEES: '/api/employees',
  EMPLOYEE: (id: number) => `/api/employees/${id}`,
  EMPLOYEES_BY_OUTLET: (outletId: number) => `/api/employees/outlet/${outletId}`,

  // Attendance
  ATTENDANCE: '/api/attendance',
  ATTENDANCE_RECORD: (id: number) => `/api/attendance/${id}`,
  ATTENDANCE_BY_EMPLOYEE: (employeeId: number) => `/api/attendance/employee/${employeeId}`,

  // Schedules
  SCHEDULES: '/api/schedules',
  SCHEDULE: (id: number) => `/api/schedules/${id}`,
  SCHEDULES_BY_EMPLOYEE: (employeeId: number) => `/api/schedules/employee/${employeeId}`,

  // Marketing Campaigns
  MARKETING_CAMPAIGNS: '/api/marketing/campaigns',
  MARKETING_CAMPAIGN: (id: number) => `/api/marketing/campaigns/${id}`,
  MARKETING_CAMPAIGNS_BY_OUTLET: (outletId: number) =>
    `/api/marketing/campaigns/outlet/${outletId}`,

  // Campaign Performance
  CAMPAIGN_PERFORMANCE: '/api/campaign_performance',
  CAMPAIGN_PERFORMANCE_RECORD: (id: number) => `/api/campaign_performance/${id}`,
  CAMPAIGN_PERFORMANCE_BY_CAMPAIGN: (campaignId: number) =>
    `/api/campaign_performance/campaign/${campaignId}`,

  // ---- Dashboard Analytics ----
  DASHBOARD_SUMMARY: '/api/dashboard/summary',
  DASHBOARD_OUTLET_PERFORMANCE: (outletId: number) => `/api/dashboard/outlets/${outletId}`,
  DASHBOARD_FRANCHISE_COMPARE: (franchiseId: number) =>
    `/api/dashboard/franchises/${franchiseId}/compare`,
  DASHBOARD_UNDERPERFORMING: '/api/dashboard/underperforming',

  // ---- Inventory Dashboard ----
  INVENTORY_DASHBOARD_SUMMARY: '/api/inventory/dashboard/summary',
  INVENTORY_DASHBOARD_STATUS: '/api/inventory/dashboard/status',
  INVENTORY_DASHBOARD_ALERTS: '/api/inventory/dashboard/alerts',
  INVENTORY_DASHBOARD_REPLENISHMENT: '/api/inventory/dashboard/replenishment',
  INVENTORY_DASHBOARD_FORECAST: (outletId: number, productId: number) =>
    `/api/inventory/dashboard/forecast/${outletId}/${productId}`,

  // ---- Workforce Dashboard ----
  WORKFORCE_DASHBOARD_SUMMARY: '/api/workforce/dashboard/summary',
  WORKFORCE_DASHBOARD_OUTLET: (outletId: number) =>
    `/api/workforce/dashboard/outlets/${outletId}`,
  WORKFORCE_DASHBOARD_EMPLOYEE: (employeeId: number) =>
    `/api/workforce/dashboard/employees/${employeeId}`,
  WORKFORCE_DASHBOARD_ALERTS: '/api/workforce/dashboard/alerts',

  // ---- Marketing Dashboard ----
  MARKETING_DASHBOARD_SUMMARY: '/api/marketing/dashboard/summary',
  MARKETING_DASHBOARD_CAMPAIGN: (campaignId: number) =>
    `/api/marketing/dashboard/campaigns/${campaignId}`,
  MARKETING_DASHBOARD_ALL_CAMPAIGNS: '/api/marketing/dashboard/campaigns',

  // ---- System ----
  ROOT: '/',
} as const;
