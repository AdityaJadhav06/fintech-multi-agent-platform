import requests
from typing import List, Optional
from app.config import settings
from app.providers.base import BaseLLMProvider, BaseEmbeddingProvider


class OllamaLLMProvider(BaseLLMProvider):
    """
    LLM Provider that communicates with a local Ollama instance (e.g. Llama 3.2).
    """

    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model: str = settings.OLLAMA_CHAT_MODEL,
        timeout: int = 180,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.chat_url = f"{self.base_url}/api/chat"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {
                "temperature": temperature,
            },
            "stream": False,
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            resp = requests.post(self.chat_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Ollama chat error ({self.model} at {self.chat_url}): {str(e)}")


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """
    Embedding Provider that communicates with a local Ollama instance (e.g. nomic-embed-text).
    """

    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model: str = settings.OLLAMA_EMBED_MODEL,
        timeout: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.embed_url = f"{self.base_url}/api/embed"

    def create_embedding(self, text: str) -> List[float]:
        payload = {
            "model": self.model,
            "input": text,
        }
        try:
            resp = requests.post(self.embed_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # Ollama /api/embed returns {"embeddings": [[...]]}
            embeddings = data.get("embeddings")
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            # Fallback for older ollama /api/embeddings: {"embedding": [...]}
            return data.get("embedding", [])
        except Exception as e:
            raise RuntimeError(f"Ollama embed error ({self.model} at {self.embed_url}): {str(e)}")
