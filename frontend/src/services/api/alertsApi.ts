import { inventoryApi } from './inventoryApi';
import { workforceApi } from './workforceApi';
import { intelligenceApi } from './intelligenceApi';

export interface UnifiedAlert {
  id: string;
  domain: 'Inventory' | 'Workforce' | 'Audit' | 'Performance' | 'Pipeline';
  severity: 'critical' | 'high' | 'medium' | 'low';
  outletId: string;
  outletName?: string;
  title: string;
  description: string;
  timestamp: string;
  status: 'active' | 'acknowledged' | 'read_only' | 'resolved';
  sourceAgent: string;
  affectedArea: string;
  metric?: string;
  value?: number | null;
  threshold?: number | null;
  recommendation?: string;
}

// In-memory acknowledgment tracking for active session
const alertAckStore: Record<string, boolean> = {};

export const alertsApi = {
  /**
   * Fetch aggregated real-time alerts across Inventory, Workforce, and Pipeline Root Causes.
   */
  getAllAlerts: async (): Promise<UnifiedAlert[]> => {
    const alerts: UnifiedAlert[] = [];

    // 1. Inventory stock alerts
    try {
      const stockAlerts = await inventoryApi.getAlerts().catch(() => []);
      stockAlerts.forEach((sa, idx) => {
        const id = `inv-alert-${sa.product_id || idx}`;
        const sev = sa.alert_type === 'CRITICAL' ? 'critical' : sa.alert_type === 'LOW_STOCK' ? 'high' : 'medium';
        alerts.push({
          id,
          domain: 'Inventory',
          severity: sev,
          outletId: `OUT-${String(sa.outlet_id).padStart(2, '0')}`,
          outletName: sa.outlet_name || `Outlet #${sa.outlet_id}`,
          title: `${sa.alert_type.replace('_', ' ')}: ${sa.product_name || 'Product'}`,
          description: sa.message || `Current stock is ${sa.current_stock} (safety limit: ${sa.threshold}).`,
          timestamp: new Date().toISOString(),
          status: alertAckStore[id] ? 'acknowledged' : 'active',
          sourceAgent: 'Inventory Replenishment Agent',
          affectedArea: 'Perishable Stock / Supply Runway',
          metric: 'current_stock',
          value: parseFloat(String(sa.current_stock)) || null,
          threshold: parseFloat(String(sa.threshold)) || null,
          recommendation: 'Initiate vendor purchase order and reallocate buffer inventory from adjacent distribution hub.',
        });
      });
    } catch {
      // Handled gracefully
    }

    // 2. Workforce staffing alerts
    try {
      const staffAlerts = await workforceApi.getStaffingAlerts().catch(() => []);
      staffAlerts.forEach((wa, idx) => {
        const id = `staff-alert-${wa.outlet_id}-${idx}`;
        const sev = wa.alert_type === 'SHORTAGE' ? 'high' : 'medium';
        alerts.push({
          id,
          domain: 'Workforce',
          severity: sev,
          outletId: `OUT-${String(wa.outlet_id).padStart(2, '0')}`,
          outletName: wa.outlet_name || `Outlet #${wa.outlet_id}`,
          title: `Staffing ${wa.alert_type}: ${wa.scheduled_staff_count}/${wa.expected_staff_count} Scheduled`,
          description: wa.message,
          timestamp: new Date().toISOString(),
          status: alertAckStore[id] ? 'acknowledged' : 'active',
          sourceAgent: 'Workforce Dispatch Agent',
          affectedArea: 'Shift Roster & Peak Coverage',
          metric: 'scheduled_staff_count',
          value: wa.scheduled_staff_count,
          threshold: wa.expected_staff_count,
          recommendation: 'Dispatch float baristas or adjust shift overlap hours to protect peak-hour throughput.',
        });
      });
    } catch {
      // Handled gracefully
    }

    // 3. Pipeline Root Causes
    try {
      const rootCauses = await intelligenceApi.getRootCauses().catch(() => []);
      rootCauses.forEach((rc) => {
        rc.issues.forEach((issue, issueIdx) => {
          const id = `rc-alert-${rc.outlet_id}-${issueIdx}`;
          const sev = (issue.severity?.toLowerCase() || 'medium') as 'critical' | 'high' | 'medium' | 'low';
          alerts.push({
            id,
            domain: (issue.domain === 'Staff' ? 'Workforce' : issue.domain) as any,
            severity: sev,
            outletId: rc.outlet_id,
            outletName: rc.outlet_id,
            title: issue.finding,
            description: issue.recommendation,
            timestamp: new Date().toISOString(),
            status: alertAckStore[id] ? 'acknowledged' : 'active',
            sourceAgent: `${issue.domain} Agent`,
            affectedArea: `${issue.domain} Operational Compliance`,
            metric: issue.metric,
            value: issue.value ?? null,
            threshold: issue.threshold ?? null,
            recommendation: issue.recommendation,
          });
        });
      });
    } catch {
      // Handled gracefully
    }

    return alerts;
  },

  /**
   * Mark alert as acknowledged in session store
   */
  acknowledgeAlert: (alertId: string): void => {
    alertAckStore[alertId] = true;
  },

  /**
   * Stub for legacy resolve calls (read-only incident telemetry)
   */
  resolveAlert: (_alertId: string, _note?: string): void => {
    // Read-only incident telemetry: resolution endpoint not exposed by backend
  },
};

