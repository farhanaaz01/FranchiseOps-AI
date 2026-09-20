import React, { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import type { InventoryStatusDTO, InventoryTransactionCreate } from '@/types';

interface CreateTransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: InventoryStatusDTO | null;
  onSubmit: (tx: InventoryTransactionCreate) => Promise<boolean>;
}

export const CreateTransactionModal: React.FC<CreateTransactionModalProps> = ({
  isOpen,
  onClose,
  item,
  onSubmit,
}) => {
  const [txType, setTxType] = useState<'IN' | 'OUT' | 'WASTAGE' | 'RETURN'>('IN');
  const [quantity, setQuantity] = useState('');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!item) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const qtyNum = parseFloat(quantity);
    if (!qtyNum || qtyNum <= 0) {
      setError('Please enter a valid positive quantity');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const ok = await onSubmit({
        inventory_id: item.inventory_id,
        transaction_type: txType,
        quantity: qtyNum,
        reason: reason.trim() || null,
      });
      if (ok) {
        setQuantity('');
        setReason('');
        onClose();
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to record transaction');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Record Inventory Transaction" size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-[#D0555A]/10 border border-[#D0555A]/30 rounded-lg text-xs text-[#D0555A]">
            {error}
          </div>
        )}

        <div className="p-3 bg-[#171A20] border border-[#262B35] rounded-lg">
          <span className="text-[10px] font-mono text-[#6C8CFF] uppercase tracking-wider block">
            {item.outlet_name || `Outlet #${item.outlet_id}`}
          </span>
          <h4 className="text-sm font-semibold text-[#EDEFF3]">{item.product_name}</h4>
          <span className="text-xs text-[#8A93A6]">Current Stock: {item.current_stock}</span>
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">
            Transaction Type
          </label>
          <div className="grid grid-cols-4 gap-2">
            {(['IN', 'OUT', 'WASTAGE', 'RETURN'] as const).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => setTxType(type)}
                className={`py-2 text-xs font-mono font-medium rounded-lg border transition-colors ${
                  txType === type
                    ? 'bg-[#6C8CFF] text-[#FFFFFF] border-[#6C8CFF]'
                    : 'bg-[#171A20] text-[#8A93A6] border-[#262B35] hover:border-[#6C8CFF]/50'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">
            Quantity <span className="text-[#D0555A]">*</span>
          </label>
          <input
            type="number"
            step="0.01"
            required
            placeholder="e.g. 15.0"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-[#8A93A6] mb-1.5">
            Audit Reason / Reference
          </label>
          <input
            type="text"
            placeholder="e.g. Weekly supplier delivery, Expired dairy, Customer return"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full px-3 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
          />
        </div>

        <div className="flex items-center justify-end gap-2 pt-4 border-t border-[#262B35]">
          <Button variant="ghost" size="sm" type="button" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" loading={submitting}>
            Log Transaction
          </Button>
        </div>
      </form>
    </Modal>
  );
};
