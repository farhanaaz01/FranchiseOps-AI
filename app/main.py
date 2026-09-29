from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
import app.models  # noqa: F401 — register Milestone 4 tables on metadata
from app.database import SessionLocal
from app.routers import (
    attendance,
    audit,
    audit_dashboard,
    campaign_performance,
    dashboard,
    employee,
    executive_dashboard,
    franchise,
    intelligence,
    inventory,
    inventory_dashboard,
    inventory_transaction,
    marketing_campaign,
    marketing_dashboard,
    notifications,
    outlet,
    product,
    sale,
    schedule,
    workforce_dashboard,
)
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_data()
    db = SessionLocal()
    try:
        from app.services import intelligence_service, notification_service

        intelligence_service.run_pipeline(db)
        notification_service.sync_alerts_from_agents(db)
    except Exception:
        pass
    finally:
        db.close()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="Agentic AI-powered Franchise Operations Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(franchise.router)
app.include_router(outlet.router)
app.include_router(sale.router)
app.include_router(product.router)
app.include_router(inventory.router)
app.include_router(inventory_transaction.router)
app.include_router(employee.router)
app.include_router(attendance.router)
app.include_router(schedule.router)
app.include_router(marketing_campaign.router)
app.include_router(campaign_performance.router)
app.include_router(dashboard.router)
app.include_router(inventory_dashboard.router)
app.include_router(workforce_dashboard.router)
app.include_router(marketing_dashboard.router)
app.include_router(audit.router)
app.include_router(audit_dashboard.router)
app.include_router(intelligence.router)
app.include_router(executive_dashboard.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {"message": "Welcome to FranchiseOps AI Backend"}
