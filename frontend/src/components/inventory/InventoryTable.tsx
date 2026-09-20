import React, { useState, useMemo } from 'react';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ArrowRightLeft, TrendingUp, ChevronUp, ChevronDown } from 'lucide-react';
import type { InventoryStatusDTO } from '@/types';

type SortKey = 'product_name' | 'outlet_name' | 'current_stock' | 'reorder_point' | 'status';
type SortDir = 'asc' | 'desc';

const STATUS_ORDER: Record<string, number> = { Critical: 0, 'Low Stock': 1, Normal: 2, Overstock: 3 };

const STATUS_BADGE_VARIANT: Record<string, string> = {
  Critical: 'danger',
  'Low Stock': 'warning',
  Normal: 'success',
  Overstock: 'accent',
};

interface InventoryTableProps {
  items: InventoryStatusDTO[];
  onOpenTransaction: (item: InventoryStatusDTO) => void;
  onOpenForecast: (item: InventoryStatusDTO) => void;
}

export const InventoryTable: React.FC<InventoryTableProps> = ({
  items,
  onOpenTransaction,
  onOpenForecast,
}) => {
  const [sortKey, setSortKey] = useState<SortKey>('status');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [categoryFilter, setCategoryFilter] = useState<string>('All');

  const categories = useMemo(() => {
    const set = new Set(items.map((i) => i.category || 'General'));
    return ['All', ...Array.from(set).sort()];
  }, [items]);

  const filtered = useMemo(() => {
    let result = [...items];
    if (statusFilter !== 'All') result = result.filter((i) => i.status === statusFilter);
    if (categoryFilter !== 'All') result = result.filter((i) => (i.category || 'General') === categoryFilter);
    result.sort((a, b) => {
      let cmp = 0;
      if (sortKey === 'current_stock') {
        cmp = parseFloat(a.current_stock) - parseFloat(b.current_stock);
      } else if (sortKey === 'reorder_point') {
        cmp = parseFloat(a.reorder_point) - parseFloat(b.reorder_point);
      } else if (sortKey === 'status') {
        cmp = (STATUS_ORDER[a.status] ?? 9) - (STATUS_ORDER[b.status] ?? 9);
      } else {
        const av = (a[sortKey] as string) || '';
        const bv = (b[sortKey] as string) || '';
        cmp = av.localeCompare(bv);
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return result;
  }, [items, sortKey, sortDir, statusFilter, categoryFilter]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else { setSortKey(key); setSortDir('asc'); }
  };

  const SortIcon = ({ col }: { col: SortKey }) =>
    sortKey === col
      ? sortDir === 'asc' ? <ChevronUp className="w-3 h-3 inline ml-0.5" /> : <ChevronDown className="w-3 h-3 inline ml-0.5" />
      : null;

  return (
    <div>
      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-2 px-5 py-3 border-b border-[#262B35]">
        <span className="text-xs text-[#5C6478]">Status:</span>
        {['All', 'Critical', 'Low Stock', 'Normal', 'Overstock'].map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
              statusFilter === s
                ? 'bg-[#6C8CFF] text-white'
                : 'bg-[#1D212A] text-[#8A93A6] border border-[#262B35] hover:border-[#6C8CFF]/50'
            }`}
          >
            {s}
          </button>
        ))}
        <span className="text-xs text-[#5C6478] ml-3">Category:</span>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="bg-[#1D212A] border border-[#262B35] text-[#8A93A6] text-[11px] rounded px-2 py-1 focus:outline-none focus:border-[#6C8CFF]/50"
        >
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <span className="text-xs text-[#5C6478] ml-auto">{filtered.length} items</span>
      </div>

      {filtered.length === 0 ? (
        <div className="py-12 text-center text-sm text-[#5C6478]">No inventory items match the current filters.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#1D212A] text-[#8A93A6] font-mono border-b border-[#262B35]">
              <tr>
                <th className="px-5 py-3 cursor-pointer hover:text-[#EDEFF3]" onClick={() => handleSort('product_name')}>
                  Product <SortIcon col="product_name" />
                </th>
                <th className="px-5 py-3 cursor-pointer hover:text-[#EDEFF3]" onClick={() => handleSort('outlet_name')}>
                  Outlet <SortIcon col="outlet_name" />
                </th>
                <th className="px-5 py-3">Category</th>
                <th className="px-5 py-3 cursor-pointer hover:text-[#EDEFF3]" onClick={() => handleSort('current_stock')}>
                  Current Stock <SortIcon col="current_stock" />
                </th>
                <th className="px-5 py-3 cursor-pointer hover:text-[#EDEFF3]" onClick={() => handleSort('reorder_point')}>
                  Reorder Point <SortIcon col="reorder_point" />
                </th>
                <th className="px-5 py-3">Reorder Qty</th>
                <th className="px-5 py-3 cursor-pointer hover:text-[#EDEFF3]" onClick={() => handleSort('status')}>
                  Status <SortIcon col="status" />
                </th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#262B35]">
              {filtered.map((item) => {
                const current = parseFloat(item.current_stock) || 0;
                const reorder = parseFloat(item.reorder_point) || 0;
                const max = parseFloat(item.max_stock || '100') || 100;
                const pct = Math.min(100, Math.round((current / Math.max(max, 1)) * 100));
                const variant = STATUS_BADGE_VARIANT[item.status] || 'default';

                return (
                  <tr key={`${item.outlet_id}-${item.product_id}`} className="hover:bg-[#1D212A]/50 transition-colors">
                    <td className="px-5 py-3.5">
                      <span className="font-semibold text-[#EDEFF3] block">{item.product_name}</span>
                      <span className="text-[10px] font-mono text-[#5C6478]">SKU-#{item.product_id}</span>
                    </td>
                    <td className="px-5 py-3.5 text-[#EDEFF3]">{item.outlet_name || `Outlet #${item.outlet_id}`}</td>
                    <td className="px-5 py-3.5">
                      <span className="bg-[#1D212A] border border-[#262B35] text-[#8A93A6] px-2 py-0.5 rounded text-[11px]">
                        {item.category || 'General'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <span className={`font-mono font-bold w-14 ${current <= reorder ? 'text-[#D0555A]' : 'text-[#EDEFF3]'}`}>
                          {item.current_stock}
                        </span>
                        <div className="w-16 bg-[#171A20] h-1.5 rounded-full overflow-hidden border border-[#262B35]">
                          <div
                            className={`h-full rounded-full ${
                              current <= reorder * 0.5 ? 'bg-[#D0555A]' : current <= reorder ? 'bg-[#E8A33D]' : 'bg-[#4FAE7C]'
                            }`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[#8A93A6]">{item.reorder_point}</td>
                    <td className="px-5 py-3.5 font-mono text-[#8A93A6]">{item.reorder_quantity}</td>
                    <td className="px-5 py-3.5">
                      <Badge variant={variant as any} size="sm">{item.status}</Badge>
                    </td>
                    <td className="px-5 py-3.5 text-right space-x-1">
                      <Button
                        variant="ghost" size="sm"
                        onClick={() => onOpenForecast(item)}
                        icon={<TrendingUp className="w-3 h-3 text-[#6C8CFF]" />}
                      >Forecast</Button>
                      <Button
                        variant="outline" size="sm"
                        onClick={() => onOpenTransaction(item)}
                        icon={<ArrowRightLeft className="w-3 h-3" />}
                      >Adjust</Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
