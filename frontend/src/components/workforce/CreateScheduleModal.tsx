import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { ScheduleCreate } from '@/types';

interface CreateScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (schedule: ScheduleCreate) => Promise<boolean>;
}

export const CreateScheduleModal: React.FC<CreateScheduleModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [employeeId, setEmployeeId] = useState(1);
  const [outletId, setOutletId] = useState(1);
  const [shiftDate, setShiftDate] = useState(new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState('08:00');
  const [endTime, setEndTime] = useState('16:30');
  const [role, setRole] = useState('Barista');
  const [submitting, setSubmitting] = useState(false);

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
        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Outlet</label>
          <select
            value={outletId}
            onChange={(e) => setOutletId(Number(e.target.value))}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
          >
            <option value={1}>OUT-01: Downtown Flagship</option>
            <option value={2}>OUT-02: Westside Hub</option>
            <option value={3}>OUT-03: Metro Mall</option>
            <option value={4}>OUT-04: Uptown Express</option>
            <option value={5}>OUT-05: Airport Terminal</option>
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
