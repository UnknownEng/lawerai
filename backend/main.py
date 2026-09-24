"""
LawerAI (Qanoon Sahayak) — Pakistani Legal Information & Intake Platform
FastAPI Production Application Entry Point with Rate Limiting, CORS restrictions,
and Secure Storage Routing.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .database import init_db
from .rate_limiter import limiter
from .routers import auth_router, chat_router, lawyer_router, emergency_router, corpus_router, feedback_router
from .safety import LEGAL_DISCLAIMER
from ingestion.vector_store import LegalVectorStore
from ingestion.corpus_loader import load_corpus_documents

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lawerai")



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Initializing {settings.APP_NAME} ({settings.ENVIRONMENT})...")
    # Initialize DB (in dev creates tables; in prod Alembic runs in release phase)
    await init_db()
    logger.info("Database connection and tables initialized.")

    # Ensure vector store is loaded or built
    store = LegalVectorStore(storage_path=settings.VECTOR_STORE_PATH)
    if not store.documents:
        logger.info("No vector store index found. Loading curated statutory corpus...")
        docs = load_corpus_documents(settings.CORPUS_DIR)
        if docs:
            store.build_index(docs)
            logger.info(f"Ingested {len(docs)} legal sections into vector store.")

    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Legal Information & Intake Platform grounded in Pakistani Law (PPC, CrPC, CPC, Family, Rent, QSO)",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware with explicit origins
allowed_origins = settings.get_allowed_origins()
logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(lawyer_router.router)
app.include_router(emergency_router.router)
app.include_router(corpus_router.router)
app.include_router(feedback_router.router)


@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "storage_backend": settings.STORAGE_BACKEND,
        "disclaimer": LEGAL_DISCLAIMER
    }


@app.get("/api/disclaimer")
async def get_disclaimer():
    return {
        "disclaimer": LEGAL_DISCLAIMER,
        "legal_notice": "LawerAI / Qanoon Sahayak is an educational and legal information assistant in closed beta. It is NOT a substitute for a licensed advocate. Always consult a lawyer licensed by the Bar Council."
    }


@app.get("/api/beta-info")
async def get_beta_info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "require_beta_code": settings.REQUIRE_BETA_CODE,
        "banner_text": "BETA — under legal review by Pakistani advocates, not for reliance as professional legal counsel."
    }


# Mount Frontend React build if available (e.g. unified container deployment)
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
