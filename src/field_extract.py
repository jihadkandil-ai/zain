"""Extract only facts present in agent notes (EN / AR / mix). Never invent."""

from __future__ import annotations

import re
from src.text_utils import redact_light

_DATE_RE = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
    r"\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})\b",
    re.IGNORECASE,
)
_ARN_RE = re.compile(r"\b(?:arn[:\s]*)?([0-9]{10,30})\b", re.IGNORECASE)
_ORDER_RE = re.compile(
    r"\b(?:order|طلب)[:\s#]*([A-Z]{0,5}-?\d{5,}|TMP-?\d+)\b",
    re.IGNORECASE,
)


def extract_fields_regex(notes: str) -> dict[str, str]:
    text = notes or ""
    out: dict[str, str] = {}
    d = _DATE_RE.search(text)
    if d:
        out["date"] = d.group(1)
    o = _ORDER_RE.search(text)
    if o:
        out["order_id"] = o.group(1)
    a = _ARN_RE.search(text)
    if a and "arn" in text.lower():
        out["arn"] = a.group(1)
    # Amount only with explicit currency (avoid grabbing date parts like 05)
    m = re.search(
        r"\b(\d+(?:[.,]\d{1,2})?)\s*(?:sar|aed|usd|ر\.?س|ريال|درهم)\b",
        text,
        re.IGNORECASE,
    )
    if m:
        out["amount"] = m.group(1)
    return out


def extract_fields_with_llm(notes: str) -> dict[str, str]:
    """Optional LLM parse — returns only keys it is confident about from notes."""
    from src.config import get_settings, has_api_key

    if not has_api_key() or len((notes or "").strip()) < 3:
        return {}

    from openai import OpenAI
    import json

    settings = get_settings()
    client = OpenAI(
        api_key=settings.llm_proxy_api_key,
        base_url=settings.llm_proxy_base_url,
    )
    prompt = {
        "agent_notes": redact_light(notes),
        "extract_only_if_explicitly_present": [
            "date",
            "order_id",
            "arn",
            "amount",
            "customer_name",
        ],
        "rules": [
            "Return JSON object only.",
            "Use empty string when unknown.",
            "Never invent dates, ARNs, amounts, or names.",
            "Understand English, Arabic, and Arabizi mix.",
        ],
    }
    try:
        resp = client.chat.completions.create(
            model=settings.llm_model,
            temperature=0,
            max_tokens=200,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract only explicit facts from agent notes. "
                        "Never invent. JSON keys: date, order_id, arn, amount, customer_name."
                    ),
                },
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
        )
        raw = (resp.choices[0].message.content or "").strip()
        data = json.loads(raw) if raw else {}
    except Exception:  # noqa: BLE001
        return {}

    out: dict[str, str] = {}
    for key in ("date", "order_id", "arn", "amount", "customer_name"):
        val = str(data.get(key) or "").strip()
        if val and val.lower() not in {"unknown", "n/a", "none", "-", "null"}:
            out[key] = val
    return out


def extract_fields(notes: str) -> dict[str, str]:
    base = extract_fields_regex(notes)
    llm = extract_fields_with_llm(notes)
    # Prefer regex when both exist (less hallucination risk)
    merged = dict(llm)
    merged.update(base)
    return merged


def fill_care_placeholders(text: str, fields: dict[str, str], *, arabic: bool = False) -> str:
    """Substitute known placeholders only; leave unknown placeholders as-is."""
    out = text or ""
    name = fields.get("customer_name") or (
        "[اسم العميل]" if arabic else "[Customer name]"
    )
    out = out.replace("{customer_name}", name)
    out = out.replace("[Customer name]", name)
    out = out.replace("[اسم العميل]", name)
    date = fields.get("date")
    if date:
        out = re.sub(r"\[Insert date\]", date, out, flags=re.IGNORECASE)
        out = out.replace("[أدخل تاريخ]", date)
        out = out.replace("{date}", date)
    else:
        # Keep a clear agent-facing marker (no invented date)
        out = re.sub(r"\[Insert date\]", "[Insert date]", out, flags=re.IGNORECASE)
    arn = fields.get("arn")
    if arn:
        out = out.replace("{arn}", arn)
        out = out.replace("(ARN)", arn)
        out = out.replace("[ARN]", arn)
    amount = fields.get("amount")
    if amount:
        out = out.replace("{amount}", amount)
        out = out.replace("(المبلغ)", amount)
        out = out.replace("[المبلغ]", amount)
    order_id = fields.get("order_id")
    if order_id:
        out = out.replace("{order_id}", order_id)
        out = out.replace("{order_number}", order_id)
        out = out.replace("[order_id]", order_id)
    return out
