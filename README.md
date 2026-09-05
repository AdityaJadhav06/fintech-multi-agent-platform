# FinTech Multi-Agent Platform
### Decision-Support Architecture for Cross-Functional Business Strategy
**Marketing • Financial • Legal • Technology • HR • ESG • GTM • Risk • Orchestrator**

---

## 🌟 Overview

The **FinTech Multi-Agent Platform** coordinates eight specialized AI domain agents under an autonomous Orchestrator supervisor to evaluate multi-faceted business, technical, and regulatory initiatives.

### Master Question Scenario
> **"Should we launch an AI-enabled lending product for SMEs in India?"**

---

## 🏗️ Architecture

- **Frontend**: Lovable Web Application / React SPA (consuming FastAPI REST & SSE streams).
- **Authentication**: Auth0 JWT validation with multi-tenant isolation (`org_id`).
- **Backend**: FastAPI asynchronous REST API + Server-Sent Events (SSE).
- **Orchestrator**: 4-Wave DAG Task Planner with parallel wave concurrency, context minimization, and conflict handling.
- **Agents (8 Domain Specialists)**:
  - **Financial Agent**: Deterministic Python math for break-even, LTV/CAC, and cash runway.
  - **Legal Agent**: RBI Digital Lending & DPDP Act compliance review with human review flags.
  - **Technology Agent**: Cloud microservices feasibility and hosting cost estimates.
  - **HR Agent**: Semantic candidate resume matching via cosine similarity with strict anti-bias guardrails.
  - **Marketing Agent**: Tier-2 Indian SME customer segmentation and CAC projections.
  - **ESG Agent**: Cloud compute emissions estimator and financial inclusion scoring.
  - **GTM Agent**: Commercial launch phasing and dependency validation.
  - **Risk Agent**: Centralized 5×5 Risk Register aggregation and mitigation planning.
- **Storage**: SQLAlchemy (Async) with SQLite default for zero-setup local lab runs, switchable to MySQL/Postgres.
- **RAG & Vector Search**: Deterministic cosine similarity chunk retrieval.

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.9+ installed
- (Optional) [Ollama](https://ollama.ai) installed with `llama3.2` and `nomic-embed-text` models.

### 2. Setup Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# Install requirements:
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```

### 4. Run the Platform API Server
```bash
uvicorn app.main:app --reload --port 8000
```
Visit API Documentation: `http://localhost:8000/docs`

### 5. Run Automated Verification Tests
```bash
pytest
```

---

## 📚 Documentation
- Full Architectural Specification & Viva Guide: [`docs/SYSTEM_REQUIREMENTS_BLUEPRINT.md`](docs/SYSTEM_REQUIREMENTS_BLUEPRINT.md)
