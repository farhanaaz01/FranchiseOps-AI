# FranchiseOps AI — Milestone 1 Presentation Script

## 1. Project Introduction (1–2 minutes)

"FranchiseOps AI is an Agentic AI-powered Franchise Operations Intelligence Platform. The goal is to help large restaurant and retail franchises manage multiple outlets more efficiently by monitoring performance, inventory, staff, marketing, and compliance through specialized AI agents."

"For Milestone 1, I focused on the **Outlet Performance Intelligence** module — the first agent of the platform. This agent tracks sales performance, compares outlets, and generates health scores so franchise owners can quickly spot problems."

---

## 2. Problem Statement (1 minute)

"Franchise owners currently rely on fragmented reports and manual checks. This leads to:
- Delayed decisions
- Inconsistent customer experience across outlets
- Inventory and revenue losses
- No clear way to compare which outlets are performing well"

"Our platform solves this by giving real-time, data-driven insights through intelligent agents."

---

## 3. What I Built in Milestone 1 (2–3 minutes)

"I worked on the backend and database part. Specifically, I built:"

### Backend (Python + FastAPI)
- **Outlet Performance Agent Service** — calculates revenue, transactions, averages, and health scores
- **Pydantic Schemas** — structured request/response models for dashboards
- **SQLAlchemy Repository Queries** — aggregates sales by outlet and date range
- **Dashboard Router** — REST endpoints for the frontend team
- **Seed Data Script** — automatically inserts sample franchises, outlets, and 30 days of sales on first run

### Database (MySQL)
- `franchises` table
- `outlets` table
- `sales` table
- Relationships: One franchise has many outlets, one outlet has many sales records

---

## 4. Key Features Implemented (2–3 minutes)

"The Milestone 1 backend supports:"

1. **Single Outlet Performance Report**
   - Total revenue, total transactions
   - Average revenue per day and per transaction
   - Health score (0–100)
   - Performance label: Excellent / Good / Average / Underperforming / Critical
   - Daily revenue trend chart data

2. **Franchise Outlet Comparison**
   - Rank outlets within a franchise by revenue
   - Compare all outlets side by side
   - Health scores per outlet

3. **Executive Dashboard Summary**
   - Total outlets and active outlets
   - Total revenue and total transactions
   - Average health score across all outlets
   - Top performing outlet and lowest performing outlet
   - List of recent underperforming outlets

4. **Underperforming Outlet Detection**
   - Automatically flags outlets whose revenue is below 70% of their franchise average
   - Shows reason and comparison with franchise average

---

## 5. API Endpoints Demo (2–3 minutes)

"Here are the main endpoints the frontend can consume:"

```
GET http://localhost:8000/api/dashboard/summary
GET http://localhost:8000/api/dashboard/outlets/{outlet_id}
GET http://localhost:8000/api/dashboard/franchises/{franchise_id}/compare
GET http://localhost:8000/api/dashboard/underperforming
```

"Optional query parameters: `start_date` and `end_date` in `YYYY-MM-DD` format."

"For example, you can call:"
```
GET http://localhost:8000/api/dashboard/outlets/1?start_date=2026-08-01&end_date=2026-08-31
```

"This returns a JSON response with the outlet's performance, health score, and daily revenue trend."

"You can also explore the interactive API docs at:"
```
http://localhost:8000/docs
```

---

## 6. How the Health Score Works (1–2 minutes)

"The health score is calculated by comparing an outlet's revenue to the average revenue of all outlets in the same franchise. A score of 100 means the outlet is at or above the franchise average. Scores below 70 are flagged as underperforming."

"If an outlet status is 'Inactive', its score is reduced by 50% to reflect lower operational activity."

---

## 7. Tech Stack (30 seconds)

- Python 3.9+
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- MySQL
- Uvicorn
- Git & GitHub

---

## 8. How to Run the Project (1–2 minutes)

"To run it locally:"

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Start MySQL and create a database named `franchiseops`
3. Copy `.env.example` to `.env` and set your MySQL password
4. Run: `uvicorn app.main:app --reload`
5. The app starts on port 8000
6. On first run, sample data is automatically inserted

"Then you can test the endpoints using a browser, Postman, curl, or the built-in Swagger UI at `/docs`."

---

## 9. GitHub Repository (30 seconds)

"All the work is committed and merged into the main branch on GitHub:"

https://github.com/farhanaaz01/FranchiseOps-AI

"Branch: `main` (Milestone 1 Python backend is there)"

---

## 10. Next Steps / Future Milestones (1 minute)

"Milestone 1 is complete. The next milestones will add:"
- Milestone 2: Inventory Agent (demand forecasting, stock monitoring, replenishment)
- Milestone 3: Staff Agent and Marketing Agent
- Milestone 4: Audit Agent, Franchise Intelligence Engine, and production deployment

"Each agent will follow the same pattern: collect data, analyze, score, and expose dashboard endpoints."

---

## 11. Closing Statement (30 seconds)

"In summary, Milestone 1 delivers a working Python backend for outlet performance monitoring with real-time analytics, benchmarking, health scores, and dashboard-ready APIs. The foundation is ready for the frontend team to build the executive dashboard."

---

## Optional: Demo Commands

```bash
# Start the application
uvicorn app.main:app --reload

# Test dashboard summary
curl http://localhost:8000/api/dashboard/summary

# Test single outlet performance
curl http://localhost:8000/api/dashboard/outlets/1

# Test franchise comparison
curl http://localhost:8000/api/dashboard/franchises/1/compare

# Test underperforming outlets
curl http://localhost:8000/api/dashboard/underperforming
```
