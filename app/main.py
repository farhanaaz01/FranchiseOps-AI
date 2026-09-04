from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import dashboard, franchise, outlet, sale
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_data()
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
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "Welcome to FranchiseOps AI Backend"}
