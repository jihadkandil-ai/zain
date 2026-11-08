"""LLM-powered bilingual email drafting via Tamara LLM Proxy + KB grounding."""

from __future__ import annotations

import json
import re
from typing import Any

from src.config import get_settings, has_api_key, provider_label
from src.emails_db import get_email_by_id, load_emails_db, top_macro_candidates
from src.generator import redact_pii

MACRO_PICKER_PROMPT = """You are Zain, a Tamara Care macro (quicktext) router.

Pick the single best standardized email macro id for the agent's messy notes.
Return ONLY JSON: {"id":"<macro_id or null>","confidence":0..1,"reason":"short"}

Rules:
- Choose ONLY from the provided candidates list (use their id exactly).
- Prefer exact Care macros over inventing a new email.
- If none fit, return {"id":null,"confidence":0,"reason":"..."}.
- Understand Arabic dialect / Arabizi (شركاء=partners, مطالبة=claim/dispute, ريفاند=refund).
"""

EMAIL_SYSTEM_PROMPT = """You are Zain, Tamara CX Voice Care's AI teammate.

Your ONLY job: draft a customer email in English AND Arabic from messy agent notes.

Understand agent notes in ANY form:
- English, Modern Standard Arabic, Gulf dialect, Arabizi / Franco-Arabic
- Transliterations: ريفاند/ريفند = refund, ميل/ايميل = email, عميل/CX = customer,
  عايز/أبغى/ابي = want, ابعت/أرسل = send, استرداد/استرجاع = refund
- Typos and shorthand are normal. Infer the Care intent; do not refuse for language.

Rules:
- Follow Tamara Care tone: empathetic, clear, professional.
- If Knowledge Base context is provided, ground the email in that policy.
- Use ONLY facts from agent notes or KB. Never invent order IDs, amounts, ARNs,
  names, phones, or national IDs. Leave unknown fields blank / omit them.
- Do not mention that you are an AI.
- When the agent clearly wants a customer email (refund, evidence request, etc.),
  ALWAYS draft both email_en and email_ar — never return empty strings for clear intent.
- Output MUST be a single JSON object with exactly these keys:
  email_en, email_ar, matched_scenario_id, confidence
- email_en and email_ar must be ready-to-send (greeting + body + sign-off).
- matched_scenario_id: KB scenario id if applicable, else null.
- confidence: number from 0 to 1.
- Only return empty emails + confidence 0 if notes have NO actionable Care intent at all.
"""


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Model response is not a JSON object")
    return data


def _sample_email_refs(limit: int = 1) -> list[dict[str, str]]:
    """One short tone sample — keep prompt small for latency."""
    samples: list[dict[str, str]] = []
    for item in load_emails_db()[:limit]:
        samples.append(
            {
                "title": str(item.get("title") or item.get("id") or ""),
                "email_en": str(item.get("email_en") or "")[:350],
                "email_ar": str(item.get("email_ar") or "")[:350],
            }
        )
    return samples


# Dialect / Arabizi cues → English intent tokens for the model
_INTENT_CUES: tuple[tuple[str, str], ...] = (
    ("ريفاند", "refund"),
    ("ريفند", "refund"),
    ("استرداد", "refund"),
    ("استرجاع", "refund"),
    ("refund", "refund"),
    ("ميل", "email"),
    ("ايميل", "email"),
    ("إيميل", "email"),
    ("email", "email"),
    ("mail", "email"),
    ("عميل", "customer"),
    ("ابعت", "send"),
    ("أرسل", "send"),
    ("ارسل", "send"),
    ("عايز", "want"),
    ("أبغى", "want"),
    ("ابي", "want"),
    ("دليل", "evidence"),
    ("evidence", "evidence"),
)


def _has_arabic_script(text: str) -> bool:
    return any("\u0600" <= ch <= "\u06FF" for ch in text)


def augment_notes_for_llm(notes: str) -> str:
    """Append a short English intent hint so dialect/Arabizi notes draft reliably."""
    text = (notes or "").strip()
    if not text:
        return text
    lowered = text.lower()
    found: list[str] = []
    for cue, label in _INTENT_CUES:
        if cue in text or cue in lowered:
            if label not in found:
                found.append(label)
    if not found and not _has_arabic_script(text):
        return text
    if not found:
        found = ["customer email draft"]
    hint = (
        "[English intent hint for drafting: agent wants to "
        + " ".join(found)
        + " to the customer. Draft Tamara Care EN+AR emails.]"
    )
    return f"{text}\n\n{hint}"


