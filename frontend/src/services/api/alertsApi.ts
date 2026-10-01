import { apiGet, apiPost, apiPatch } from './apiClient';
import { inventoryApi } from './inventoryApi';
import { workforceApi } from './workforceApi';
import { intelligenceApi } from './intelligenceApi';
import type { NotificationResponse } from '@/types/backend';

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
  backendNotificationId?: number;
}

// In-memory status tracking cache
const alertStatusStore: Record<string, 'active' | 'acknowledged' | 'resolved'> = {};

export const alertsApi = {
  /**
   * Fetch aggregated real-time alerts across backend Notifications API,
   * Inventory, Workforce, and Pipeline Root Causes.
   */
  getAllAlerts: async (): Promise<UnifiedAlert[]> => {
    // 1. Try to fetch from real backend /api/notifications
    try {
      let notifications = await apiGet<NotificationResponse[]>('/api/notifications').catch(() => []);

      // If empty, attempt to trigger /api/notifications/sync once to populate backend rows from agents
      if (!notifications || notifications.length === 0) {
        await apiPost('/api/notifications/sync', {}).catch(() => null);
        notifications = await apiGet<NotificationResponse[]>('/api/notifications').catch(() => []);
      }

      if (notifications && notifications.length > 0) {
        return notifications.map((n) => {
          const id = String(n.notification_id);
          const cachedStatus = alertStatusStore[id];
          const finalStatus = cachedStatus || n.status || 'active';

          const outletKey = n.outlet_id
            ? `OUT-${String(n.outlet_id).padStart(2, '0')}`
            : 'CORP-HQ';

          const validDomain = (
            ['Inventory', 'Workforce', 'Audit', 'Performance', 'Pipeline'].includes(n.domain)
              ? n.domain
              : 'Pipeline'
          ) as UnifiedAlert['domain'];

          const validSev = (
            ['critical', 'high', 'medium', 'low'].includes(n.severity?.toLowerCase())
              ? n.severity.toLowerCase()
              : 'medium'
          ) as UnifiedAlert['severity'];

          return {
            id,
            backendNotificationId: n.notification_id,
            domain: validDomain,
            severity: validSev,
            outletId: outletKey,
            outletName: n.outlet_name || outletKey,
            title: n.title,
            description: n.description || '',
            timestamp: n.created_at || new Date().toISOString(),
            status: finalStatus,
            sourceAgent: n.source_agent || `${n.domain} Agent`,
            affectedArea: n.affected_area || 'Operations',
            metric: n.metric || undefined,
            value: n.metric_value !== null ? parseFloat(String(n.metric_value)) : null,
            threshold: n.threshold_value !== null ? parseFloat(String(n.threshold_value)) : null,
            recommendation: n.recommendation || undefined,
          };
        });
      }
    } catch {
      // If notification router is unavailable, fall through to domain-level aggregation
    }

    // 2. Fallback: Aggregate from real inventory, workforce, and pipeline APIs
    const alerts: UnifiedAlert[] = [];

    // Inventory stock alerts
    try {
      const stockAlerts = await inventoryApi.getAlerts().catch(() => []);
      stockAlerts.forEach((sa, idx) => {
        const id = `inv-alert-${sa.outlet_id}-${sa.product_id || idx}`;
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
          status: alertStatusStore[id] || 'active',
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

    // Workforce staffing alerts
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
          status: alertStatusStore[id] || 'active',
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

    // Pipeline Root Causes
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
            status: alertStatusStore[id] || 'active',
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
   * Mark alert as acknowledged, updating backend status if numeric ID
   */
  acknowledgeAlert: async (alertId: string): Promise<void> => {
    alertStatusStore[alertId] = 'acknowledged';
    const numId = parseInt(alertId, 10);
    if (!isNaN(numId)) {
      await apiPatch(`/api/notifications/${numId}`, { status: 'acknowledged' }).catch(() => null);
    }
  },

  /**
   * Mark alert as resolved, updating backend status if numeric ID
   */
  resolveAlert: async (alertId: string, _note?: string): Promise<void> => {
    alertStatusStore[alertId] = 'resolved';
    const numId = parseInt(alertId, 10);
    if (!isNaN(numId)) {
      await apiPatch(`/api/notifications/${numId}`, { status: 'resolved' }).catch(() => null);
    }
  },
};
