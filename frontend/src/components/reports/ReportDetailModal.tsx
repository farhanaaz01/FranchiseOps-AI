import React, { useState, useMemo } from 'react';
import {
  X,
  Download,
  Printer,
  Calendar,
  Layers,
  Sparkles,
  Database,
  Filter,
  Search,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { exportToCsv } from '@/utils/csvExport';
import { cn } from '@/utils/cn';

export interface ReportDefinition {
  id: string;
  title: string;
  category: 'Operations' | 'Finance' | 'Risk & Compliance';
  description: string;
  lastGenerated: string;
  freshness: 'Live Telemetry' | 'Cached Pipeline';
  rowCount: number;
  filename: string;
  kpis: { label: string; value: string; subtext?: string }[];
  chartData: Array<Record<string, any>>;
  chartConfig?: {
    dataKeyX: string;
    bars: { dataKey: string; name: string; color: string }[];
  };
  headers: string[];
  rows: (string | number | boolean | null | undefined)[][];
}

interface ReportDetailModalProps {
  report: ReportDefinition | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ReportDetailModal: React.FC<ReportDetailModalProps> = ({
  report,
  isOpen,
  onClose,
}) => {
  const [filterQuery, setFilterQuery] = useState('');
  const [selectedOutlet, setSelectedOutlet] = useState<string>('ALL');

  if (!isOpen || !report) return null;

  const handleExportCsv = () => {
    exportToCsv(report.filename, report.headers, report.rows);
  };

  const handlePrint = () => {
    window.print();
  };

  // Find if there is an outlet column to filter by
  const outletColIndex = report.headers.findIndex(
    (h) => h.toLowerCase().includes('outlet') || h.toLowerCase() === 'id'
  );

  const filteredRows = useMemo(() => {
    let result = report.rows;

    if (selectedOutlet !== 'ALL' && outletColIndex !== -1) {
      result = result.filter((row) => {
        const val = String(row[outletColIndex] || '');
        return val.toUpperCase().includes(selectedOutlet.toUpperCase());
      });
    }

    if (filterQuery.trim()) {
      const q = filterQuery.toLowerCase();
      result = result.filter((row) =>
        row.some((cell) => String(cell).toLowerCase().includes(q))
      );
    }

    return result;
  }, [report.rows, filterQuery, selectedOutlet, outletColIndex]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs select-none">
      <div className="w-full max-w-5xl bg-[#12141A] border border-[#262B35] rounded-xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden animate-in fade-in zoom-in-95 duration-150 print:bg-white print:text-black print:border-none print:shadow-none print:max-h-none print:h-auto">
        {/* Header */}
        <div className="p-5 border-b border-[#262B35] bg-[#171A20] flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span
                className={cn(
                  'text-[10px] font-mono uppercase px-2 py-0.5 rounded font-semibold',
                  report.category === 'Operations' && 'bg-[#6C8CFF]/10 text-[#6C8CFF] border border-[#6C8CFF]/30',
                  report.category === 'Finance' && 'bg-[#F2A73B]/10 text-[#F2A73B] border border-[#F2A73B]/30',
                  report.category === 'Risk & Compliance' && 'bg-[#3AA99F]/10 text-[#3AA99F] border border-[#3AA99F]/30'
                )}
              >
                {report.category}
              </span>
              <span className="text-[10px] font-mono text-[#4FAE7C] bg-[#4FAE7C]/10 px-2 py-0.5 rounded border border-[#4FAE7C]/30 flex items-center gap-1">
                <Database className="w-2.5 h-2.5" />
                {report.freshness}
              </span>
              <span className="text-[10px] font-mono text-[#5C6478]">
                {report.rowCount} records compiled
              </span>
            </div>

            <h2 className="text-base font-bold text-[#EDEFF3] font-display print:text-black">
              {report.title}
            </h2>
            <p className="text-xs text-[#8A93A6] mt-0.5 print:text-gray-600">
              {report.description}
            </p>
          </div>

          <div className="flex items-center gap-2 print:hidden">
            <Button
              variant="outline"
              size="sm"
              icon={<Printer className="w-3.5 h-3.5" />}
              onClick={handlePrint}
              title="Print formatted report or save as PDF"
            >
              Print / PDF
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={<Download className="w-3.5 h-3.5" />}
              onClick={handleExportCsv}
              title="Download full CSV file in browser"
            >
              Export CSV
            </Button>
            <button
              onClick={onClose}
              className="p-1.5 text-[#8A93A6] hover:text-[#EDEFF3] hover:bg-[#1D212A] rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Scrollable Report Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Summary KPIs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {report.kpis.map((kpi, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-[#171A20] border border-[#262B35] print:border-gray-200 space-y-1"
              >
                <div className="text-[10px] font-mono uppercase text-[#5C6478] font-semibold">
                  {kpi.label}
                </div>
                <div className="text-lg font-bold text-[#EDEFF3] font-mono print:text-black">
                  {kpi.value}
                </div>
                {kpi.subtext && (
                  <div className="text-[10px] text-[#8A93A6]">{kpi.subtext}</div>
                )}
              </div>
            ))}
          </div>

          {/* Visual Chart if provided */}
          {report.chartData && report.chartData.length > 0 && report.chartConfig && (
            <div className="p-4 rounded-xl bg-[#171A20] border border-[#262B35] space-y-3 print:border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-[#EDEFF3] font-display">
                  Visual Distribution & Trends
                </span>
                <span className="text-[10px] font-mono text-[#5C6478]">
                  Operational Analysis
                </span>
              </div>
              <div className="h-56 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={report.chartData}
                    margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#262B35" />
                    <XAxis
                      dataKey={report.chartConfig.dataKeyX}
                      tick={{ fill: '#5C6478', fontSize: 10 }}
                      axisLine={{ stroke: '#262B35' }}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: '#5C6478', fontSize: 10 }}
                      axisLine={{ stroke: '#262B35' }}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#171A20',
                        borderColor: '#262B35',
                        borderRadius: '8px',
                        fontSize: '11px',
                        color: '#EDEFF3',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', color: '#8A93A6' }} />
                    {report.chartConfig.bars.map((bar) => (
                      <Bar
                        key={bar.dataKey}
                        dataKey={bar.dataKey}
                        name={bar.name}
                        fill={bar.color}
                        radius={[4, 4, 0, 0]}
                      />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Table Controls (Search & Outlet filter) */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2 print:hidden">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#5C6478]" />
              <input
                type="text"
                value={filterQuery}
                onChange={(e) => setFilterQuery(e.target.value)}
                placeholder="Filter table rows..."
                className="w-full pl-8 pr-3 py-1.5 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-none focus:border-[#6C8CFF]"
              />
            </div>

            {outletColIndex !== -1 && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#5C6478]">Store:</span>
                <select
                  value={selectedOutlet}
                  onChange={(e) => setSelectedOutlet(e.target.value)}
                  className="bg-[#171A20] border border-[#262B35] text-xs text-[#EDEFF3] rounded-lg px-2.5 py-1.5 focus:outline-none"
                >
                  <option value="ALL">All Outlets</option>
                  <option value="OUT-01">OUT-01 (Downtown)</option>
                  <option value="OUT-02">OUT-02 (Westside)</option>
                  <option value="OUT-03">OUT-03 (Metro Mall)</option>
                  <option value="OUT-04">OUT-04 (Uptown)</option>
                  <option value="OUT-05">OUT-05 (Airport)</option>
                </select>
              </div>
            )}
          </div>

          {/* Tabular Data View */}
          <div className="rounded-xl border border-[#262B35] overflow-hidden bg-[#171A20] print:border-gray-300">
            <div className="overflow-x-auto max-h-72">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-[#12141A] border-b border-[#262B35] text-[10px] font-mono text-[#5C6478] uppercase sticky top-0">
                    {report.headers.map((h, i) => (
                      <th key={i} className="px-3.5 py-2.5 font-semibold">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#262B35]/40 text-[#EDEFF3]">
                  {filteredRows.length === 0 ? (
                    <tr>
                      <td
                        colSpan={report.headers.length}
                        className="px-4 py-8 text-center text-xs text-[#5C6478]"
                      >
                        No records match the active filter criteria.
                      </td>
                    </tr>
                  ) : (
                    filteredRows.map((row, rowIdx) => (
                      <tr
                        key={rowIdx}
                        className="hover:bg-[#1D212A]/60 transition-colors"
                      >
                        {row.map((cell, colIdx) => (
                          <td
                            key={colIdx}
                            className="px-3.5 py-2.5 text-[11px] font-mono whitespace-nowrap"
                          >
                            {cell === null || cell === undefined ? '—' : String(cell)}
                          </td>
                        ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <div className="px-4 py-2 bg-[#12141A] border-t border-[#262B35] flex items-center justify-between text-[10px] font-mono text-[#5C6478]">
              <span>
                Showing {filteredRows.length} of {report.rows.length} records
              </span>
              <span>Generated client-side from active telemetry</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-[#171A20] border-t border-[#262B35] flex items-center justify-between print:hidden">
          <div className="text-[11px] text-[#5C6478]">
            Compliance & audit reference: <span className="font-mono">{report.filename}</span>
          </div>
          <Button variant="outline" size="sm" onClick={onClose}>
            Close Report
          </Button>
        </div>
      </div>
    </div>
  );
};