def build_email_user_prompt(
    agent_notes: str,
    kb_context: dict[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "agent_notes": agent_notes.strip(),
        "task": "Draft bilingual customer emails (EN + AR) for this case.",
        "tone_samples": _sample_email_refs(),
        "output_schema": {
            "email_en": "string",
            "email_ar": "string",
            "matched_scenario_id": "string|null",
            "confidence": "number 0..1",
        },
    }
    if kb_context:
        payload["knowledge_base_match"] = {
            "scenario_id": kb_context.get("scenario_id"),
            "scenario_title": kb_context.get("scenario_title"),
            "topic": kb_context.get("topic"),
            "macro_name": kb_context.get("macro_name"),
            "agent_action_policy": kb_context.get("agent_action"),
            "case_policy": kb_context.get("salesforce"),
            "reference_email_en": (kb_context.get("email_en") or "")[:500],
            "reference_email_ar": (kb_context.get("email_ar") or "")[:500],
        }
    return (
        "Generate customer emails from this context.\n"
        "Return JSON only with non-empty email_en and email_ar.\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def _call_proxy(
    client: Any,
    model: str,
    user_content: str,
    *,
    use_json_format: bool,
) -> str:
    kwargs: dict[str, Any] = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "timeout": 45.0,
        "max_tokens": 1200,
    }
    if use_json_format:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def generate_emails_llm(
    agent_notes: str,
    kb_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call Tamara LLM Proxy for email_en + email_ar only."""
    from openai import OpenAI

    if not has_api_key():
        raise RuntimeError("LLM_PROXY_API_KEY is not set")

    settings = get_settings()
    cleaned_notes, redactions = redact_pii(agent_notes)
    augmented = augment_notes_for_llm(cleaned_notes)
    user_prompt = build_email_user_prompt(augmented, kb_context)

    client = OpenAI(
        api_key=settings.llm_proxy_api_key,
        base_url=settings.llm_proxy_base_url,
    )

    text = _call_proxy(client, settings.llm_model, user_prompt, use_json_format=True)
    raw: dict[str, Any] | None = None
    try:
        raw = _extract_json(text)
    except (json.JSONDecodeError, ValueError):
        raw = None

    email_en = str((raw or {}).get("email_en") or "").strip()
    email_ar = str((raw or {}).get("email_ar") or "").strip()

    # Retry once: dialect notes sometimes yield empty {} with json_object mode
    if not email_en and not email_ar:
        simple = (
            "Agent notes (may be Arabic dialect / Arabizi):\n"
            f"{augmented}\n\n"
            "Draft a Tamara Care customer email in English and Arabic about this request.\n"
            "Return ONLY JSON: "
            '{"email_en":"...","email_ar":"...","matched_scenario_id":null,"confidence":0.8}'
        )
        text = _call_proxy(client, settings.llm_model, simple, use_json_format=False)
        raw = _extract_json(text)
        email_en = str(raw.get("email_en") or "").strip()
        email_ar = str(raw.get("email_ar") or "").strip()

    confidence = (raw or {}).get("confidence")
    try:
        confidence_f = float(confidence) if confidence is not None else 0.0
    except (TypeError, ValueError):
        confidence_f = 0.0

    if not email_en and not email_ar:
        raise ValueError("LLM returned empty emails")

    return {
        "email_en": email_en,
        "email_ar": email_ar,
        "matched_scenario_id": (raw or {}).get("matched_scenario_id"),
        "confidence": confidence_f if confidence_f > 0 else 0.7,
        "source": "llm_proxy_email",
        "provider": provider_label(),
        "model": settings.llm_model,
        "redactions": redactions,
    }


def enrich_kb_result_with_llm_emails(
    notes: str,
    kb_result: dict[str, Any],
) -> dict[str, Any]:
    """Replace KB template emails with LLM drafts when proxy is available."""
    enriched = dict(kb_result)
    sf = kb_result.get("salesforce") or {}
    context = {
        **kb_result,
        "agent_action": kb_result.get("agent_action")
        or (kb_result.get("case_comment") or "").split("Action Taken:")[-1].strip(),
        "salesforce": sf,
    }
    llm = generate_emails_llm(notes, context)
    enriched["email_en"] = llm["email_en"]
    enriched["email_ar"] = llm["email_ar"]
    enriched["email_source"] = llm["source"]
    enriched["email_provider"] = llm.get("provider")
    enriched["email_model"] = llm.get("model")
    enriched["email_confidence"] = llm.get("confidence")
    enriched["redactions"] = llm.get("redactions") or []
    enriched["source"] = "tamara_knowledge_base+llm_email"
    return enriched


def generate_emails_from_notes_llm_only(notes: str) -> dict[str, Any] | None:
    """LLM-only email path — accept either language; do not keyword-gate."""
    llm = generate_emails_llm(notes, kb_context=None)
    if not llm.get("email_en") and not llm.get("email_ar"):
        return None

    template_id = None
    mid = llm.get("matched_scenario_id")
    if isinstance(mid, str) and mid:
        try:
            get_email_by_id(mid)
            template_id = mid
        except KeyError:
            template_id = None

    return {
        "source": "llm_email",
        "scenario_id": template_id or mid,
        "scenario_title": "LLM email draft",
        "topic": "Email Generation",
        "macro_en": "",
        "macro_ar": "",
        "case_comment": "",
        "email_en": llm["email_en"],
        "email_ar": llm["email_ar"],
        "case_closure": "",
        "email_source": llm["source"],
        "email_provider": llm.get("provider"),
        "email_model": llm.get("model"),
        "email_confidence": llm.get("confidence"),
        "redactions": llm.get("redactions") or [],
    }


def pick_macro_id_with_llm(notes: str) -> tuple[str | None, float]:
    """Ask the proxy to pick a macro id from ranked expanded-DB candidates."""
    from openai import OpenAI

    if not has_api_key():
        return None, 0.0

    candidates = top_macro_candidates(notes, limit=15)
    if not candidates:
        return None, 0.0

    settings = get_settings()
    cleaned, _ = redact_pii(notes)
    client = OpenAI(
        api_key=settings.llm_proxy_api_key,
        base_url=settings.llm_proxy_base_url,
    )
    user = json.dumps(
        {"agent_notes": cleaned, "candidates": candidates},
        ensure_ascii=False,
    )
    resp = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": MACRO_PICKER_PROMPT},
            {"role": "user", "content": user},
        ],
        timeout=35.0,
        max_tokens=200,
    )
    raw = _extract_json(resp.choices[0].message.content or "")
    mid = raw.get("id")
    try:
        conf = float(raw.get("confidence") or 0)
    except (TypeError, ValueError):
        conf = 0.0
    if not isinstance(mid, str) or not mid.strip():
        return None, conf
    allowed = {str(c["id"]) for c in candidates}
    if mid not in allowed:
        return None, conf
    return mid, conf

