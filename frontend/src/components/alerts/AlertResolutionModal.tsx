import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { UnifiedAlert } from '@/services/api/alertsApi';

interface AlertResolutionModalProps {
  isOpen: boolean;
  onClose: () => void;
  alert: UnifiedAlert | null;
  onResolve: (id: string, note?: string) => void;
}

export const AlertResolutionModal: React.FC<AlertResolutionModalProps> = ({
  isOpen,
  onClose,
  alert,
  onResolve,
}) => {
  const [resolutionNote, setResolutionNote] = useState('');
  const [resolving, setResolving] = useState(false);

  if (!alert) return null;

  const handleResolve = () => {
    setResolving(true);
    try {
      onResolve(alert.id, resolutionNote);
      setResolutionNote('');
      onClose();
    } finally {
      setResolving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Resolve Operational Incident" size="md">
      <div className="space-y-4">
        <div className="p-3.5 bg-[#171A20] border border-[#262B35] rounded-lg space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-[#6C8CFF] uppercase tracking-wider">
              {alert.domain} • {alert.outletName || alert.outletId}
            </span>
            <span className="text-[10px] font-mono uppercase font-bold text-[#D0555A]">
              {alert.severity}
            </span>
          </div>
          <h4 className="text-sm font-semibold text-[#EDEFF3]">{alert.title}</h4>
          <p className="text-xs text-[#8A93A6]">{alert.description}</p>
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">
            Corrective Action Taken & Notes
          </label>
          <textarea
            rows={3}
            placeholder="e.g. Dispatched emergency dairy restock order; verified walk-in temperature calibration."
            value={resolutionNote}
            onChange={(e) => setResolutionNote(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#262B35]">
          <Button variant="ghost" size="sm" onClick={onClose} disabled={resolving}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" onClick={handleResolve} loading={resolving}>
            Mark Incident Resolved
          </Button>
        </div>
      </div>
    </Modal>
  );
};
