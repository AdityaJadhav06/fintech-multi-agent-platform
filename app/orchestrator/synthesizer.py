from datetime import datetime
from typing import Any, Dict, List, Optional
from app.schemas.agent_contracts import AgentName, AgentOutputContract
from app.schemas.case import FinalReportResponse
from app.providers import get_llm_provider
from app.providers.base import BaseLLMProvider


class ReportSynthesizer:
    """
    Synthesizes domain outputs into an executive decision-support report:
    - Identifies cross-domain contradictions and conflicts
    - Gathers all human-review tickets
    - Extracts deterministic financial metrics and Central Risk Register
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def detect_conflicts(
        self,
        agent_outputs: Dict[AgentName, AgentOutputContract],
    ) -> List[str]:
        """
        Rule-based and semantic conflict detection across domain findings.
        """
        conflicts = []

        # Conflict Check 1: Marketing customer volumes vs Technology capacity
        mkt_leads = 0
        if AgentName.MARKETING in agent_outputs:
            mkt_calcs = agent_outputs[AgentName.MARKETING].calculations
            mkt_leads = mkt_calcs.get("target_monthly_leads", 0)

        tech_tps = 0
        if AgentName.TECHNOLOGY in agent_outputs:
            tech_calcs = agent_outputs[AgentName.TECHNOLOGY].calculations
            tech_tps = tech_calcs.get("target_tps", 0)

        if mkt_leads > 100000 and tech_tps < 200:
            conflicts.append(
                f"Capacity Mismatch: Marketing targets {mkt_leads:,} monthly leads, but Technology "
                f"architecture is currently provisioned for {tech_tps} TPS."
            )

        # Conflict Check 2: GTM Launch date vs Legal Human Review requirement
        legal_blocked = False
        if AgentName.LEGAL in agent_outputs:
            legal_blocked = agent_outputs[AgentName.LEGAL].human_review_required

        if AgentName.GTM in agent_outputs:
            gtm_calcs = agent_outputs[AgentName.GTM].calculations
            months_to_pilot = gtm_calcs.get("months_to_pilot", 0)
            if legal_blocked and months_to_pilot < 2:
                conflicts.append(
                    "Timeline Risk: GTM schedules pilot launch in under 2 months, but mandatory "
                    "RBI legal compliance certification remains unresolved and flagged for human review."
                )

        return conflicts

    def synthesize(
        self,
        case_id: str,
        master_question: str,
        agent_outputs: Dict[AgentName, AgentOutputContract],
    ) -> FinalReportResponse:
        """
        Builds the consolidated decision-support response.
        """
        domain_summaries: Dict[str, str] = {}
        all_findings: List[Dict[str, Any]] = []
        deterministic_metrics: Dict[str, Any] = {}
        central_risks: List[Dict[str, Any]] = []
        open_questions: List[str] = []
        human_review_reasons: List[str] = []
        requires_human_review = False

        for name, output in agent_outputs.items():
            domain_summaries[name.value] = output.summary

            for f in output.findings:
                all_findings.append({
                    "agent": name.value,
                    "title": f.title,
                    "description": f.description,
                    "category": f.category,
                    "severity": f.severity,
                })

            if output.calculations:
                deterministic_metrics[name.value] = output.calculations

            open_questions.extend(output.data_gaps)

            if output.human_review_required:
                requires_human_review = True
                human_review_reasons.extend(output.review_reasons)

        # Build Central Risk Register: Prioritize Risk Agent's compiled and scored register
        if AgentName.RISK in agent_outputs and agent_outputs[AgentName.RISK].risks:
            for r in agent_outputs[AgentName.RISK].risks:
                central_risks.append({
                    "agent": "risk",
                    "risk_id": r.risk_id,
                    "description": r.description,
                    "probability": r.probability.value,
                    "impact": r.impact.value,
                    "severity_score": r.severity_score,
                    "mitigation": r.mitigation,
                    "owner": r.owner,
                })
        else:
            for name, output in agent_outputs.items():
                for r in output.risks:
                    central_risks.append({
                        "agent": name.value,
                        "risk_id": r.risk_id,
                        "description": r.description,
                        "probability": r.probability.value,
                        "impact": r.impact.value,
                        "severity_score": r.severity_score,
                        "mitigation": r.mitigation,
                        "owner": r.owner,
                    })

        conflicts = self.detect_conflicts(agent_outputs)

        system_prompt = (
            "You are the Executive Supervisor of a FinTech Multi-Agent Decision Platform. "
            "Synthesize domain findings into a concise, professional executive briefing. "
            "Clearly present the bottom-line decision recommendation, key constraints, and governance gates."
        )

        user_prompt = (
            f"Master Question: {master_question}\n"
            f"Domain Summaries: {domain_summaries}\n"
            f"Conflicts Identified: {conflicts}\n"
            f"Human Review Required: {requires_human_review} ({human_review_reasons})\n"
            "Provide the final executive decision synthesis."
        )

        synthesis_text = self.llm.generate(system_prompt, user_prompt)

        return FinalReportResponse(
            case_id=case_id,
            master_question=master_question,
            synthesis_summary=synthesis_text,
            domain_summaries=domain_summaries,
            key_findings=all_findings,
            deterministic_metrics=deterministic_metrics,
            central_risk_register=central_risks,
            open_questions_and_gaps=open_questions,
            conflicts_identified=conflicts,
            human_review_required=requires_human_review,
            review_reasons=human_review_reasons,
            generated_at=datetime.utcnow(),
        )
