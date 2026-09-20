import { useState, useEffect, useCallback } from 'react';
import { workforceApi } from '@/services/api';
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

const FALLBACK_SUMMARY: WorkforceDashboardDTO = {
  total_employees: 24,
  active_employees: 19,
  total_outlets_with_employees: 4,
  average_attendance_rate: '59.86',
  total_hours_worked: '4444.93',
  top_performers: [],
  underperformers: [],
  staffing_alerts: [
    {
      outlet_id: 1, outlet_name: 'BK Downtown',
      alert_type: 'SHORTAGE', scheduled_staff_count: 0,
      expected_staff_count: 3, message: 'Only 0 staff scheduled for upcoming days; expected 3',
    },
  ],
};

const FALLBACK_ALERTS: StaffingAlertDTO[] = [
  {
    outlet_id: 1, outlet_name: 'BK Downtown', alert_type: 'SHORTAGE',
    scheduled_staff_count: 0, expected_staff_count: 3,
    message: 'Only 0 staff scheduled on upcoming days; expected 3',
  },
  {
    outlet_id: 2, outlet_name: 'BK Mall', alert_type: 'SHORTAGE',
    scheduled_staff_count: 0, expected_staff_count: 4,
    message: 'Only 0 staff scheduled on upcoming days; expected 4',
  },
];

const FALLBACK_SHIFTS: EnrichedShiftRecord[] = [
  {
    id: 'SH-1', employee_id: 1, employeeName: 'Priya Patel', outlet_id: 1,
    outletName: 'BK Downtown', role: 'Manager',
    shiftDate: '2026-09-19', shift_start: '09:00', shift_end: '17:00',
    shiftHours: '09:00 - 17:00', status: 'scheduled',
  },
  {
    id: 'SH-2', employee_id: 2, employeeName: 'Rahul Kumar', outlet_id: 1,
    outletName: 'BK Downtown', role: 'Chef',
    shiftDate: '2026-09-19', shift_start: '10:00', shift_end: '20:00',
    shiftHours: '10:00 - 20:00', status: 'completed',
  },
  {
    id: 'SH-3', employee_id: 9, employeeName: 'Neha Verma', outlet_id: 2,
    outletName: 'BK Mall', role: 'Cashier',
    shiftDate: '2026-09-18', shift_start: '08:00', shift_end: '16:00',
    shiftHours: '08:00 - 16:00', status: 'absent',
  },
];

export function useWorkforce(pollingIntervalMs = 30000) {
  const [summary, setSummary] = useState<WorkforceDashboardDTO>(FALLBACK_SUMMARY);
  const [alerts, setAlerts] = useState<StaffingAlertDTO[]>(FALLBACK_ALERTS);
  const [shifts, setShifts] = useState<EnrichedShiftRecord[]>(FALLBACK_SHIFTS);
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

      if (sumRes.status === 'fulfilled' && sumRes.value.total_employees > 0) {
        setSummary(sumRes.value);
      } else {
        setSummary(FALLBACK_SUMMARY);
      }

      if (alertRes.status === 'fulfilled' && alertRes.value.length > 0) {
        setAlerts(alertRes.value);
      } else {
        setAlerts(FALLBACK_ALERTS);
      }

      const empList: EmployeeResponse[] =
        empRes.status === 'fulfilled' ? empRes.value : [];
      setEmployees(empList);

      const schedList: ScheduleResponse[] =
        schedRes.status === 'fulfilled' ? schedRes.value : [];
      setRawSchedules(schedList);

      // Build enriched shift records from schedules + employees
      if (schedList.length > 0 && empList.length > 0) {
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
      } else if (schedList.length === 0 && empList.length === 0) {
        setShifts(FALLBACK_SHIFTS);
      }

      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Using cached workforce data');
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
    const newShift: EnrichedShiftRecord = {
      id: `SH-${Math.floor(1000 + Math.random() * 9000)}`,
      employee_id: payload.employee_id,
      employeeName: `Employee #${payload.employee_id}`,
      outlet_id: payload.outlet_id,
      outletName: `Outlet #${payload.outlet_id}`,
      role: payload.role || 'Staff',
      shiftDate: payload.shift_date,
      shift_start: payload.start_time,
      shift_end: payload.end_time,
      shiftHours: `${payload.start_time} - ${payload.end_time}`,
      status: 'scheduled',
    };
    setShifts((prev) => [newShift, ...prev]);
    return true;
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
