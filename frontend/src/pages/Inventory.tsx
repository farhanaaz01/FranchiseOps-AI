import React, { useState } from 'react';
import { PageHeader } from '@/components/ui/PageHeader';
import { KPICard } from '@/components/kpi/KPICard';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  Package, AlertTriangle, TrendingDown, ShoppingCart,
  Search, RefreshCw, ArrowRightLeft, DollarSign,
} from 'lucide-react';
import { useInventory } from '@/hooks/useInventory';
import {
  InventoryTable,
  ReplenishmentCard,
  StockAlertsList,
  DemandForecastModal,
  CreateTransactionModal,
} from '@/components/inventory';
import { StockStatusDistributionChart, StockVsReorderChart } from '@/components/inventory/InventoryCharts';
import { formatCurrency } from '@/utils/formatters';
import type { InventoryStatusDTO } from '@/types';

export const Inventory: React.FC = () => {
  const {
    dashboardSummary,
    statusList,
    alerts,
    recommendations,
    approvedRecs,
    loading,
    refresh,
    approveRecommendation,
    recordTransaction,
  } = useInventory();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedForecastItem, setSelectedForecastItem] = useState<InventoryStatusDTO | null>(null);
  const [selectedTxItem, setSelectedTxItem] = useState<InventoryStatusDTO | null>(null);

  const filteredItems = statusList.filter((item) =>
    (item.product_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    String(item.product_id).includes(searchTerm) ||
    (item.outlet_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.category || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const criticalCount = dashboardSummary.critical_stock_count;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Inventory & Stock Control"
        subtitle="Predictive stockout analysis, perishable batch monitoring, and automated supplier reorders."
        badge={
          <Badge variant={criticalCount > 0 ? 'danger' : 'success'}>
            {criticalCount} Critical Stockouts
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={<RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />}
              onClick={refresh}
            >
              Sync ERP
            </Button>
            {statusList.length > 0 && (
              <Button
                variant="primary"
                size="sm"
                icon={<ArrowRightLeft className="w-3.5 h-3.5" />}
                onClick={() => setSelectedTxItem(statusList[0])}
              >
                Log Stock Movement
              </Button>
            )}
          </div>
        }
      />

      {/* KPI Cards Row — real backend data */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Inventory Value"
          value={formatCurrency(dashboardSummary.total_stock_value, true)}
          subtext={`${dashboardSummary.total_inventory_items} SKUs across ${dashboardSummary.total_products} products`}
          icon={<DollarSign className="w-4 h-4 text-[#6C8CFF]" />}
        />
        <KPICard
          title="Critical Stock Items"
          value={String(dashboardSummary.critical_stock_count)}
          subtext={`${dashboardSummary.low_stock_count} below reorder point`}
          status="critical"
          icon={<AlertTriangle className="w-4 h-4 text-[#D0555A]" />}
        />
        <KPICard
          title="Replenishment Signals"
          value={String(recommendations.length)}
          subtext={`${approvedRecs.length} Approved · ${dashboardSummary.overstock_count} overstocked`}
          status="healthy"
          icon={<ShoppingCart className="w-4 h-4 text-[#4FAE7C]" />}
        />
        <KPICard
          title="30-Day Wastage"
          value={formatCurrency(dashboardSummary.total_wastage_30_days, true)}
          subtext="Spoilage & expired stock"
          status="risk"
          icon={<TrendingDown className="w-4 h-4 text-[#E8A33D]" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <StockStatusDistributionChart summary={dashboardSummary} />
        <StockVsReorderChart items={statusList} />
      </div>

      {/* Replenishment + Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ReplenishmentCard
          recommendations={recommendations}
          approvedKeys={approvedRecs}
          onApprove={approveRecommendation}
        />
        <StockAlertsList alerts={alerts} />
      </div>

      {/* Full SKU Inventory Table */}
      <Card>
        <CardHeader separator>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-3">
            <div>
              <CardTitle>SKU Inventory Matrix</CardTitle>
              <span className="text-xs text-[#5C6478]">Live stock levels — sort and filter by status or category</span>
            </div>
            <div className="relative max-w-xs w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#5C6478]" />
              <input
                type="text"
                placeholder="Search SKUs, names, outlets, category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF]"
              />
            </div>
          </div>
        </CardHeader>
        <InventoryTable
          items={filteredItems}
          onOpenForecast={(item) => setSelectedForecastItem(item)}
          onOpenTransaction={(item) => setSelectedTxItem(item)}
        />
      </Card>

      {/* Demand Forecast Modal */}
      <DemandForecastModal
        isOpen={Boolean(selectedForecastItem)}
        onClose={() => setSelectedForecastItem(null)}
        item={selectedForecastItem}
      />

      {/* Record Transaction Modal */}
      <CreateTransactionModal
        isOpen={Boolean(selectedTxItem)}
        onClose={() => setSelectedTxItem(null)}
        item={selectedTxItem}
        onSubmit={recordTransaction}
      />
    </div>
  );
};
