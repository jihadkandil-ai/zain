"""Tamara CX Knowledge Base — scenarios, macros, policies for Zain."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "tamara_knowledge_base.json"


def load_kb() -> dict[str, Any]:
    with KB_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_scenarios(kb: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = kb or load_kb()
    rows: list[dict[str, Any]] = []
    for topic_key, topic in (data.get("topics") or {}).items():
        for scenario in topic.get("scenarios") or []:
            row = dict(scenario)
            row["topic_key"] = topic_key
            row["topic"] = topic.get("topic")
            row["topic_meta"] = {
                "critical_security_rule": topic.get("critical_security_rule"),
                "primary_questions_rule": topic.get("primary_questions_rule"),
                "primary_questions": topic.get("primary_questions") or [],
                "secondary_questions": topic.get("secondary_questions") or [],
                "mandatory_evidence": topic.get("mandatory_evidence") or [],
            }
            rows.append(row)
    return rows


def match_scenario(notes: str) -> dict[str, Any] | None:
    """Return best-matching scenario from agent notes, or None if unclear."""
    text = (notes or "").strip().lower()
    if len(text) < 3:
        return None

    kb = load_kb()
    best: dict[str, Any] | None = None
    best_score = 0

    for scenario in iter_scenarios(kb):
        score = 0
        keyword_hits = 0
        title = (scenario.get("title") or "").lower()
        sid = (scenario.get("id") or "").lower()
        sid_spaced = sid.replace("_", " ")

        if sid and sid in text.replace(" ", "_"):
            score += 8
            keyword_hits += 1
        if title and title in text:
            score += 6
            keyword_hits += 1

        for kw in scenario.get("keywords") or []:
            key = kw.lower().strip()
            if not key:
                continue
            if key in text:
                # Longer / more specific phrases weigh more
                boost = 4 if " " in key or len(key) >= 12 else 3
                score += boost
                keyword_hits += 1

        # Soft topic hints only if we already have a keyword hit
        if keyword_hits:
            topic = (scenario.get("topic") or "").lower()
            for token in topic.replace("/", " ").replace("-", " ").split():
                if len(token) > 5 and token in text:
                    score += 1
            if "unrecognized" in text and "unrecognized" in (title + sid_spaced):
                score += 2
            if "partial" in text and "partial" in (title + sid_spaced):
                score += 3
            if "escalate" in text and (scenario.get("salesforce") or {}).get("escalate_to"):
                score += 1

        # Prefer more keyword hits on ties (more specific scenarios)
        if score > best_score or (
            score == best_score and score > 0 and keyword_hits > (best or {}).get("_hits", 0)
        ):
            best_score = score
            best = dict(scenario)
            best["_hits"] = keyword_hits

    # Require a real keyword/title hit so gibberish does not match
    if best is None or best_score < 3:
        return None
    return best


def _fraud_questions(kb: dict[str, Any], scenario: dict[str, Any]) -> list[str]:
    if scenario.get("use_mandatory_fraud_questions"):
        return list(kb.get("mandatory_fraud_questions") or [])
    return []


def build_macro_script(scenario: dict[str, Any], kb: dict[str, Any] | None = None) -> tuple[str, str]:
    """What to tell CX — EN + AR talk track from agent_action + policy prompts."""
    data = kb or load_kb()
    action = (scenario.get("agent_action") or "").strip()
    meta = scenario.get("topic_meta") or {}
    security = (meta.get("critical_security_rule") or "").strip()
    evidence = meta.get("mandatory_evidence") or []
    fraud_qs = _fraud_questions(data, scenario)

    en_parts = [
        "Hi,",
        "",
        "Thank you for contacting Tamara Care.",
        "",
        action,
    ]
    if fraud_qs:
        en_parts += ["", "I also need to ask a few security questions:", ""]
        en_parts += [f"{i}. {q}" for i, q in enumerate(fraud_qs, 1)]
    if evidence:
        en_parts += ["", "Please share the following evidence if you have not already:", ""]
        en_parts += [f"- {item}" for item in evidence]
    if security:
        en_parts += ["", f"(Agent note — security): {security}"]
    en_parts += ["", "Is there anything else I can help you with?", "", "Tamara Care Team"]

    ar_parts = [
        "هلا وسهلا،",
        "",
        "شكرًا لتواصلك مع رعاية تمارا.",
        "",
        "بناءً على حالتك، الخطوة الصحيحة هي كما يلي:",
        action,
    ]
    if fraud_qs:
        ar_parts += ["", "سأحتاج أيضًا أن أطرح عليك أسئلة أمنية مهمة:", ""]
        ar_parts += [f"{i}. {q}" for i, q in enumerate(fraud_qs, 1)]
    if evidence:
        ar_parts += ["", "يرجى تزويدنا بالمستندات التالية إن لم ترسلها بعد:", ""]
        ar_parts += [f"- {item}" for item in evidence]
    ar_parts += ["", "أي خدمة ثانية؟ حنا موجودين.", "", "فريق رعاية تمارا"]

    return "\n".join(en_parts), "\n".join(ar_parts)


def build_case_comment(notes: str, scenario: dict[str, Any]) -> str:
    sf = scenario.get("salesforce") or {}
    action = (scenario.get("agent_action") or "").strip()
    complaint = (notes or "").strip() or scenario.get("condition") or scenario.get("title")
    lines = [
        "CX Asks/Complaint:",
        complaint,
        "",
        "Action Taken:",
        action,
        f"Resolution type: {sf.get('case_comment_resolution_type') or '—'}",
    ]
    if sf.get("escalate_to"):
        lines.append(f"Escalated to: {sf['escalate_to']}")
    if sf.get("sla"):
        lines.append(f"SLA: {sf['sla']}")
    return "\n".join(lines)


def build_closure(scenario: dict[str, Any]) -> str:
    sf = scenario.get("salesforce") or {}
    lines = [
        "Suggested Salesforce fields:",
        "",
        f"• Status: {sf.get('status') or '—'}",
        f"• Interaction Type: Voice",
        f"• Issue Type: {sf.get('issue_type') or '—'}",
        f"• Case Comment / Resolution Type: {sf.get('case_comment_resolution_type') or '—'}",
        f"• Macro: {sf.get('macro') or '—'}",
    ]
    if sf.get("escalate_to"):
        lines.append(f"• Escalate To: {sf['escalate_to']}")
    if sf.get("sla"):
        lines.append(f"• SLA: {sf['sla']}")
    return "\n".join(lines)


def build_emails_from_scenario(scenario: dict[str, Any]) -> tuple[str, str]:
    """Compose bilingual customer emails from the approved agent action / policy."""
    action = (scenario.get("agent_action") or "").strip()
    title = (scenario.get("title") or "").strip()
    sf = scenario.get("salesforce") or {}

    en = (
        "Hi,\n"
        "Thank you for contacting Tamara Care.\n\n"
        f"Regarding your request ({title}):\n"
        f"{action}\n\n"
    )
    if sf.get("escalate_to"):
        en += (
            f"We have escalated your case to {sf['escalate_to']} "
            "for further handling"
        )
        if sf.get("sla"):
            en += f" (expected follow-up within {sf['sla']})"
        en += ".\n\n"
    en += (
        "If you need anything else, please reply to this email.\n\n"
        "Kind regards,\n"
        "Tamara Care Team"
    )

    ar = (
        "هلا وسهلا،\n"
        "شكرًا لتواصلك مع رعاية تمارا.\n\n"
        f"بخصوص طلبك ({title}):\n"
        f"{action}\n\n"
    )
    if sf.get("escalate_to"):
        ar += f"تم رفع حالتك إلى فريق {sf['escalate_to']} للمتابعة"
        if sf.get("sla"):
            ar += f" (خلال {sf['sla']})"
        ar += ".\n\n"
    ar += (
        "إذا احتجت أي مساعدة إضافية، يرجى الرد على هذا البريد.\n\n"
        "مع أطيب التحيات،\n"
        "فريق رعاية تمارا"
    )
    return en, ar


def resolve_email_template_id(scenario: dict[str, Any], kb: dict[str, Any] | None = None) -> str | None:
    data = kb or load_kb()
    macro = ((scenario.get("salesforce") or {}).get("macro") or "").strip()
    mapping = data.get("macro_to_email_id") or {}
    return mapping.get(macro)


def generate_from_notes(notes: str) -> dict[str, Any] | None:
    """Full four-pillar draft from KB scenario match. None if intent unclear."""
    scenario = match_scenario(notes)
    if not scenario:
        return None

    kb = load_kb()
    macro_en, macro_ar = build_macro_script(scenario, kb)
    email_en, email_ar = build_emails_from_scenario(scenario)
    email_template_id = resolve_email_template_id(scenario, kb)

    return {
        "source": "tamara_knowledge_base",
        "scenario_id": scenario.get("id"),
        "scenario_title": scenario.get("title"),
        "topic": scenario.get("topic"),
        "agent_action": (scenario.get("agent_action") or "").strip(),
        "macro_name": (scenario.get("salesforce") or {}).get("macro"),
        "macro_en": macro_en,
        "macro_ar": macro_ar,
        "case_comment": build_case_comment(notes, scenario),
        "email_en": email_en,
        "email_ar": email_ar,
        "email_template_id": email_template_id,
        "case_closure": build_closure(scenario),
        "salesforce": scenario.get("salesforce") or {},
    }
