"""
QR Code Generator API - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints import qr, auth
from src.middleware.auth import auth_middleware
from src.utils.logging import setup_logging, LoggingMiddleware

# Setup logging first
setup_logging()

app = FastAPI(
    title="QR Code Generator API",
    description="Secure stateless API for generating QR codes in multiple formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add authentication middleware
app.middleware("http")(auth_middleware)

# Include routers
app.include_router(auth.router, prefix="/v1", tags=["Authentication"])
app.include_router(qr.router, prefix="/v1", tags=["QR Code Generation"])


@app.get("/v1/health")
async def health_check():
    """Health check endpoint (no authentication required)"""
    return {
        "status": "healthy",
        "timestamp": "2025-11-14T10:30:00Z",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
