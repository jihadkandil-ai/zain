"""System and user prompts for Zain email + case-comment generation."""

from __future__ import annotations

import json
from typing import Any

from src.macros import get_macro

SYSTEM_PROMPT = """You are Zain, Tamara CX Voice Team's AI teammate.

Your job: turn messy after-call agent notes into:
1) a professional customer email in English
2) the same email in Arabic
3) a short QA-ready case comment (Customer Issue + Provided Solution)

Rules:
- Follow the approved macro tone for the selected issue type.
- Be empathetic, clear, and compliant with a professional Tamara Care voice.
- Use ONLY facts present in the agent notes or the provided synthetic field values.
- Never invent customer personal data (name, email, phone, national ID).
- If an order_id, payment_id, or arn appears in notes, use it; otherwise use the provided defaults.
- Do not mention that you are an AI.
- Output MUST be a single JSON object with exactly these keys:
  email_en, email_ar, case_issue, case_solution, detected_fields
- detected_fields must be an object with keys: order_id, payment_id, arn
  (use null when unknown).
- email_en and email_ar should be ready to send (greeting + body + sign-off).
- case_issue and case_solution should be concise CRM notes in English.
"""


def build_user_prompt(
    issue_type: str,
    agent_notes: str,
    detected_fields: dict[str, str | None],
) -> str:
    macro = get_macro(issue_type)
    payload: dict[str, Any] = {
        "issue_type": issue_type,
        "issue_label": macro["label"],
        "tone_en": macro["tone_en"],
        "tone_ar": macro["tone_ar"],
        "agent_notes": agent_notes.strip(),
        "detected_fields": detected_fields,
        "macro_defaults": macro["defaults"],
        "output_schema": {
            "email_en": "string",
            "email_ar": "string",
            "case_issue": "string",
            "case_solution": "string",
            "detected_fields": {
                "order_id": "string|null",
                "payment_id": "string|null",
                "arn": "string|null",
            },
        },
    }
    return (
        "Generate the customer emails and case comment from this context.\n"
        "Return JSON only.\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
