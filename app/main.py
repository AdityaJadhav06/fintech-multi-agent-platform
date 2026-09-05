from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.api import cases_router, agents_router, risks_router, approvals_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB schema & seed tenant
    await init_db()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "FinTech Multi-Agent Decision-Support Platform with specialized domain agents: "
        "Marketing, Financial, Legal, Technology, HR, ESG, GTM, Risk, and Orchestrator."
    ),
    lifespan=lifespan,
)

# Enable CORS for Lovable frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(cases_router)
app.include_router(agents_router)
app.include_router(risks_router)
app.include_router(approvals_router)


@app.get("/", tags=["System"])
async def root():
    return {
        "platform": settings.APP_NAME,
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "agents": [
            "marketing",
            "financial",
            "legal",
            "technology",
            "hr",
            "esg",
            "gtm",
            "risk",
            "orchestrator",
        ],
        "documentation": "/docs",
    }


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "mock_auth_enabled": settings.MOCK_AUTH_ENABLED,
    }
