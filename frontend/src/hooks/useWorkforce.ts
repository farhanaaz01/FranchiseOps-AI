import { useState, useEffect, useCallback } from 'react';
import { workforceApi } from '@/services/api';
import { apiPost } from '@/services/api/apiClient';
import type {
  WorkforceDashboardDTO,
  StaffingAlertDTO,
  EmployeeResponse,
  ScheduleResponse,
} from '@/types';

export interface EnrichedShiftRecord {
  id: string;
  employee_id: number;
  employeeName: string;
  outlet_id: number | null;
  outletName: string;
  role: string;
  shiftDate: string;
  shift_start: string | null;
  shift_end: string | null;
  shiftHours: string;
  status: 'scheduled' | 'completed' | 'cancelled' | 'absent';
}

const EMPTY_SUMMARY: WorkforceDashboardDTO = {
  total_employees: 0,
  active_employees: 0,
  total_outlets_with_employees: 0,
  average_attendance_rate: '0.00',
  total_hours_worked: '0.00',
  top_performers: [],
  underperformers: [],
  staffing_alerts: [],
};

export function useWorkforce(pollingIntervalMs = 30000) {
  const [summary, setSummary] = useState<WorkforceDashboardDTO>(EMPTY_SUMMARY);
  const [alerts, setAlerts] = useState<StaffingAlertDTO[]>([]);
  const [shifts, setShifts] = useState<EnrichedShiftRecord[]>([]);
  const [employees, setEmployees] = useState<EmployeeResponse[]>([]);
  const [rawSchedules, setRawSchedules] = useState<ScheduleResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkforce = useCallback(async () => {
    try {
      const [sumRes, alertRes, empRes, schedRes] = await Promise.allSettled([
        workforceApi.getSummary(),
        workforceApi.getStaffingAlerts(),
        workforceApi.getEmployees(),
        workforceApi.getSchedules(),
      ]);

      setSummary(
        sumRes.status === 'fulfilled' ? sumRes.value : EMPTY_SUMMARY
      );
      setAlerts(
        alertRes.status === 'fulfilled' ? alertRes.value : []
      );

      const empList: EmployeeResponse[] =
        empRes.status === 'fulfilled' ? empRes.value : [];
      setEmployees(empList);

      const schedList: ScheduleResponse[] =
        schedRes.status === 'fulfilled' ? schedRes.value : [];
      setRawSchedules(schedList);

      // Build enriched shift records from real schedules + employees
      if (schedList.length > 0) {
        const empMap = new Map<number, EmployeeResponse>();
        empList.forEach((e) => empMap.set(e.employee_id, e));

        const enriched: EnrichedShiftRecord[] = schedList.slice(0, 100).map((s) => {
          const emp = empMap.get(s.employee_id);
          const statusRaw = (s.status || 'SCHEDULED').toUpperCase();
          const statusMapped: EnrichedShiftRecord['status'] =
            statusRaw === 'COMPLETED' ? 'completed'
            : statusRaw === 'CANCELLED' ? 'cancelled'
            : 'scheduled';

          return {
            id: `SH-${s.schedule_id}`,
            employee_id: s.employee_id,
            employeeName: emp?.full_name ?? `Employee #${s.employee_id}`,
            outlet_id: emp?.outlet_id ?? null,
            outletName: emp ? `Outlet #${emp.outlet_id}` : 'Unknown Outlet',
            role: emp?.role ?? 'Staff',
            shiftDate: s.schedule_date,
            shift_start: s.shift_start,
            shift_end: s.shift_end,
            shiftHours: s.shift_start && s.shift_end ? `${s.shift_start} - ${s.shift_end}` : '—',
            status: statusMapped,
          };
        });
        setShifts(enriched);
      } else {
        setShifts([]);
      }

      const anyFulfilled = [sumRes, alertRes, empRes, schedRes].some(
        (r) => r.status === 'fulfilled'
      );
      if (!anyFulfilled) {
        setError('Failed to fetch workforce data from backend.');
      } else {
        setError(null);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch workforce data');
    } finally {
      setLoading(false);
    }
  }, []);

  const scheduleShift = async (payload: {
    employee_id: number;
    outlet_id: number;
    shift_date: string;
    start_time: string;
    end_time: string;
    role?: string | null;
  }): Promise<boolean> => {
    try {
      await apiPost('/api/schedules', {
        employee_id: payload.employee_id,
        schedule_date: payload.shift_date,
        shift_start: payload.start_time,
        shift_end: payload.end_time,
        status: 'SCHEDULED',
      });
      await fetchWorkforce();
      return true;
    } catch (err: any) {
      setError(err?.message || 'Failed to schedule shift');
      return false;
    }
  };

  useEffect(() => {
    fetchWorkforce();
    if (pollingIntervalMs > 0) {
      const interval = setInterval(fetchWorkforce, pollingIntervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchWorkforce, pollingIntervalMs]);

  return {
    summary,
    alerts,
    shifts,
    employees,
    rawSchedules,
    loading,
    error,
    refresh: fetchWorkforce,
    scheduleShift,
  };
}
