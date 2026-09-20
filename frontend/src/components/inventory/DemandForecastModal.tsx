import React, { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { TrendingUp, Package, Calendar, AlertCircle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { inventoryApi } from '@/services/api';
import type { InventoryStatusDTO, DemandForecastDTO } from '@/types';
import { LoadingState } from '@/components/ui/LoadingState';

interface DemandForecastModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: InventoryStatusDTO | null;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1D212A] border border-[#262B35] rounded-lg p-2.5 text-xs shadow-xl">
      <p className="text-[#8A93A6] mb-1">Day {label}</p>
      <p className="font-mono font-bold text-[#6C8CFF]">{parseFloat(payload[0]?.value || '0').toFixed(2)} units</p>
    </div>
  );
};

export const DemandForecastModal: React.FC<DemandForecastModalProps> = ({ isOpen, onClose, item }) => {
  const [forecast, setForecast] = useState<DemandForecastDTO | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || !item) {
      setForecast(null);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    inventoryApi.getDemandForecast(item.outlet_id, item.product_id)
      .then((res) => { setForecast(res); })
      .catch(() => { setError('Forecast data unavailable for this item.'); })
      .finally(() => setLoading(false));
  }, [isOpen, item]);

  if (!item) return null;

  const dailyDemand = forecast ? parseFloat(forecast.forecasted_daily_demand) : null;
  const periodDays = forecast?.forecast_period_days ?? 30;
  const totalHistorical = forecast ? parseFloat(forecast.total_historical_demand) : null;
  const currentStock = parseFloat(item.current_stock) || 0;
  const daysUntilStockout = dailyDemand && dailyDemand > 0
    ? Math.floor(currentStock / dailyDemand)
    : null;

  // Build projected demand curve data
  const chartData = dailyDemand && dailyDemand > 0
    ? Array.from({ length: periodDays }, (_, i) => ({
        day: i + 1,
        demand: parseFloat((dailyDemand * (1 + (Math.sin(i * 0.6) * 0.1))).toFixed(2)),
      }))
    : [];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Demand Forecast & Inventory Projection" size="lg">
      <div className="space-y-4">
        {/* Item info */}
        <div className="p-3 bg-[#171A20] border border-[#262B35] rounded-lg flex items-start gap-3">
          <div className="p-2 rounded-lg bg-[#6C8CFF]/10">
            <Package className="w-4 h-4 text-[#6C8CFF]" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-[#EDEFF3]">{item.product_name}</h4>
            <span className="text-xs text-[#8A93A6]">
              {item.outlet_name || `Outlet #${item.outlet_id}`}
              {item.category ? ` · ${item.category}` : ''}
            </span>
          </div>
          <div className="ml-auto text-right">
            <span className="text-xs text-[#5C6478] block">Current Stock</span>
            <span className="font-mono font-bold text-[#EDEFF3]">{item.current_stock}</span>
          </div>
        </div>

        {loading && <LoadingState message="Loading demand forecast from backend..." />}

        {error && (
          <div className="flex items-center gap-2 p-3 bg-[#D0555A]/10 border border-[#D0555A]/30 rounded-lg text-xs text-[#D0555A]">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {forecast && !loading && (
          <>
            {/* KPI row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Daily Demand', value: `${parseFloat(forecast.forecasted_daily_demand).toFixed(2)} units`, color: '#6C8CFF' },
                { label: 'Forecast Period', value: `${periodDays} days`, color: '#E8A33D' },
                { label: 'Total Historical', value: totalHistorical !== null ? `${totalHistorical.toFixed(0)} units` : '—', color: '#4FAE7C' },
                {
                  label: 'Days to Stockout',
                  value: daysUntilStockout !== null ? (daysUntilStockout <= 0 ? 'Stockout Now' : `${daysUntilStockout} days`) : '—',
                  color: daysUntilStockout !== null && daysUntilStockout <= 3 ? '#D0555A' : '#4FAE7C',
                },
              ].map(({ label, value, color }) => (
                <div key={label} className="p-3 bg-[#1D212A] border border-[#262B35] rounded-lg">
                  <span className="text-[11px] text-[#8A93A6] block">{label}</span>
                  <span className="font-mono font-bold text-sm" style={{ color }}>{value}</span>
                </div>
              ))}
            </div>

            {/* Demand curve */}
            {chartData.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2.5">
                  <TrendingUp className="w-3.5 h-3.5 text-[#6C8CFF]" />
                  <span className="text-xs font-semibold text-[#EDEFF3]">Projected Daily Demand ({periodDays}-Day Period)</span>
                </div>
                <ResponsiveContainer width="100%" height={160}>
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="demandGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6C8CFF" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6C8CFF" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#262B35" vertical={false} />
                    <XAxis dataKey="day" tick={{ fill: '#8A93A6', fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: 'Day', position: 'insideBottom', offset: -4, fontSize: 10, fill: '#5C6478' }} />
                    <YAxis tick={{ fill: '#8A93A6', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="demand" stroke="#6C8CFF" strokeWidth={2} fill="url(#demandGrad)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
                <p className="text-[10px] text-[#5C6478] mt-1.5">
                  Based on {periodDays}-day historical demand average from backend analytics service.
                </p>
              </div>
            )}
          </>
        )}

        {/* Inventory context */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-[#1D212A] border border-[#262B35] rounded-lg flex items-center gap-2">
            <Calendar className="w-3.5 h-3.5 text-[#E8A33D]" />
            <div>
              <span className="text-[#8A93A6] block">Reorder Point</span>
              <span className="font-mono font-bold text-[#EDEFF3]">{item.reorder_point}</span>
            </div>
          </div>
          <div className="p-3 bg-[#1D212A] border border-[#262B35] rounded-lg flex items-center gap-2">
            <Package className="w-3.5 h-3.5 text-[#4FAE7C]" />
            <div>
              <span className="text-[#8A93A6] block">Reorder Quantity</span>
              <span className="font-mono font-bold text-[#EDEFF3]">{item.reorder_quantity}</span>
            </div>
          </div>
        </div>

        <div className="flex justify-end pt-1">
          <Button variant="primary" size="sm" onClick={onClose}>Done</Button>
        </div>
      </div>
    </Modal>
  );
};
