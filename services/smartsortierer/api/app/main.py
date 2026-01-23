"""
SmartSortierer Pro - FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import check_db_connection
from app.core.security import APIKeyMiddleware
from app.api import files, docs

app = FastAPI(
    title="SmartSortierer Pro API",
    description="Intelligente Dokumentenverwaltung mit KI",
    version="0.3.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware - Restrict origins in production
cors_origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:3000",
    "http://127.0.0.1",
]
if hasattr(settings, 'CORS_ORIGINS') and settings.CORS_ORIGINS:
    cors_origins.extend(settings.CORS_ORIGINS.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if settings.ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# API Key Security Middleware
app.add_middleware(APIKeyMiddleware)

# Include routers
app.include_router(files.router)
app.include_router(docs.router)

@app.get("/api/health")
async def health_check():
    """Health check endpoint with database connectivity check"""
    db_ok = check_db_connection()
    
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "api",
        "version": "0.4.0",
        "phase": "4 - Document Ingest Pipeline",
        "checks": {
            "database": "ok" if db_ok else "failed",
            "storage_root": settings.STORAGE_ROOT,
            "environment": settings.ENVIRONMENT
        }
    }

@app.get("/api/")
async def root():
    """API root"""
    return {
        "message": "SmartSortierer Pro API",
        "docs": "/api/docs",
        "health": "/api/health"
    }
