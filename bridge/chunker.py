from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List


@dataclass
class Chunk:
    chunk_id: int
    text: str


def _split_paragraphs(text: str) -> List[str]:
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _split_sentences(text: str) -> List[str]:
    # Lightweight heuristic sentence splitter.
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    max_chars: int = 5000,
    overlap_chars: int = 500,
    preserve_paragraphs: bool = True,
) -> List[Chunk]:
    if not text or not text.strip():
        return []

    units = _split_paragraphs(text) if preserve_paragraphs else _split_sentences(text)
    if not units:
        units = [text.strip()]

    chunks: List[str] = []
    current = ""

    for unit in units:
        candidate = f"{current}\n\n{unit}".strip() if current else unit

        if len(candidate) <= max_chars:
            current = candidate
            continue

        # Flush current chunk first.
        if current:
            chunks.append(current)

        # If the incoming unit itself is too big, split by sentence.
        if len(unit) > max_chars:
            sentences = _split_sentences(unit)
            part = ""
            for s in sentences:
                c2 = f"{part} {s}".strip() if part else s
                if len(c2) <= max_chars:
                    part = c2
                else:
                    if part:
                        chunks.append(part)
                    part = s
            if part:
                current = part
            else:
                current = ""
        else:
            current = unit

    if current:
        chunks.append(current)

    # Apply character overlap as soft carry-over context.
    if overlap_chars > 0 and len(chunks) > 1:
        with_overlap: List[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap_chars:]
            merged = f"[OVERLAP_CONTEXT]\n{prev_tail}\n[/OVERLAP_CONTEXT]\n\n{chunks[i]}"
            with_overlap.append(merged)
        chunks = with_overlap

    return [Chunk(chunk_id=i + 1, text=c) for i, c in enumerate(chunks)]
