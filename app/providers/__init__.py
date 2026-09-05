from app.config import settings
from app.providers.base import BaseLLMProvider, BaseEmbeddingProvider
from app.providers.mock_provider import MockLLMProvider, MockEmbeddingProvider
from app.providers.ollama_provider import OllamaLLMProvider, OllamaEmbeddingProvider


def get_llm_provider() -> BaseLLMProvider:
    provider_type = settings.LLM_PROVIDER.lower()
    if provider_type == "ollama":
        try:
            return OllamaLLMProvider()
        except Exception:
            return MockLLMProvider()
    return MockLLMProvider()


def get_embedding_provider() -> BaseEmbeddingProvider:
    provider_type = settings.EMBEDDING_PROVIDER.lower()
    if provider_type == "ollama":
        try:
            return OllamaEmbeddingProvider()
        except Exception:
            return MockEmbeddingProvider()
    return MockEmbeddingProvider()
