# FranchiseOps AI Backend

Agentic AI-powered Franchise Operations Intelligence Platform — Python FastAPI backend.

## Tech Stack

- Python 3.9+
- FastAPI
- SQLAlchemy 2.0
- MySQL
- Pydantic
- Uvicorn

## Project Structure

```text
app/
├── config.py                 # App settings
├── database.py               # SQLAlchemy engine and sessions
├── models.py                 # Database models
├── schemas.py                # Pydantic request/response schemas
├── seed.py                   # Sample data loader
├── main.py                   # FastAPI entry point
├── routers/                  # API route handlers
│   ├── franchise.py
│   ├── outlet.py
│   ├── sale.py
│   └── dashboard.py
└── services/                 # Business logic
    ├── franchise_service.py
    ├── outlet_service.py
    ├── sale_service.py
    └── performance_service.py
```

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a MySQL database named `franchiseops`.

4. Copy `.env.example` to `.env` and fill in your MySQL password:

```bash
copy .env.example .env
```

5. Run the application:

```bash
uvicorn app.main:app --reload
```

The server will start on `http://localhost:8000`.

## API Documentation

Once running, interactive docs are available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Main Endpoints

### CRUD Endpoints

- `GET /api/franchises`
- `POST /api/franchises`
- `GET /api/franchises/{franchise_id}`
- `PUT /api/franchises/{franchise_id}`
- `DELETE /api/franchises/{franchise_id}`

- `GET /api/outlets`
- `POST /api/outlets`
- `GET /api/outlets/{outlet_id}`
- `GET /api/outlets/franchise/{franchise_id}`
- `PUT /api/outlets/{outlet_id}`
- `DELETE /api/outlets/{outlet_id}`

- `GET /api/sales`
- `POST /api/sales`
- `GET /api/sales/{sale_id}`
- `GET /api/sales/outlet/{outlet_id}`
- `PUT /api/sales/{sale_id}`
- `DELETE /api/sales/{sale_id}`

### Dashboard / Analytics Endpoints (Milestone 1)

- `GET /api/dashboard/summary`
- `GET /api/dashboard/outlets/{outlet_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/dashboard/franchises/{franchise_id}/compare?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/dashboard/underperforming?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

## Sample Data

On first run, the app automatically creates:

- 2 franchises
- 4 outlets (Active and Inactive)
- 30 days of sales data per outlet

## Milestones

- **Milestone 1 (complete):** Outlet Performance Intelligence — revenue trends, benchmarking, health scores, underperforming outlet detection.
- **Milestone 2:** Inventory Intelligence
- **Milestone 3:** Workforce & Marketing Intelligence
- **Milestone 4:** Audit Intelligence & Enterprise Deployment
