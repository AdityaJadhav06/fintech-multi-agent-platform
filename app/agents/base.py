from abc import ABC, abstractmethod
from typing import Optional
from app.schemas.agent_contracts import AgentName, AgentInputContract, AgentOutputContract
from app.providers import get_llm_provider, get_embedding_provider
from app.providers.base import BaseLLMProvider, BaseEmbeddingProvider


class BaseAgent(ABC):
    """
    Abstract Base Class for all specialized FinTech Domain Agents.
    Enforces common interface, typed contract compliance, and isolated execution.
    """

    def __init__(
        self,
        name: AgentName,
        description: str,
        llm_provider: Optional[BaseLLMProvider] = None,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
    ):
        self.name = name
        self.description = description
        self.llm = llm_provider or get_llm_provider()
        self.embedder = embedding_provider or get_embedding_provider()

    @abstractmethod
    async def run(self, input_contract: AgentInputContract) -> AgentOutputContract:
        """
        Execute domain-specific analysis, tools, and guardrails.
        Must return a validated AgentOutputContract.
        """
        pass
