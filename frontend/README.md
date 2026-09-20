# FranchiseOps AI — Frontend Architecture (Phase 1)

> **Franchise Intelligence Platform**  
> Enterprise multi-unit operational dashboard, telemetry visualization, and autonomous agent orchestration.

---

## 1. Overview

This frontend application is built specifically for **FranchiseOps AI**. It serves corporate HQ, franchise regional directors, and unit store managers with real-time operational diagnostics, composite KPI health scoring, machine learning revenue forecasts, and autonomous agent workflows.

---

## 2. Technology Stack

- **Framework:** [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Bundler / Dev Server:** [Vite 6](https://vitejs.dev/)
- **Styling:** [Tailwind CSS 3.4](https://tailwindcss.com/) + PostCSS + Autoprefixer
- **Design Tokens:** Enterprise Dark Palette (`#0E1013` base, `#171A20` panel, `#1D212A` panel-alt, `#262B35` borders, `#6C8CFF` accent)
- **Routing:** [React Router v6](https://reactrouter.com/)
- **Data Visualization:** [Recharts](https://recharts.org/)
- **Iconography:** [Lucide React](https://lucide.dev/)
- **HTTP Client:** Type-safe fetch API client with abort controllers, timeout handling, and typed error responses

---

## 3. Directory Structure

```
frontend/
├── index.html                     # HTML5 entry with Inter, Space Grotesk, IBM Plex Mono fonts
├── package.json                   # Dependencies and npm scripts
├── tsconfig.json                  # TypeScript compiler settings (strict mode, @/* alias)
├── tsconfig.node.json             # Vite config TS settings
├── vite.config.ts                 # Vite setup with @/ path alias & /api reverse proxy
├── tailwind.config.js             # Enterprise color palette and typography tokens
├── postcss.config.js              # PostCSS plugins
├── .env.example                   # Environment configuration variables
└── src/
    ├── main.tsx                   # React root mount
    ├── App.tsx                    # Application routing (12 distinct routes)
    ├── index.css                  # Global CSS, Tailwind directives, theme variables
    ├── types/
    │   ├── backend.ts             # 35+ TypeScript interfaces matching app/schemas.py
    │   ├── pipeline.ts            # Pydantic schema types matching data_engine/schemas.py
    │   └── index.ts               # Common UI, navigation, status, and alert types
    ├── services/
    │   └── api/
    │       ├── apiClient.ts       # Typed fetch wrapper with GET/POST/PUT/DELETE
    │       ├── endpoints.ts       # 40+ verified FastAPI endpoints
    │       └── realtimeAdapter.ts # Safe fallback adapter (backend has no WebSockets)
    ├── utils/
    │   ├── cn.ts                  # clsx + tailwind-merge helper
    │   └── formatters.ts          # Currency, percentage, dates, health score formatters
    ├── components/
    │   ├── ui/                    # Base UI components (Button, Card, Badge, Modal, etc.)
    │   ├── kpi/                   # Metric cards (KPICard)
    │   ├── layout/                # Sidebar, TopNav, AppLayout
    │   ├── charts/                # Recharts visualizations (RevenueTrendChart)
    │   ├── outlets/               # Outlets module components (Phase 2)
    │   ├── inventory/             # Inventory module components (Phase 2)
    │   ├── workforce/             # Workforce module components (Phase 2)
    │   ├── marketing/             # Marketing module components (Phase 2)
    │   ├── audit/                 # Audit module components (Phase 2)
    │   ├── alerts/                # Alerts module components (Phase 2)
    │   ├── agents/                # Agents module components (Phase 2)
    │   └── ai/                    # AI Copilot components (Phase 2)
    └── pages/
        ├── Overview.tsx           # Enterprise executive dashboard
        ├── Outlets.tsx            # Multi-unit outlet directory & matrix
        ├── OutletDetails.tsx      # Deep-dive outlet telemetry & ML forecast
        ├── Inventory.tsx          # Stockout risk & inventory management
        ├── Workforce.tsx          # Staffing roster & absenteeism optimization
        ├── Marketing.tsx          # Campaign ROI & promo attribution
        ├── Audit.tsx              # HACCP food safety & brand compliance
        ├── AIInsights.tsx         # Operational Copilot & XGBoost drivers
        ├── Alerts.tsx             # Threshold breach incident management
        ├── AgentActivity.tsx      # Autonomous agent execution log
        ├── Reports.tsx            # Executive briefs & automated downloads
        └── Settings.tsx           # Composite KPI weights & system config
```

---

## 4. Setup & Running Locally

### Prerequisites
- **Node.js:** v18+ (tested on Node v24)
- **npm:** v9+

### Commands

On Windows (using `cmd.exe` if PowerShell ExecutionPolicy blocks npm):

```cmd
cd frontend
npm install
npm run dev
```

The application will start at `http://localhost:5173`.

### Production Build

```cmd
cd frontend
npm run build
npm run preview
```

### TypeScript Validation

```cmd
cd frontend
npx tsc --noEmit
```

---

## 5. Backend Gateway & Integration

- The Vite development server is configured with a reverse proxy forwarding `/api/*` to `http://localhost:8000/*`.
- Backend CORS in `app/config.py` is pre-configured to accept requests from `http://localhost:5173`.
- All endpoint paths are defined in `src/services/api/endpoints.ts` and directly correspond to the verified FastAPI backend routers.
- The pipeline schema in `src/types/pipeline.ts` mirrors the 5-outlet output produced by `data_engine/pipeline.py`.

---

## 6. Phase 1 Scope & Protection Guarantee

- **Status:** Phase 1 Complete (Foundation, Layout, Design System, Type Safety, Routing, and Module Pages).
- **Backend Integrity:** **Zero** existing backend files, ML models, CSV datasets, database configs, or HTML templates were modified or removed.
- **Phase 2 Ready:** Production API binding, real-time polling hooks, interactive form submissions, and full autonomous agent execution flows can now be layered onto this stable foundation.
