from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text from LLM with given system and user instructions."""
        pass


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def create_embedding(self, text: str) -> List[float]:
        """Generate high-dimensional semantic vector embedding for input text."""
        pass
