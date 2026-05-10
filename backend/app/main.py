from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.routers import auth, clients, products, invoices, dashboard, suppliers, withholdings, export

# Import all models so Base.metadata.create_all creates all tables
from app.models import supplier, withholding  # noqa: F401

settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)

# Auto-migrate: add new columns if missing
from sqlalchemy import text, inspect as sa_inspect
_inspector = sa_inspect(engine)

def _add_column_if_missing(table: str, column: str, col_type: str = "VARCHAR"):
    cols = [c["name"] for c in _inspector.get_columns(table)]
    if column not in cols:
        with engine.begin() as conn:
            conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}'))

_add_column_if_missing("companies", "rne")
_add_column_if_missing("clients", "rne")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de facturation et gestion commerciale - SIC Facture",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(clients.router)
app.include_router(products.router)
app.include_router(invoices.router)
app.include_router(suppliers.router)
app.include_router(withholdings.router)
app.include_router(export.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
