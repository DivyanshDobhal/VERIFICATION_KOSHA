from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import auth, workers, biometrics, sessions, recognition_reviews, analytics, sites

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Worker Identity Management System – Mobile Biometric REST API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup for Capacitor Mobile (Android/iOS) and Web Client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized Error Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. No biometric templates were compromised.",
            "status_code": 500,
        }
    )

# Register Routers under /api/v1 and /api
app.include_router(auth.router, prefix="/api")
app.include_router(workers.router, prefix="/api")
app.include_router(biometrics.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(recognition_reviews.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(sites.router, prefix="/api")

@app.get("/health")
async def health_check():
    from app.ml.model_loader import model_manager
    return {
        "status": "healthy",
        "service": "Kosha Labs Biometric API",
        "version": settings.VERSION,
        "model_configured": model_manager.is_configured(),
        "model_file": model_manager.resolved_model_file,
        "model_info": model_manager.model_summary_info,
    }

