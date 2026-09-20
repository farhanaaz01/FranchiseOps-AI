import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';

// Page components
import { Overview } from '@/pages/Overview';
import { Outlets } from '@/pages/Outlets';
import { OutletDetails } from '@/pages/OutletDetails';
import { Inventory } from '@/pages/Inventory';
import { Workforce } from '@/pages/Workforce';
import { Marketing } from '@/pages/Marketing';
import { Audit } from '@/pages/Audit';
import { AIInsights } from '@/pages/AIInsights';
import { DecisionCenter } from '@/pages/DecisionCenter';
import { Alerts } from '@/pages/Alerts';
import { AgentActivity } from '@/pages/AgentActivity';
import { Reports } from '@/pages/Reports';
import { Settings } from '@/pages/Settings';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
          {/* Main Dashboard */}
          <Route index element={<Overview />} />

          {/* Operations Module */}
          <Route path="outlets" element={<Outlets />} />
          <Route path="outlets/:outletId" element={<OutletDetails />} />
          <Route path="inventory" element={<Inventory />} />
          <Route path="workforce" element={<Workforce />} />
          <Route path="marketing" element={<Marketing />} />
          <Route path="audit" element={<Audit />} />

          {/* Intelligence & Automation Module */}
          <Route path="ai-insights" element={<AIInsights />} />
          <Route path="decision-center" element={<DecisionCenter />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="agent-activity" element={<AgentActivity />} />

          {/* Reporting & Settings */}
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </ErrorBoundary>
  );
};

export default App;
