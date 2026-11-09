"""LLM drafts the Case Comment only — agent-style, facts from notes only."""

from __future__ import annotations

import json
from typing import Any

from src.config import get_settings, has_api_key
from src.text_utils import redact_light

_SYSTEM = """You are a Tamara Voice Care agent writing an internal Case Comment for the next agent/QA.
Rules:
- Use ONLY facts from the agent notes and the matched Care context provided.
- Never invent order IDs, dates, ARNs, amounts, or outcomes.
- If a detail is missing, write "Not provided" / leave blank — do not guess.
- Professional, concise English.
- Structure exactly:

CX Asks/Complaint:
<what the customer wanted / said>

Action Taken:
<what the agent did / what was matched / what was sent or advised>

Next Step (if any):
<optional short line, or "None">
"""


def draft_case_comment(
    notes: str,
    *,
    macro_title: str = "",
    issue_path: str = "",
    fields: dict[str, str] | None = None,
) -> str | None:
    if not has_api_key() or len((notes or "").strip()) < 3:
        return None

    from openai import OpenAI

    settings = get_settings()
    client = OpenAI(
        api_key=settings.llm_proxy_api_key,
        base_url=settings.llm_proxy_base_url,
    )
    payload = {
        "agent_notes": redact_light(notes),
        "matched_macro_title": macro_title,
        "suggested_issue_type_path": issue_path,
        "extracted_fields": fields or {},
    }
    try:
        resp = client.chat.completions.create(
            model=settings.llm_model,
            temperature=0.2,
            max_tokens=500,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
        )
        text = (resp.choices[0].message.content or "").strip()
    except Exception:  # noqa: BLE001
        return None

    if not text or "CX Asks" not in text:
        return None
    return text


def fallback_case_comment(notes: str, macro_title: str = "") -> str:
    return (
        "CX Asks/Complaint:\n"
        f"{(notes or '').strip() or 'Not provided'}\n\n"
        "Action Taken:\n"
        + (
            f"Matched Care macro `{macro_title}` and shared the approved Care email/talk track."
            if macro_title
            else "Reviewed notes; no Care macro matched."
        )
        + "\n\nNext Step (if any):\nNone"
    )
