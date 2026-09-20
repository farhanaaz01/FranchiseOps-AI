import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { MarketingCampaignCreate } from '@/types';

interface CreateCampaignModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (campaign: MarketingCampaignCreate) => Promise<boolean>;
}

export const CreateCampaignModal: React.FC<CreateCampaignModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [outletId, setOutletId] = useState(1);
  const [campaignName, setCampaignName] = useState('');
  const [channel, setChannel] = useState('Local Social Media Ads');
  const [budget, setBudget] = useState('1500');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(
    new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!campaignName.trim()) return;

    setSubmitting(true);
    try {
      const ok = await onSubmit({
        outlet_id: outletId,
        campaign_name: campaignName.trim(),
        channel,
        budget: parseFloat(budget) || 1000,
        start_date: startDate,
        end_date: endDate,
      });
      if (ok) {
        setCampaignName('');
        onClose();
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Launch New Marketing Campaign" size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">
            Target Outlet
          </label>
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

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">
            Campaign Name <span className="text-[#D0555A]">*</span>
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Autumn Pumpkin Spice Rollout"
            value={campaignName}
            onChange={(e) => setCampaignName(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Channel / Type</label>
            <input
              type="text"
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Budget ($ USD)</label>
            <input
              type="number"
              step="50"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
            />
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-[#262B35]">
          <Button variant="ghost" size="sm" type="button" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" loading={submitting}>
            Launch Campaign
          </Button>
        </div>
      </form>
    </Modal>
  );
};
