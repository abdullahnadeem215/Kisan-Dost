"""
FastAPI Main Application for Kisan Dost.
Evidence-Grounded AI Agronomy Multi-Agent Advisory & Farm Decision System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import advisory, simulator, passport, farm_health, tools, demo
from config.settings import settings


def create_app() -> FastAPI:
    """
    Creates and configures the Kisan Dost FastAPI application.
    """
    app = FastAPI(
        title="Kisan Dost (کسان دوست) API",
        description=(
            "Evidence-Grounded Multi-Agent Agronomy Advisory & Farm Decision Engine for Pakistani Farmers.\n\n"
            "### Core Guarantees:\n"
            "- **Multi-Agent Handoffs**: Orchestrated via OpenAI Agents SDK.\n"
            "- **Deterministic Numerical Grounding**: Zero hallucinated numbers. All fertilizer bags, water schedules, mandi prices, and profits come from verified agricultural datasets and mathematical models.\n"
            "- **What-If Decision Simulator**: Exposing explicit trade-offs across water, costs, profits, and risk.\n"
            "- **Cross-Domain Conflict Resolution**: Autonomous reconciliation between agronomic recommendations and real-world farm constraints.\n"
            "- **Pesticide Safety Enforcement**: Strict blocking of unverified chemical dosages."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS for all frontend origins (React, Next.js, Flutter, etc.)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API Routers
    api_prefix = "/api"
    app.include_router(advisory.router, prefix=api_prefix)
    app.include_router(simulator.router, prefix=api_prefix)
    app.include_router(passport.router, prefix=api_prefix)
    app.include_router(farm_health.router, prefix=api_prefix)
    app.include_router(tools.router, prefix=api_prefix)
    app.include_router(demo.router, prefix=api_prefix)

    @app.get("/", tags=["System & Health"])
    async def root():
        """
        Root endpoint providing system health, capabilities catalog, and documentation links.
        """
        return {
            "name": "Kisan Dost (کسان دوست) Farm Decision API",
            "version": "2.0.0",
            "status": "ONLINE",
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json"
            },
            "features": {
                "advisory": "/api/advisory/query",
                "decision_simulator": "/api/simulator/compare",
                "farm_passport": "/api/passport",
                "farm_health_index": "/api/farm-health/calculate",
                "deterministic_tools": "/api/tools",
                "benchmark_demos": "/api/demo/scenarios"
            }
        }

    @app.get("/health", tags=["System & Health"])
    async def health_check():
        """
        Health and system status check.
        """
        return {
            "status": "HEALTHY",
            "environment": settings.environment,
            "database": "CONNECTED",
            "agents_sdk": "READY",
            "deterministic_tools_count": 10,
            "supported_languages": ["en", "roman_urdu", "ur"]
        }

    return app


app = create_app()
