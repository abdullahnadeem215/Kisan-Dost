"""
Kisan Dost — FastAPI Server Entry Point
Run with: python server.py
"""
import sys
import uvicorn
from config.settings import settings

if __name__ == "__main__":
    print("=" * 70)
    print("🌾 KISAN DOST (کسان دوست) — AI AGRONOMY MULTI-AGENT API SERVER")
    print("=" * 70)
    print(f"• Swagger API Docs: http://localhost:{settings.api_port}/docs")
    print(f"• ReDoc Docs:      http://localhost:{settings.api_port}/redoc")
    print(f"• Health Check:    http://localhost:{settings.api_port}/health")
    print(f"• Base API URL:    http://localhost:{settings.api_port}/api")
    print("=" * 70)
    
    uvicorn.run(
        "app.api.app:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=True
    )
