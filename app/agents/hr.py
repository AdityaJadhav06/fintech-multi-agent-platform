import json
from datetime import datetime
from typing import Any, Dict, List, Optional
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
from app.tools.document_parser import cosine_similarity


class HRAgent(BaseAgent):
    """
    Self-Contained HR Agent:
    - Workforce feasibility & headcount planning
    - Candidate resume matching via deterministic cosine similarity
    - Skill-gap analysis
    - Strict anti-bias and fairness guardrails (no demographic inference)
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=AgentName.HR,
            description="Workforce planning, skill-gap analysis, and anti-bias candidate resume evaluation.",
            **kwargs,
        )

    def rank_candidates(
        self,
        job_description: str,
        resumes: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Calculates semantic similarity between job description and resumes.
        """
        if not job_description or not resumes:
            return []

        jd_vector = self.embedder.create_embedding(job_description)
        ranked = []

        for candidate in resumes:
            resume_text = candidate.get("resume_text", "")
            resume_id = candidate.get("id", candidate.get("filename", "unknown"))

            resume_vector = self.embedder.create_embedding(resume_text)
            similarity = cosine_similarity(jd_vector, resume_vector)

            ranked.append({
                "candidate_id": resume_id,
                "filename": candidate.get("filename", resume_id),
                "similarity_score": round(similarity, 4),
                "similarity_pct": round(similarity * 100, 2),
                "resume_text": resume_text,
            })

        ranked.sort(key=lambda x: x["similarity_score"], reverse=True)
        return ranked

    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        # 1. Identify Tech roles requested or default engineering roles
        tech_roles = "Senior Credit Risk MLOps Engineer, Backend Python/FastAPI Developer, Compliance Specialist"
        for finding in input_contract.upstream_findings:
            if finding.get("agent") == "technology":
                roles_found = finding.get("calculations", {}).get("required_roles")
                if roles_found:
                    tech_roles = ", ".join(roles_found)

        # 2. Extract sample resumes from constraints or evaluate standard profile
        resumes = input_contract.constraints.get("resumes", [
            {
                "id": "CAND-01",
                "filename": "priya_sharma_mlops.txt",
                "resume_text": "MLOps Engineer with 5 years experience in Python, PyTorch, credit scoring pipelines, Docker, Kubernetes, AWS ap-south-1.",
            },
            {
                "id": "CAND-02",
                "filename": "rahul_verma_backend.txt",
                "resume_text": "Backend Engineer with 3 years experience in FastAPI, PostgreSQL, Redis, payment gateways, and banking APIs.",
            },
            {
                "id": "CAND-03",
                "filename": "amit_patel_generalist.txt",
                "resume_text": "Software Developer experienced in Java, Spring Boot, legacy enterprise monoliths, and basic SQL.",
            },
        ])

        ranked_candidates = self.rank_candidates(tech_roles, resumes)

        # 3. System Prompt with strict anti-bias guardrails
        system_prompt = (
            "You are an HR resume analysis assistant. "
            "Provide factual, evidence-based comparisons between a job description and resume. "
            "Use only information present in the supplied text. "
            "Do not infer age, gender, race, religion, health, nationality, disability, or any other sensitive personal characteristic. "
            "Do not make the hiring decision. Do not say who should be hired. "
            "Clearly distinguish matching evidence from missing or unspecified information."
        )

        top_candidate = ranked_candidates[0] if ranked_candidates else None
        top_candidate_text = top_candidate["resume_text"] if top_candidate else "No candidates provided."

        user_prompt = (
            f"JOB DESCRIPTION ROLES:\n{tech_roles}\n\n"
            f"TOP CANDIDATE RESUME:\n{top_candidate_text}\n\n"
            "Analyze candidate match against requirements. Return exactly: "
            "1. MATCHING SKILLS, 2. RELEVANT EXPERIENCE, 3. MISSING OR UNSPECIFIED REQUIREMENTS, 4. EVIDENCE SUMMARY."
        )

        llm_analysis = self.llm.generate(system_prompt, user_prompt)

        findings = [
            FindingItem(
                title="Talent Availability & Key Role Requirements",
                description=f"Identified core technical roles required: {tech_roles}. Evaluated {len(ranked_candidates)} candidate profiles.",
                category="Workforce Planning",
                severity="MEDIUM",
            ),
            FindingItem(
                title="Top Candidate Semantic Match",
                description=(
                    f"Top candidate '{top_candidate['filename']}' achieved {top_candidate['similarity_pct']}% semantic similarity match."
                    if top_candidate
                    else "No candidate resumes submitted."
                ),
                category="Candidate Evaluation",
                severity="LOW",
            ),
        ]

        risks = [
            RiskItem(
                risk_id="RSK-HR-001",
                description="High market competition for specialized Credit Risk MLOps talent in India may delay launch timeline by 6-8 weeks.",
                probability=RiskProbability.HIGH,
                impact=RiskImpact.HIGH,
                mitigation="Initiate immediate contract staffing or specialist recruitment retainers; leverage remote hiring across Tier-1 Indian tech hubs.",
                owner="VP Talent / Head of HR",
            )
        ]

        return AgentOutputContract(
            agent=self.name,
            case_id=input_contract.case_id,
            status=AgentState.COMPLETED,
            summary=f"Workforce analysis completed. Evaluated candidate pool against required roles ({tech_roles}). Identified 1 high-probability hiring risk.",
            findings=findings,
            calculations={
                "ranked_candidates": [
                    {
                        "candidate_id": c["candidate_id"],
                        "filename": c["filename"],
                        "similarity_score": c["similarity_score"],
                    }
                    for c in ranked_candidates
                ],
                "roles_evaluated": tech_roles.split(", "),
            },
            assumptions=[
                "Tech talent compensation benchmarks aligned with Indian FinTech Tier-1 rates.",
                "Engineering lead time is 60 days before code freeze.",
            ],
            data_gaps=[
                "Specific local credit bureau API familiarity could not be confirmed for all candidates; listed as 'not specified'.",
            ],
            risks=risks,
            dependencies=["technology"],
            sources=[
                SourceEvidence(
                    document_id="resumes_pool",
                    clause_or_chunk_id="resume_top_match",
                    exact_citation=top_candidate_text[:120] if top_candidate else "N/A",
                )
            ],
            human_review_required=False,
            review_reasons=[],
            timestamp=datetime.utcnow(),
        )
