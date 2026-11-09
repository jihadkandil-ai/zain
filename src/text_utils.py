"""Small text helpers with no heavy dependencies."""

from __future__ import annotations

import re


def redact_light(notes: str) -> str:
    """Strip obvious emails/phones before sending notes to the LLM."""
    text = notes or ""
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", "[email]", text)
    text = re.sub(r"\b(?:\+?\d[\d\s\-()]{7,}\d)\b", "[phone]", text)
    return text
