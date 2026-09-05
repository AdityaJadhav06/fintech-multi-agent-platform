from typing import Any, Dict, List, Optional
from app.providers import get_embedding_provider
from app.providers.base import BaseEmbeddingProvider
from app.tools.document_parser import cosine_similarity, chunk_text


class VectorStoreIndex:
    """
    RAG Vector Store for storing, embedding, and semantic similarity search over document chunks.
    """

    def __init__(self, embedding_provider: Optional[BaseEmbeddingProvider] = None):
        self.embedder = embedding_provider or get_embedding_provider()
        self.indexed_chunks: List[Dict[str, Any]] = []

    def add_document(
        self,
        document_id: str,
        filename: str,
        text_content: str,
        chunk_size: int = 250,
        overlap: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Chunks text, generates embeddings, and adds to the index.
        """
        chunks = chunk_text(text_content, chunk_size, overlap)
        added = []

        for c in chunks:
            chunk_id = f"{document_id}_chk_{c['chunk_index']}"
            vector = self.embedder.create_embedding(c["content"])

            record = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "filename": filename,
                "chunk_index": c["chunk_index"],
                "content": c["content"],
                "vector": vector,
            }
            self.indexed_chunks.append(record)
            added.append(record)

        return added

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.50,
        filter_doc_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Cosine similarity search across indexed document chunks.
        """
        if not self.indexed_chunks or not query:
            return []

        query_vec = self.embedder.create_embedding(query)
        scored_chunks = []

        for item in self.indexed_chunks:
            if filter_doc_ids and item["document_id"] not in filter_doc_ids:
                continue

            sim = cosine_similarity(query_vec, item["vector"])
            if sim >= min_similarity:
                scored_chunks.append({
                    "chunk_id": item["chunk_id"],
                    "document_id": item["document_id"],
                    "filename": item["filename"],
                    "content": item["content"],
                    "similarity": round(sim, 4),
                })

        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:top_k]


# Global shared in-memory instance for active session
vector_store = VectorStoreIndex()
