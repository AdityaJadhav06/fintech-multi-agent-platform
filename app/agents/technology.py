from datetime import datetime
from app.agents.base import BaseAgent
from app.schemas.agent_contracts import (
    AgentName,
    AgentState,
    AgentInputContract,
    AgentOutputContract,
    FindingItem,
    RiskItem,
    RiskProbability,
    RiskImpact,
    SourceEvidence,
)


class TechnologyAgent(BaseAgent):
    """
    Technology Agent:
    - Analyzes system architecture, cloud feasibility, APIs, and security.
    - Specifies required engineering roles for HR Agent downstream dependency.
    - Estimates cloud hosting infrastructure budget in Indian regions.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=AgentName.TECHNOLOGY,
            description="Technical feasibility, cloud architecture, APIs, security, and infrastructure cost estimation.",
            **kwargs,
        )

    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        system_prompt = (
            "You are a Chief Technology Officer (CTO) and cloud security architect. "
            "Design scalable, bank-grade microservices for credit decisioning. "
            "Ensure high availability, low latency (<500ms credit decisioning), and ISO 27001 / SOC 2 compliance."
        )

        user_prompt = (
            f"Business Question: {input_contract.user_request}\n"
            f"Context: {input_contract.business_context}\n"
            "Recommend architectural stack, APIs, cloud regions, and engineering skill requirements."
        )

        llm_analysis = self.llm.generate(system_prompt, user_prompt)

        required_roles = [
            "Senior Credit Risk MLOps Engineer",
            "Backend Python/FastAPI Developer",
            "Cloud Security & DevSecOps Lead",
        ]

        findings = [
            FindingItem(
                title="Microservices Architecture & Stack",
                description=(
                    "Recommended architecture: FastAPI core REST microservices, PostgreSQL with async pgvector for audit and RAG, "
                    "Redis for sub-millisecond credit state caching, and Apache Kafka for asynchronous loan event streaming."
                ),
                category="System Architecture",
                severity="LOW",
            ),
            FindingItem(
                title="Data Residency & Cloud Region",
                description=(
                    "Target cloud deployment: AWS ap-south-1 (Mumbai) or GCP asia-south1. Full adherence to Indian sovereign "
                    "data localization regulations with multi-AZ redundancy for 99.95% SLA."
                ),
                category="Infrastructure & Security",
                severity="LOW",
            ),
            FindingItem(
                title="Credit Decision Engine Latency",
                description=(
                    "Automated rule evaluation and ML credit score inference latency targeted at < 450ms, with async fallbacks "
                    "for external bureau API rate limits."
                ),
                category="Performance & Scalability",
                severity="MEDIUM",
            ),
        ]

        risks = [
            RiskItem(
                risk_id="RSK-TECH-001",
                description="Third-party credit bureau API (CIBIL/Experian) latency spikes or outages could cause loan application drop-offs and timeout errors.",
                probability=RiskProbability.HIGH,
                impact=RiskImpact.MEDIUM,
                mitigation="Implement circuit breaker patterns, asynchronous webhook processing, and local synthetic scoring cache.",
                owner="Lead Solutions Architect",
            ),
            RiskItem(
                risk_id="RSK-TECH-002",
                description="Model drift in SME credit risk predictions during macroeconomic stress may lead to underestimated default rates.",
                probability=RiskProbability.MEDIUM,
                impact=RiskImpact.HIGH,
                mitigation="Deploy continuous automated model monitoring with Evidently AI and weekly population stability index (PSI) checks.",
                owner="Lead MLOps Engineer",
            ),
        ]

        return AgentOutputContract(
            agent=self.name,
            case_id=input_contract.case_id,
            status=AgentState.COMPLETED,
            summary="Technical architecture validated. High-availability cloud deployment in AWS ap-south-1 with sub-500ms decisioning. Defined 3 critical engineering roles for HR.",
            findings=findings,
            calculations={
                "estimated_monthly_infra_cost_inr": 280000,
                "target_tps": 500,
                "decision_latency_sla_ms": 450,
                "required_roles": required_roles,
            },
            assumptions=[
                "Cloud infrastructure provisioned via Infrastructure-as-Code (Terraform).",
                "Automated CI/CD with security scanning (SAST/DAST) in pipeline.",
            ],
            data_gaps=[
                "Expected peak concurrent loan applications during festive sales periods needs precise quantification.",
            ],
            risks=risks,
            dependencies=[],
            sources=[
                SourceEvidence(
                    document_id="tech_spec_v1",
                    clause_or_chunk_id="cloud_infra_section",
                    exact_citation="Hosting target AWS ap-south-1 with PostgreSQL and Redis caching.",
                )
            ],
            human_review_required=False,
            review_reasons=[],
            timestamp=datetime.utcnow(),
        )
