import { apiGet } from './apiClient';
import type {
  WorkforceDashboardDTO,
  OutletWorkforceDTO,
  EmployeePerformanceDTO,
  StaffingAlertDTO,
  EmployeeResponse,
  ScheduleResponse,
  AttendanceResponse,
} from '@/types';

function buildQuery(startDate?: string | null, endDate?: string | null): string {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const q = params.toString();
  return q ? `?${q}` : '';
}

export const workforceApi = {
  /**
   * Fetch workforce dashboard summary (attendance, overtime, shortages)
   */
  getSummary: (): Promise<WorkforceDashboardDTO> => {
    return apiGet<WorkforceDashboardDTO>('/api/workforce/dashboard/summary');
  },

  /**
   * Fetch workforce analytics for a specific outlet
   */
  getOutletWorkforce: (
    outletId: number | string,
    startDate?: string | null,
    endDate?: string | null
  ): Promise<OutletWorkforceDTO> => {
    return apiGet<OutletWorkforceDTO>(
      `/api/workforce/dashboard/outlets/${outletId}${buildQuery(startDate, endDate)}`
    );
  },

  /**
   * Fetch performance analytics for a single employee
   */
  getEmployeePerformance: (
    employeeId: number | string,
    startDate?: string | null,
    endDate?: string | null
  ): Promise<EmployeePerformanceDTO> => {
    return apiGet<EmployeePerformanceDTO>(
      `/api/workforce/dashboard/employees/${employeeId}${buildQuery(startDate, endDate)}`
    );
  },

  /**
   * Fetch staffing shortage and overtime alerts
   */
  getStaffingAlerts: (): Promise<StaffingAlertDTO[]> => {
    return apiGet<StaffingAlertDTO[]>('/api/workforce/dashboard/alerts');
  },

  /**
   * Fetch all schedules (shift records) via /api/schedules
   */
  getSchedules: (): Promise<ScheduleResponse[]> => {
    return apiGet<ScheduleResponse[]>('/api/schedules');
  },

  /**
   * Fetch attendance records for an employee via /api/attendance/employee/{id}
   */
  getAttendanceByEmployee: (employeeId: number | string): Promise<AttendanceResponse[]> => {
    return apiGet<AttendanceResponse[]>(`/api/attendance/employee/${employeeId}`);
  },

  /**
   * Fetch all employees via /api/employees
   */
  getEmployees: (): Promise<EmployeeResponse[]> => {
    return apiGet<EmployeeResponse[]>('/api/employees');
  },

  /**
   * Fetch employees for a specific outlet via /api/employees/outlet/{id}
   */
  getEmployeesByOutlet: (outletId: number | string): Promise<EmployeeResponse[]> => {
    return apiGet<EmployeeResponse[]>(`/api/employees/outlet/${outletId}`);
  },
};
