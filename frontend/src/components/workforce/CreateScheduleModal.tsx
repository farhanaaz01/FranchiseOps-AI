import React, { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { ScheduleCreate, EmployeeResponse } from '@/types';

interface CreateScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (schedule: ScheduleCreate) => Promise<boolean>;
  employees?: EmployeeResponse[];
  outlets?: Array<{ outlet_id: number; name: string }>;
}

const DEFAULT_OUTLET_OPTIONS = [
  { outlet_id: 1, name: 'OUT-01: Downtown Flagship' },
  { outlet_id: 2, name: 'OUT-02: Westside Hub' },
  { outlet_id: 3, name: 'OUT-03: Metro Mall' },
  { outlet_id: 4, name: 'OUT-04: Uptown Express' },
  { outlet_id: 5, name: 'OUT-05: Airport Terminal' },
];

export const CreateScheduleModal: React.FC<CreateScheduleModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  employees = [],
  outlets = DEFAULT_OUTLET_OPTIONS,
}) => {
  const activeOutlets = outlets.length > 0 ? outlets : DEFAULT_OUTLET_OPTIONS;
  const [employeeId, setEmployeeId] = useState<number>(employees[0]?.employee_id || 1);
  const [outletId, setOutletId] = useState<number>(activeOutlets[0]?.outlet_id || 1);
  const [shiftDate, setShiftDate] = useState(new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState('08:00');
  const [endTime, setEndTime] = useState('16:30');
  const [role, setRole] = useState('Barista');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (employees.length > 0 && !employees.some((e) => e.employee_id === employeeId)) {
      const first = employees[0];
      setEmployeeId(first.employee_id);
      setOutletId(first.outlet_id || activeOutlets[0]?.outlet_id || 1);
      if (first.role) setRole(first.role);
    }
  }, [employees, employeeId, activeOutlets]);

  const handleEmployeeChange = (empId: number) => {
    setEmployeeId(empId);
    const emp = employees.find((e) => e.employee_id === empId);
    if (emp) {
      if (emp.outlet_id) setOutletId(emp.outlet_id);
      if (emp.role) setRole(emp.role);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const ok = await onSubmit({
        employee_id: employeeId,
        outlet_id: outletId,
        shift_date: shiftDate,
        start_time: startTime,
        end_time: endTime,
        role,
      });
      if (ok) onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Schedule Shift" size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        {employees.length > 0 && (
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Staff Member</label>
            <select
              value={employeeId}
              onChange={(e) => handleEmployeeChange(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            >
              {employees.map((emp) => (
                <option key={emp.employee_id} value={emp.employee_id}>
                  {emp.full_name} ({emp.role || 'Staff'})
                </option>
              ))}
            </select>
          </div>
        )}

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Outlet</label>
          <select
            value={outletId}
            onChange={(e) => setOutletId(Number(e.target.value))}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
          >
            {activeOutlets.map((o) => (
              <option key={o.outlet_id} value={o.outlet_id}>
                {o.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Role / Position</label>
            <input
              type="text"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Shift Date</label>
            <input
              type="date"
              value={shiftDate}
              onChange={(e) => setShiftDate(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Start Time</label>
            <input
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">End Time</label>
            <input
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-[#262B35]">
          <Button variant="ghost" size="sm" type="button" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" loading={submitting}>
            Confirm Shift
          </Button>
        </div>
      </form>
    </Modal>
  );
};
