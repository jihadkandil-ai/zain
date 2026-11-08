"""LLM generation via Tamara LLM Proxy, with structured parsing and template fallback."""

from __future__ import annotations

import json
import re
from typing import Any

from src.config import get_settings, has_api_key, provider_label
from src.macros import get_macro
from src.prompts import SYSTEM_PROMPT, build_user_prompt

REQUIRED_KEYS = ("email_en", "email_ar", "case_issue", "case_solution", "detected_fields")
FIELD_KEYS = ("order_id", "payment_id", "arn")

ORDER_RE = re.compile(r"\bTMP-[A-Z0-9]+\b", re.IGNORECASE)
PAYMENT_RE = re.compile(r"\bPAY-[A-Z0-9]+\b", re.IGNORECASE)
ARN_RE = re.compile(r"\bARN[-_]?[A-Z0-9]+\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s\-()]{7,}\d)(?!\w)")


def redact_pii(text: str) -> tuple[str, list[str]]:
    """Replace email/phone-like patterns so demos stay synthetic-safe."""
    flags: list[str] = []
    cleaned = text

    def _email(_match: re.Match[str]) -> str:
        flags.append("email")
        return "[REDACTED_EMAIL]"

    def _phone(_match: re.Match[str]) -> str:
        flags.append("phone")
        return "[REDACTED_PHONE]"

    cleaned = EMAIL_RE.sub(_email, cleaned)
    cleaned = PHONE_RE.sub(_phone, cleaned)
    return cleaned, sorted(set(flags))


def extract_fields(notes: str) -> dict[str, str | None]:
    order = ORDER_RE.search(notes)
    payment = PAYMENT_RE.search(notes)
    arn = ARN_RE.search(notes)
    return {
        "order_id": order.group(0).upper() if order else None,
        "payment_id": payment.group(0).upper() if payment else None,
        "arn": arn.group(0).upper() if arn else None,
    }


def _fill_template(template: str, fields: dict[str, str]) -> str:
    try:
        return template.format(**fields)
    except KeyError:
        return template


def fallback_result(issue_type: str, notes: str) -> dict[str, Any]:
    macro = get_macro(issue_type)
    detected = extract_fields(notes)
    fields = {
        key: (detected.get(key) or macro["defaults"][key]) for key in FIELD_KEYS
    }
    return {
        "email_en": _fill_template(macro["template_en"], fields),
        "email_ar": _fill_template(macro["template_ar"], fields),
        "case_issue": _fill_template(macro["case_issue_template"], fields),
        "case_solution": _fill_template(macro["case_solution_template"], fields),
        "detected_fields": {
            "order_id": detected.get("order_id"),
            "payment_id": detected.get("payment_id"),
            "arn": detected.get("arn"),
        },
        "source": "fallback_template",
        "redactions": [],
    }


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


def _normalize_result(raw: dict[str, Any], notes: str, source: str) -> dict[str, Any]:
    missing = [key for key in REQUIRED_KEYS if key not in raw]
    if missing:
        raise ValueError(f"Missing keys in model response: {missing}")

    detected_raw = raw.get("detected_fields") or {}
    if not isinstance(detected_raw, dict):
        detected_raw = {}

    extracted = extract_fields(notes)
    detected = {
        key: (detected_raw.get(key) or extracted.get(key) or None) for key in FIELD_KEYS
    }

    result = {
        "email_en": str(raw["email_en"]).strip(),
        "email_ar": str(raw["email_ar"]).strip(),
        "case_issue": str(raw["case_issue"]).strip(),
        "case_solution": str(raw["case_solution"]).strip(),
        "detected_fields": detected,
        "source": source,
        "redactions": [],
    }
    for key in ("email_en", "email_ar", "case_issue", "case_solution"):
        if not result[key]:
            raise ValueError(f"Empty value for {key}")
    return result


def generate_with_llm_proxy(issue_type: str, notes: str) -> dict[str, Any]:
    """Call Tamara LLM Proxy (OpenAI-compatible chat completions)."""
    from openai import OpenAI

    settings = get_settings()
    if not settings.llm_proxy_api_key:
        raise RuntimeError("LLM_PROXY_API_KEY is not set")

    client = OpenAI(
        api_key=settings.llm_proxy_api_key,
        base_url=settings.llm_proxy_base_url,
    )
    user_prompt = build_user_prompt(issue_type, notes, extract_fields(notes))
    response = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = response.choices[0].message.content or ""
    source = "llm_proxy" if "tamara" in settings.llm_proxy_base_url.lower() else "openai_compatible"
    return _normalize_result(_extract_json(text), notes, source)


def generate(issue_type: str, agent_notes: str) -> dict[str, Any]:
    """Generate emails + case notes; always returns a usable result."""
    get_macro(issue_type)  # validate early
    cleaned_notes, redactions = redact_pii(agent_notes)

    if has_api_key():
        try:
            result = generate_with_llm_proxy(issue_type, cleaned_notes)
            result["redactions"] = redactions
            result["provider"] = provider_label()
            return result
        except Exception as exc:  # noqa: BLE001 — demo must not blank
            result = fallback_result(issue_type, cleaned_notes)
            result["redactions"] = redactions
            result["error"] = str(exc)
            result["source"] = "fallback_template"
            return result

    result = fallback_result(issue_type, cleaned_notes)
    result["redactions"] = redactions
    result["warning"] = (
        "No LLM_PROXY_API_KEY set; used synthetic macro templates. "
        "Request a Tamara LLM Proxy virtual key via #it-helpdesk."
    )
    return result
