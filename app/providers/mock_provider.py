import hashlib
import math
import random
from typing import List, Optional
from app.providers.base import BaseLLMProvider, BaseEmbeddingProvider


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM Provider for offline student labs, unit testing,
    and fast CI/CD execution without local Ollama or cloud API keys.
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        prompt_lower = (user_prompt + " " + system_prompt).lower()

        if "marketing" in prompt_lower:
            return (
                "Market Analysis Summary:\n"
                "Target Market: Indian Micro, Small, and Medium Enterprises (MSMEs) with turnover between INR 50L and 5Cr.\n"
                "Positioning: Frictionless collateral-free digital working capital credit with 24-hour sanction.\n"
                "Key Channels: Digital GST/UPI ecosystem integration, regional merchant associations, NBFC co-origination.\n"
                "CAC Assumption: Estimated at INR 3,500 - 4,500 per approved borrower through digital channels."
            )
        elif "financial" in prompt_lower:
            return (
                "Financial Viability Summary:\n"
                "Unit Economics: Loan spread of 4.5% over cost of funds is sufficient to achieve break-even at 1,250 loans/month.\n"
                "Assumptions: Average loan ticket size INR 3,00,000; tenure 12 months; credit default rate capped at 3.5%.\n"
                "Cash Runway: Initial INR 5Cr capital provides 18 months runway under base-case loan book expansion."
            )
        elif "legal" in prompt_lower:
            return (
                "Legal & Regulatory Assessment:\n"
                "Regulatory Framework: Subject to RBI Digital Lending Guidelines (2022) and DPDP Act (2023).\n"
                "Compliance Constraint: All loan disbursals and collections must flow directly between RE bank accounts without pass-through accounts.\n"
                "Human Review: Certified Indian legal counsel must review the lending partnership agreement."
            )
        elif "technology" in prompt_lower:
            return (
                "Technology Feasibility & Architecture:\n"
                "Recommended Stack: FastAPI microservices, PostgreSQL with pgvector, Redis cache, hosted in AWS ap-south-1 (Mumbai).\n"
                "Scalability: Designed for 5,000 RPM underwriting throughput with sub-second credit bureau API integration.\n"
                "Estimated Cloud Cost: INR 2,50,000 - 3,50,000 monthly for high-availability multi-AZ deployment."
            )
        elif "hr" in prompt_lower:
            return (
                "Workforce & Talent Assessment:\n"
                "1. MATCHING SKILLS: Core Python, FastAPI, Credit Risk Modeling, Machine Learning.\n"
                "2. RELEVANT EXPERIENCE: 4+ years in financial services and fintech engineering.\n"
                "3. MISSING OR UNSPECIFIED REQUIREMENTS: India credit bureau (CIBIL/Experian) API experience is not specified.\n"
                "4. EVIDENCE SUMMARY: Strong technical background suitable for credit decision engine development."
            )
        elif "esg" in prompt_lower:
            return (
                "ESG Impact Assessment:\n"
                "Environmental: Cloud data center carbon footprint estimated at 120 kg CO2e/month.\n"
                "Social: Accelerates financial inclusion for underserved Tier-2/Tier-3 micro-enterprises previously dependent on informal moneylenders.\n"
                "Governance: Transparent automated APR disclosures eliminate hidden processing fees."
            )
        elif "gtm" in prompt_lower:
            return (
                "Go-To-Market Strategy:\n"
                "Phase 1 (Months 1-3): Closed pilot with 200 pre-screened merchant borrowers in Maharashtra and Gujarat.\n"
                "Phase 2 (Months 4-6): Expansion to 5 major industrial clusters via anchor merchant partnerships.\n"
                "Phase 3 (Months 7-12): Pan-India digital marketing and automated underwriting scale-up."
            )
        elif "risk" in prompt_lower:
            return (
                "Risk Analysis:\n"
                "Identified key operational, regulatory, and credit default risks across all domains.\n"
                "Central mitigations established including reserve capital, automated bureau cross-checks, and Indian cloud data residency."
            )
        else:
            return (
                "Orchestrated Synthesis:\n"
                "The proposed AI-enabled lending initiative for Indian SMEs is technically and commercially viable.\n"
                "Key prerequisite: Secure NBFC/Bank regulated entity partnership and complete human legal sign-off."
            )


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic embedding provider that maps input text to a 384-dimensional
    normalized pseudo-vector based on MD5 and SHA-256 hash seeds.
    Ensures identical texts yield identical vectors with accurate cosine similarity properties.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def create_embedding(self, text: str) -> List[float]:
        # Hash text into seeds
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Seed pseudo-random generator deterministically
        seed = int.from_bytes(h[:8], "big")
        rnd = random.Random(seed)

        # Generate vector
        raw_vector = [rnd.uniform(-1.0, 1.0) for _ in range(self.dimensions)]

        # Normalize vector to unit length
        magnitude = math.sqrt(sum(x * x for x in raw_vector))
        if magnitude == 0:
            return [0.0] * self.dimensions
        return [x / magnitude for x in raw_vector]
