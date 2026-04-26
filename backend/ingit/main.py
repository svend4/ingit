"""
InGit FastAPI Application
Main entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ingit.config import settings
from ingit.api import projects, tasks, documents, health

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="InGit - Integrated Git Platform with Offline-First Approach",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/api/docs",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.ENVIRONMENT == "development" else None,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "ingit.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
