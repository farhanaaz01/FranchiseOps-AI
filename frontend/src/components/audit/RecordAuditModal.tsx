import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { AuditRecord } from '@/services/api/auditApi';

interface RecordAuditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (audit: Omit<AuditRecord, 'id'>) => Promise<AuditRecord>;
}

export const RecordAuditModal: React.FC<RecordAuditModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [outletId, setOutletId] = useState('OUT-01');
  const [outletName, setOutletName] = useState('Downtown Flagship');
  const [inspectionDate, setInspectionDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [auditorName, setAuditorName] = useState('Senior Auditor');
  const [score, setScore] = useState('92.0');
  const [criticalViolations, setCriticalViolations] = useState(0);
  const [minorViolations, setMinorViolations] = useState(1);
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleOutletChange = (val: string) => {
    setOutletId(val);
    const names: Record<string, string> = {
      'OUT-01': 'Downtown Flagship',
      'OUT-02': 'Westside Hub',
      'OUT-03': 'Metro Mall',
      'OUT-04': 'Uptown Express',
      'OUT-05': 'Airport Terminal',
    };
    setOutletName(names[val] || val);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const scoreNum = parseFloat(score) || 75;
    const status: 'Passed' | 'Warning' | 'Failed' =
      scoreNum >= 80 ? 'Passed' : scoreNum >= 65 ? 'Warning' : 'Failed';

    try {
      await onSubmit({
        outletId,
        outletName,
        inspectionDate,
        auditorName,
        score: scoreNum,
        status,
        criticalViolations: Number(criticalViolations),
        minorViolations: Number(minorViolations),
        notes: notes.trim() || 'Standards verified and documented.',
      });
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Log Food Safety & Health Audit" size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Inspected Outlet</label>
          <select
            value={outletId}
            onChange={(e) => handleOutletChange(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
          >
            <option value="OUT-01">OUT-01: Downtown Flagship</option>
            <option value="OUT-02">OUT-02: Westside Hub</option>
            <option value="OUT-03">OUT-03: Metro Mall</option>
            <option value="OUT-04">OUT-04: Uptown Express</option>
            <option value="OUT-05">OUT-05: Airport Terminal</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Inspection Date</label>
            <input
              type="date"
              value={inspectionDate}
              onChange={(e) => setInspectionDate(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Lead Inspector</label>
            <input
              type="text"
              value={auditorName}
              onChange={(e) => setAuditorName(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Compliance Score (0-100)</label>
            <input
              type="number"
              step="0.5"
              min="0"
              max="100"
              value={score}
              onChange={(e) => setScore(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Critical Violations</label>
            <input
              type="number"
              min="0"
              value={criticalViolations}
              onChange={(e) => setCriticalViolations(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Minor Violations</label>
            <input
              type="number"
              min="0"
              value={minorViolations}
              onChange={(e) => setMinorViolations(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Findings & Corrective Notes</label>
          <textarea
            rows={3}
            placeholder="e.g. Temperature sensors calibrated; grease trap clean."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#262B35]">
          <Button variant="ghost" size="sm" type="button" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" loading={submitting}>
            Save Audit Record
          </Button>
        </div>
      </form>
    </Modal>
  );
};
