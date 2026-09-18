# FranchiseOps AI — Milestone 2 Presentation Script
## Inventory Intelligence & Optimization

---

## 1. Opening (30 seconds)

"In Milestone 2, we built the **Inventory Agent** — the second specialized AI agent in the FranchiseOps AI platform. While Milestone 1 focused on outlet performance, this milestone focuses on **inventory optimization across all franchise locations**."

"The goal is to reduce stockouts, prevent overstocking, minimize wastage, and automatically recommend when and how much to reorder."

---

## 2. Problem We Are Solving (1 minute)

"Franchises face major inventory problems every day:"

- **Stockouts** — popular items run out, leading to lost sales
- **Overstocking** — too much inventory ties up cash and storage space
- **Wastage** — fresh items expire before they are used
- **No visibility** — managers can't see inventory health across outlets
- **Manual reordering** — staff guess reorder quantities instead of using data

"This milestone solves these problems by giving real-time inventory monitoring, demand forecasting, and automated replenishment suggestions."

---

## 3. Backend Architecture (2 minutes)

"The backend is built with **Python, FastAPI, SQLAlchemy, and MySQL**. We added the Inventory Agent on top of the existing Milestone 1 backend."

### New Database Tables

| Table | Purpose |
|---|---|
| `products` | Master catalog of items like Burger Patties, Fries, Soda |
| `inventory` | Current stock level per outlet per product |
| `inventory_transactions` | Tracks every stock movement: IN, OUT, WASTAGE, RETURN |
| `purchase_orders` | Optional table for planned replenishment orders |

### Relationships

- One **Outlet** has many **Inventory** records
- One **Product** appears in many **Inventory** records
- One **Inventory** record has many **Transactions**

### Core Backend Services

| Service | Responsibility |
|---|---|
| `product_service.py` | CRUD for products |
| `inventory_service.py` | CRUD for stock levels |
| `inventory_transaction_service.py` | Records stock movements and auto-updates current stock |
| `inventory_analytics_service.py` | The Inventory Agent — forecasts, alerts, recommendations |

---

## 4. Backend Logic Explained (2–3 minutes)

### Demand Forecasting

"We use a **30-day moving average** to predict daily demand per product per outlet."

Formula:
```
forecasted_daily_demand = total_OUT_quantity_last_30_days / 30
```

"This is simple, fast, and effective enough for a franchise dashboard. Later milestones can upgrade to machine learning models."

### Stock Status Monitoring

"Each inventory item gets a status based on current stock vs thresholds:"

| Status | Condition |
|---|---|
| **Critical** | current_stock == 0 |
| **Low Stock** | current_stock <= reorder_point |
| **Overstock** | current_stock >= max_stock |
| **Normal** | everything else |

"Thresholds are set per product per outlet based on average daily usage."

### Wastage Tracking

"Wastage transactions record expired, damaged, or discarded items. The dashboard shows total wastage over the last 30 days so managers can identify problem areas."

### Replenishment Recommendation

"The system recommends reorder quantity using:"

```
safety_stock        = forecasted_daily_demand × 2 days
lead_time_demand    = forecasted_daily_demand × 3 days
target_stock        = lead_time_demand + safety_stock
recommended_order   = target_stock − current_stock
```

"This ensures outlets never run out while avoiding over-ordering."

---

## 5. API Endpoints — Backend to Frontend Bridge (2–3 minutes)

"The frontend consumes these REST endpoints:"

### CRUD Endpoints

```text
GET    /api/products                     → list all products
POST   /api/products                     → add a new product
GET    /api/inventory                    → list all inventory records
GET    /api/inventory/outlet/{id}        → inventory for one outlet
POST   /api/inventory-transactions        → record a stock movement
```

### Dashboard / Analytics Endpoints

```text
GET /api/inventory/dashboard/summary
GET /api/inventory/dashboard/status
GET /api/inventory/dashboard/alerts
GET /api/inventory/dashboard/replenishment
GET /api/inventory/dashboard/forecast/{outlet_id}/{product_id}
```

### Example: Summary Dashboard Response

