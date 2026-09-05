import math
import os
from typing import Any, Dict, List


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Computes deterministic cosine similarity between two float vectors.
    Returns value between -1.0 and 1.0.
    """
    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        min_len = min(len(vector_a), len(vector_b))
        vector_a = vector_a[:min_len]
        vector_b = vector_b[:min_len]

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    mag_a = math.sqrt(sum(a * a for a in vector_a))
    mag_b = math.sqrt(sum(b * b for b in vector_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_product / (mag_a * mag_b)


def chunk_text(
    text: str,
    chunk_size_words: int = 250,
    overlap_words: int = 30,
) -> List[Dict[str, Any]]:
    """
    Splits document text into overlapping token/word windows with sequence tracking.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    chunk_idx = 0

    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunk_content = " ".join(words[start:end])

        chunks.append({
            "chunk_index": chunk_idx,
            "content": chunk_content,
            "word_count": end - start,
            "start_word": start,
            "end_word": end,
        })

        chunk_idx += 1
        if end >= len(words):
            break
        start += (chunk_size_words - overlap_words)

    return chunks


def extract_text_from_file(file_path: str) -> str:
    """
    Reads plain text or basic file formats. Extensible for PDF/DOCX.
    """
    if not os.path.exists(file_path):
        return ""

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext in (".txt", ".md", ".json", ".csv", ".xml"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    # Fallback / Binary format placeholder
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
