from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import courses, enrollments, progress

app = FastAPI(
    title="LearnHub Core API (FastAPI)",
    description="High-performance services for Courses, Enrollments, and Progress in LearnHub LMS",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers under /api and direct routes
app.include_router(courses.router, prefix="/api")
app.include_router(enrollments.router, prefix="/api")
app.include_router(progress.router, prefix="/api")

# Also mount under /fastapi prefix for distinct routing if desired
app.include_router(courses.router, prefix="/fastapi")
app.include_router(enrollments.router, prefix="/fastapi")
app.include_router(progress.router, prefix="/fastapi")


@app.get("/")
@app.get("/health/")
def health_check():
    return {
        "status": "healthy",
        "service": "LearnHub FastAPI Backend",
        "version": "1.0.0",
    }