```json
{
  "total_products": 8,
  "total_inventory_items": 32,
  "total_stock_value": 29337.00,
  "low_stock_count": 5,
  "critical_stock_count": 5,
  "overstock_count": 6,
  "total_wastage_30_days": 88.96,
  "top_alerts": [...],
  "replenishment_recommendations": [...]
}
```

### Example: Replenishment Recommendation

```json
{
  "outlet_id": 1,
  "outlet_name": "BK Downtown",
  "product_id": 1,
  "product_name": "Burger Patties",
  "current_stock": 0.00,
  "forecasted_daily_demand": 17.02,
  "days_until_stockout": 0,
  "recommended_order_quantity": 85.10,
  "recommended_order_date": "2026-09-07",
  "reason": "Stock is at or below reorder point. Reorder to cover lead time + safety stock."
}
```

---

## 6. Frontend Ideas / Dashboard Screens (2 minutes)

"The frontend can be built with React, Vue, or any framework. Here are the key screens it should display:"

### Screen 1 — Inventory Executive Dashboard

Cards showing:
- Total products
- Total inventory value
- Low stock count
- Critical stock count
- Overstock count
- Wastage in last 30 days

Plus charts:
- Stock status pie chart (Critical / Low / Normal / Overstock)
- Top 10 alerts list
- Inventory value by outlet

### Screen 2 — Outlet Inventory View

- Table of all products in a selected outlet
- Columns: product name, current stock, reorder point, status
- Color-coded status badges
- Search and filter by category or status

### Screen 3 — Alerts & Notifications

- Real-time alert list
- Group by outlet
- One-click action to create purchase order or transfer stock

### Screen 4 — Replenishment Planner

- Table of recommended reorders
- Columns: outlet, product, current stock, forecasted demand, recommended quantity
- "Approve Order" button that creates a purchase order

### Screen 5 — Demand Forecast Chart

- Line chart showing historical usage vs forecasted daily demand
- Per product, per outlet

### Screen 6 — Wastage Report

- Bar chart of wastage by product
- Filter by outlet and date range
- Highlight products with highest wastage

---

## 7. How Frontend Connects to Backend (1 minute)

"The frontend makes simple HTTP calls using fetch or axios:"

```javascript
// React example: load inventory summary
const response = await fetch('http://localhost:8000/api/inventory/dashboard/summary');
const data = await response.json();

// Show critical stock count
document.title = `Critical Items: ${data.critical_stock_count}`;
```

```javascript
// React example: load alerts
const alerts = await fetch('http://localhost:8000/api/inventory/dashboard/alerts')
  .then(r => r.json());

// Render alert cards
alerts.map(alert => (
  <AlertCard
    key={`${alert.outlet_id}-${alert.product_id}`}
    type={alert.alert_type}
    outlet={alert.outlet_name}
    product={alert.product_name}
    stock={alert.current_stock}
    message={alert.message}
  />
));
```

"CORS is already enabled in `app/main.py` for `http://localhost:5173`, so a Vite frontend will work without issues."

---

## 8. Demo Flow You Can Show (2 minutes)

1. Start the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Open Swagger UI at `http://localhost:8000/docs`

3. Call `/api/inventory/dashboard/summary` and show:
   - total products
   - critical / low / overstock counts
   - total stock value

4. Call `/api/inventory/dashboard/alerts` and show alert cards

5. Call `/api/inventory/dashboard/replenishment` and show recommended order quantities

6. Call `/api/inventory/dashboard/forecast/1/1` and explain the 30-day moving average

7. Mention that the frontend can render these exact JSON responses as charts, tables, and badges.

---

## 9. Tech Stack Recap (30 seconds)

- **Backend:** Python, FastAPI, SQLAlchemy, MySQL
- **API Docs:** Swagger UI at `/docs`
- **Frontend:** React / Vue / any framework that can call REST APIs
- **Communication:** JSON over HTTP with CORS enabled

---

## 10. Closing (30 seconds)

"Milestone 2 delivers a complete Inventory Intelligence backend with demand forecasting, stock alerts, wastage tracking, and automatic replenishment recommendations. The frontend can now build dashboards that give franchise managers real-time visibility and actionable insights to optimize inventory across every outlet."

"Next, Milestone 3 will add the Staff Agent and Marketing Agent for workforce and campaign analytics."
