# FranchiseOps AI — Milestones 1–3 Live Demo Checklist (Backend + DB)

**Repo:** https://github.com/farhanaaz01/FranchiseOps-AI  
**Branch:** `main` (pulled locally — includes M1–M3 `app/` + team `frontend/` + `data_engine/`)

---

## Before you start

| Step | Command / note |
|------|----------------|
| MySQL | Create database `franchiseops` |
| Env | Copy `.env.example` → `.env`, set `DB_PASSWORD` |
| Install | `pip install -r requirements.txt` |
| Run API | `uvicorn app.main:app --reload` → **http://localhost:8000** |
| Swagger | **http://localhost:8000/docs** |
| Seed | First startup runs `seed_data()` — franchises, outlets, sales, inventory, employees, campaigns |

**Optional frontend (teammate):** `cd frontend && npm install && npm run dev` → http://localhost:5173

---

## Database tables by milestone

| M | Tables |
|---|--------|
| **M1** | `franchises`, `outlets`, `sales` |
| **M2** | `products`, `inventory`, `inventory_transactions`, `purchase_orders` |
| **M3** | `employees`, `attendance`, `schedules`, `marketing_campaigns`, `campaign_performance` |

---

## Milestone 1 — Outlet Performance Agent (demo in ~3 min)

**Eval:** monitoring, benchmarking, performance dashboard.

| # | Method | Endpoint | What to say |
|---|--------|----------|-------------|
| 1 | GET | `/api/dashboard/summary` | Executive outlet KPIs: revenue, health scores, top/low outlets |
| 2 | GET | `/api/dashboard/franchises/1/compare` | Rank outlets in franchise 1 |
| 3 | GET | `/api/dashboard/outlets/1` | One outlet + revenue trend (optional `?start_date=&end_date=`) |
| 4 | GET | `/api/dashboard/underperforming` | Outlets below franchise average |
| 5 | GET | `/api/franchises` | Data foundation |
| 6 | GET | `/api/outlets` | Multi-location support |

**curl (PowerShell):**
```powershell
curl http://localhost:8000/api/dashboard/summary
curl http://localhost:8000/api/dashboard/franchises/1/compare
curl http://localhost:8000/api/dashboard/outlets/1
```

---

## Milestone 2 — Inventory Agent (demo in ~3 min)

**Eval:** forecasting, stock monitoring, replenishment.

| # | Method | Endpoint | What to say |
|---|--------|----------|-------------|
| 1 | GET | `/api/inventory/dashboard/summary` | Stock value, critical/low/overstock counts, wastage |
| 2 | GET | `/api/inventory/dashboard/alerts` | Critical / low / overstock alerts |
| 3 | GET | `/api/inventory/dashboard/replenishment` | Recommended order quantities |
| 4 | GET | `/api/inventory/dashboard/forecast/1/1` | 30-day moving average demand (outlet 1, product 1) |
| 5 | GET | `/api/inventory/outlet/1` | Stock levels for one outlet |
| 6 | GET | `/api/products` | Product catalog |

**curl:**
```powershell
curl http://localhost:8000/api/inventory/dashboard/summary
curl http://localhost:8000/api/inventory/dashboard/alerts
curl http://localhost:8000/api/inventory/dashboard/replenishment
```

---

## Milestone 3 — Staff + Marketing Agents (demo in ~4 min)

**Eval:** workforce analytics, marketing tracking, operational insights.

### Staff Agent

| # | Method | Endpoint | What to say |
|---|--------|----------|-------------|
| 1 | GET | `/api/workforce/dashboard/summary` | Headcount, attendance rate, top/under performers |
| 2 | GET | `/api/workforce/dashboard/alerts` | Staffing shortages (next 7 days) |
| 3 | GET | `/api/workforce/dashboard/employees/1` | Productivity score + attendance breakdown |
| 4 | GET | `/api/workforce/dashboard/outlets/1` | All staff performance at outlet 1 |
| 5 | GET | `/api/employees/outlet/1` | CRUD data layer |

### Marketing Agent

| # | Method | Endpoint | What to say |
|---|--------|----------|-------------|
| 6 | GET | `/api/marketing/dashboard/summary` | Budget, revenue, overall ROI |
| 7 | GET | `/api/marketing/dashboard/campaigns` | Compare all campaigns |
| 8 | GET | `/api/marketing/dashboard/campaigns/1` | ROI, engagement, conversion for one campaign |
| 9 | GET | `/api/marketing-campaigns/outlet/1` | Campaigns tied to outlet |

**curl:**
```powershell
curl http://localhost:8000/api/workforce/dashboard/summary
curl http://localhost:8000/api/workforce/dashboard/alerts
curl http://localhost:8000/api/marketing/dashboard/summary
curl http://localhost:8000/api/marketing/dashboard/campaigns
```

---

## 5-minute “exam demo” order (minimum)

1. `GET /api/dashboard/summary` — **M1**  
2. `GET /api/inventory/dashboard/summary` — **M2**  
3. `GET /api/workforce/dashboard/summary` — **M3 Staff**  
4. `GET /api/marketing/dashboard/summary` — **M3 Marketing**  
5. Show **Swagger `/docs`** — all routers registered  

---

## Quick verification (no MySQL)

```powershell
$env:DATABASE_URL="sqlite:///./demo_check.db"
uvicorn app.main:app --port 8000
# Then hit summary endpoints above; delete demo_check.db after
```

---

## Git milestone map

| Milestone | Branch (historical) | On `main`? |
|-----------|---------------------|------------|
| M1 | `milestone-1-backend` | Yes |
| M2 | `milestone-2-inventory` | Yes (PR #1) |
| M3 | `milestone-3-workforce-marketing` | Yes (merge `391457e`) |

---

## Milestone 4 — Audit, Intelligence, Executive, Notifications

| # | Method | Path | Purpose |
|---|--------|------|---------|
| 1 | GET | `/api/intelligence/latest` | Latest `PipelineOutput` (KPIs, scores, forecasts, root causes) |
| 2 | POST | `/api/intelligence/run` | Re-run pipeline from DB (+ sync notifications) |
| 3 | GET | `/api/intelligence/root-causes` | Root-cause findings (`?outlet_id=OUT-01`) |
| 4 | GET | `/api/intelligence/forecasts` | 7-day revenue forecasts |
| 5 | GET | `/api/executive/summary` | Unified executive dashboard (all agents) |
| 6 | GET | `/api/audit/dashboard/summary` | Audit KPIs (inspections + compliance) |
| 7 | GET | `/api/audit/dashboard/compliance` | Per-outlet compliance + pipeline health |
| 8 | GET/POST | `/api/audits/inspections` | Manual inspection CRUD |
| 9 | GET/POST | `/api/audits/compliance` | Compliance snapshot records |
| 10 | GET | `/api/notifications` | Persisted unified alerts |
| 11 | POST | `/api/notifications/sync` | Refresh alerts from all agents |
| 12 | PATCH | `/api/notifications/{id}` | Acknowledge / resolve (`{"status":"acknowledged"}`) |
| 13 | GET/POST | `/api/notifications/action-plans` | Workflow action plans |

**Note:** On startup the API runs the intelligence pipeline once and syncs notifications. Existing MySQL DBs get new tables via `create_all`; re-seed or POST compliance rows if audit tables are empty.

---

## Your talking line (30 sec)

“We implemented four domain agents as FastAPI services on MySQL: outlet performance, inventory, workforce, and marketing. Each milestone adds SQLAlchemy models, seed data, CRUD APIs, and dashboard endpoints consumed by our React frontend on port 5173.”
