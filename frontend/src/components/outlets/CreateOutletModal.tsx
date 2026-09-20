import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { OutletCreate } from '@/types';

interface CreateOutletModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (outlet: OutletCreate) => Promise<boolean>;
}

export const CreateOutletModal: React.FC<CreateOutletModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [outletName, setOutletName] = useState('');
  const [location, setLocation] = useState('');
  const [franchiseId, setFranchiseId] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!outletName.trim()) {
      setError('Outlet name is required');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const ok = await onSubmit({
        franchise_id: franchiseId,
        outlet_name: outletName.trim(),
        location: location.trim() || null,
        status: 'Active',
      });
      if (ok) {
        setOutletName('');
        setLocation('');
        onClose();
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to create outlet');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add New Franchise Outlet" size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-[#D0555A]/10 border border-[#D0555A]/30 rounded-lg text-xs text-[#D0555A]">
            {error}
          </div>
        )}

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">
            Outlet Name <span className="text-[#D0555A]">*</span>
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Midtown Crossing"
            value={outletName}
            onChange={(e) => setOutletName(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Location / Address</label>
          <input
            type="text"
            placeholder="e.g. 450 Lexington Ave, New York, NY"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Franchise Territory</label>
          <select
            value={franchiseId}
            onChange={(e) => setFranchiseId(Number(e.target.value))}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
          >
            <option value={1}>Franchise Group #1 (Metro NY Region)</option>
            <option value={2}>Franchise Group #2 (Tri-State Hubs)</option>
          </select>
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-[#262B35]">
          <Button variant="ghost" size="sm" type="button" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" loading={submitting}>
            Create Outlet
          </Button>
        </div>
      </form>
    </Modal>
  );
};
