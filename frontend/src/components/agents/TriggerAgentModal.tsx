import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { AgentInfo } from './AgentStatusGrid';

interface TriggerAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  agent: AgentInfo | null;
  onExecute: (agentId: string, taskParams: { outletId: string; instructions: string }) => void;
}

export const TriggerAgentModal: React.FC<TriggerAgentModalProps> = ({
  isOpen,
  onClose,
  agent,
  onExecute,
}) => {
  const [outletId, setOutletId] = useState('OUT-01');
  const [instructions, setInstructions] = useState('');
  const [running, setRunning] = useState(false);

  if (!agent) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setRunning(true);
    try {
      onExecute(agent.id, { outletId, instructions });
      setInstructions('');
      onClose();
    } finally {
      setRunning(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Dispatch ${agent.name}`} size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="p-3 bg-[#171A20] border border-[#262B35] rounded-lg">
          <span className="text-xs text-[#8A93A6] block">Domain Agent: {agent.domain}</span>
          <p className="text-xs text-[#EDEFF3] mt-0.5">{agent.description}</p>
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">Target Outlet</label>
          <select
            value={outletId}
            onChange={(e) => setOutletId(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] focus:outline-hidden focus:border-[#6C8CFF]"
          >
            <option value="ALL">All Franchise Outlets (Network-wide)</option>
            <option value="OUT-01">OUT-01: Downtown Flagship</option>
            <option value="OUT-02">OUT-02: Westside Hub</option>
            <option value="OUT-03">OUT-03: Metro Mall</option>
            <option value="OUT-04">OUT-04: Uptown Express</option>
            <option value="OUT-05">OUT-05: Airport Terminal</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">
            Operational Prompt / Directives (Optional)
          </label>
          <textarea
            rows={3}
            placeholder="e.g. Run 7-day safety stock scan and verify supplier lead times."
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#262B35]">
          <Button variant="ghost" size="sm" type="button" onClick={onClose} disabled={running}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" loading={running}>
            Dispatch Agent
          </Button>
        </div>
      </form>
    </Modal>
  );
};
