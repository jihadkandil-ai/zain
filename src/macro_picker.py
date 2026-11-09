"""LLM picks the single best Care macro id from ranked candidates."""

from __future__ import annotations

import json
import re
from typing import Any

from src.config import get_settings, has_api_key

_PICK_SYSTEM = """You are Zain's macro router for Tamara Voice Care.
Pick the ONE Care macro id that best matches the agent's messy notes.
Rules:
- Choose only from the provided candidates ids.
- Prefer exact customer intent (e.g. OTP not received vs explaining OTP requirement).
- Ignore weak keyword overlap (shared words like order/otp alone are not enough).
- Return JSON only: {"macro_id":"<id>","confidence":0.0to1.0,"reason":"short"}
- If none fit, return {"macro_id":"","confidence":0,"reason":"no match"}
"""


def pick_macro_id_with_llm(
    notes: str,
    candidates: list[dict[str, Any]],
) -> tuple[str | None, float]:
    """Return (macro_id, confidence) or (None, 0) if unavailable/unclear."""
    if not has_api_key() or not candidates:
        return None, 0.0

    from openai import OpenAI

    settings = get_settings()
    slim = [
        {
            "id": str(c.get("id") or ""),
            "title": str(c.get("title") or ""),
            "score": float(c.get("_match_score") or c.get("score") or 0),
            "when_to_use": str(c.get("when_to_use") or "")[:160],
        }
        for c in candidates
        if c.get("id")
    ][:12]
    if not slim:
        return None, 0.0

    client = OpenAI(
        api_key=settings.llm_proxy_api_key,
        base_url=settings.llm_proxy_base_url,
    )
    payload = {"agent_notes": (notes or "").strip(), "candidates": slim}
    try:
        resp = client.chat.completions.create(
            model=settings.llm_model,
            temperature=0,
            max_tokens=200,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _PICK_SYSTEM},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
        )
        raw = (resp.choices[0].message.content or "").strip()
        data = json.loads(raw) if raw else {}
    except Exception:  # noqa: BLE001 — fall back to retrieval
        return None, 0.0

    mid = str(data.get("macro_id") or "").strip()
    conf = float(data.get("confidence") or 0)
    allowed = {str(c["id"]) for c in slim}
    if not mid or mid not in allowed or conf < 0.45:
        return None, conf
    return mid, conf


def redact_light(notes: str) -> str:
    """Strip obvious emails/phones before sending notes to the picker."""
    text = notes or ""
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", "[email]", text)
    text = re.sub(r"\b(?:\+?\d[\d\s\-()]{7,}\d)\b", "[phone]", text)
    return text
