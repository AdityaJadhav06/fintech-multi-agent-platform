from typing import Dict
from app.agents.base import BaseAgent
from app.schemas.agent_contracts import AgentName
from app.agents.marketing import MarketingAgent
from app.agents.financial import FinancialAgent
from app.agents.legal import LegalAgent
from app.agents.technology import TechnologyAgent
from app.agents.hr import HRAgent
from app.agents.esg import ESGAgent
from app.agents.gtm import GTMAgent
from app.agents.risk import RiskAgent

AGENT_REGISTRY: Dict[AgentName, type] = {
    AgentName.MARKETING: MarketingAgent,
    AgentName.FINANCIAL: FinancialAgent,
    AgentName.LEGAL: LegalAgent,
    AgentName.TECHNOLOGY: TechnologyAgent,
    AgentName.HR: HRAgent,
    AgentName.ESG: ESGAgent,
    AgentName.GTM: GTMAgent,
    AgentName.RISK: RiskAgent,
}


def create_agent(name: AgentName, **kwargs) -> BaseAgent:
    agent_cls = AGENT_REGISTRY.get(name)
    if not agent_cls:
        raise ValueError(f"Unknown agent name: {name}")
    return agent_cls(**kwargs)
