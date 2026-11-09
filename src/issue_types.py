"""Retrieve Salesforce Issue Category / Sub Category / Issue Type from agent notes."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "issue_types_kb.json"

# High-precision messy-note cues → issue type id (from issue_types_kb.json)
# Order matters: more specific first.
INTENT_ISSUE_TYPES: list[tuple[str, tuple[str, ...]]] = [
    (
        "payment_payment_methods_card_is_not_accepted",
        (
            "card not accepted",
            "card declined",
            "card related",
            "card problem",
            "card issue",
            "بطاقة مرفوضة",
            "مشكلة بطاقة",
            "البطاقة ما تشتغل",
            "البطاقه ما تشتغل",
        ),
    ),
    (
        "payment_postpone_payment",
        (
            "promise to pay",
            "promising to pay",
            "postpone payment",
            "postpone installment",
            "defer payment",
            "adjust payment plan",
            "change due date",
            "change payment date",
            "تأجيل دفعة",
            "تاجيل دفعه",
            "يأجل دفعه",
            "عايز يأجل",
            "وعد بالدفع",
            "يغير تاريخ الاستحقاق",
        ),
    ),
    (
        "payment_unable_to_pay_pending_dues",
        (
            "unable to pay pending dues",
            "not able to pay pending dues",
            "can't pay pending dues",
            "cannot pay pending dues",
            "unable to pay dues",
            "not able to pay dues",
            "pay now error",
            "pay now greyed",
            "ما أقدر أدفع",
            "ما قدرت ادفع",
        ),
    ),
]


@lru_cache(maxsize=1)
def _load_raw(mtime_ns: int) -> dict[str, Any]:
    del mtime_ns
    with KB_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_issue_types_kb() -> dict[str, Any]:
    return _load_raw(KB_PATH.stat().st_mtime_ns)


def list_issue_types() -> list[dict[str, Any]]:
    return list(load_issue_types_kb().get("issue_types") or [])


def _by_id() -> dict[str, dict[str, Any]]:
    return {str(i.get("id") or ""): i for i in list_issue_types()}


def _normalize(text: str) -> str:
    t = (text or "").strip().lower()
    t = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه")
    t = t.replace("'", "").replace("’", "").replace("`", "")
    t = re.sub(r"\bdidnt\b", "did not", t)
    t = re.sub(r"\s+", " ", t)
    return t


def _depth(path: str) -> int:
    return path.count(">") + 1 if path else 0


def _score_issue(notes_norm: str, item: dict[str, Any]) -> float:
    score = 0.0
    path = _normalize(str(item.get("path") or ""))
    use_case = _normalize(str(item.get("use_case") or ""))
    includes_list = [_normalize(x) for x in (item.get("includes") or []) if x]
    includes = " ".join(includes_list)
    keywords = [_normalize(k) for k in (item.get("keywords") or []) if k]

    for kw in keywords:
        if not kw:
            continue
        if kw in notes_norm:
            score += 6.0 if " " in kw or len(kw) >= 8 else 4.0
            continue
        # multi-word keyword: require most tokens present
        parts = [p for p in re.split(r"[^\w\u0600-\u06FF]+", kw) if len(p) > 2]
        if len(parts) >= 2 and sum(1 for p in parts if p in notes_norm) >= max(2, len(parts) - 1):
            score += 4.5

    for phrase in includes_list:
        parts = [p for p in re.split(r"[^\w\u0600-\u06FF]+", phrase) if len(p) > 3]
        if len(parts) >= 2:
            hit = sum(1 for p in parts if p in notes_norm)
            if hit >= max(2, len(parts) - 1):
                score += 3.0 + 0.4 * hit

    leaf = _normalize(str(item.get("issue_type") or ""))
    if leaf and leaf in notes_norm:
        score += 5.0
    else:
        leaf_parts = [p for p in re.split(r"[^\w\u0600-\u06FF]+", leaf) if len(p) > 3]
        if leaf_parts and all(p in notes_norm for p in leaf_parts):
            score += 4.0

    for tok in re.split(r"[^\w\u0600-\u06FF]+", path):
        if len(tok) > 4 and tok in notes_norm:
            score += 0.45

    blob = f"{use_case} {includes}"
    note_tokens = [t for t in re.split(r"[^\w\u0600-\u06FF]+", notes_norm) if len(t) > 3]
    hits = sum(1 for t in note_tokens if t in blob)
    score += min(hits * 0.4, 4.5)

    # Prefer more specific (L3) rows slightly over parent-only rows
    score += 0.35 * max(0, _depth(path) - 2)

    # Disambiguate OTP / order OTP vs generic login parent
    if "otp" in notes_norm:
        if "otp" in leaf or "otp" in path:
            score += 2.5
            if ("login" in notes_norm or "register" in notes_norm or "sign up" in notes_norm) and (
                "login" in path or "registration" in path
            ):
                score += 2.0
            if ("order" in notes_norm or "checkout" in notes_norm) and "placing an order" in path:
                score += 2.0
        elif path.endswith("registration & login") or leaf == "registration & login":
            score -= 2.0

    excludes = " ".join(_normalize(x) for x in (item.get("does_not_include") or []))
    if excludes:
        ex_hits = sum(1 for t in note_tokens if len(t) > 5 and t in excludes)
        if ex_hits and hits < 2:
            score -= 1.8

    return score


def _intent_issue_id(notes_norm: str) -> tuple[str, str] | None:
    """Return (issue_id, cue) for high-precision payment closures."""
    # Card-related failure while trying to pay dues → Card is not accepted
    cannot_pay = any(
        x in notes_norm
        for x in (
            "unable to pay",
            "not able to pay",
            "can't pay",
            "cannot pay",
            "ما اقدر ادفع",
            "ما قدرت ادفع",
            "pending dues",
            "dues",
            "مستحقات",
        )
    )
    cardish = any(
        x in notes_norm
        for x in (
            "card not accepted",
            "card declined",
            "card related",
            "card problem",
            "card issue",
            "بطاقة مرفوضة",
            "مشكلة بطاقة",
            "البطاقة ما تشتغل",
            "البطاقه ما تشتغل",
        )
    )
    if cannot_pay and cardish:
        return "payment_payment_methods_card_is_not_accepted", "unable_pay+card"

    # App / technical / payment-link workaround → Unable to pay pending dues
    technical = any(
        x in notes_norm
        for x in (
            "technical",
            "tech issue",
            "app issue",
            "app error",
            "application",
            "payment link",
            "pay link",
            "greyed",
            "timeout",
            "network",
            "مشكلة تقنية",
            "مشكلة بالتطبيق",
            "لينك دفع",
            "رابط دفع",
        )
    )
    if cannot_pay and (technical or "pending dues" in notes_norm or "مستحقات" in notes_norm):
        if not cardish:
            return "payment_unable_to_pay_pending_dues", "unable_pay+tech_or_dues"

    # Promise to pay / postpone / adjust plan
    for issue_id, cues in INTENT_ISSUE_TYPES:
        for cue in cues:
            cue_n = _normalize(cue)
            if cue_n and cue_n in notes_norm:
                # Don't let generic unable-to-pay beat card/tech rules above
                if issue_id == "payment_payment_methods_card_is_not_accepted" and not (
                    cannot_pay or "card" in notes_norm or "بطاق" in notes_norm
                ):
                    continue
                return issue_id, cue

    # Mixed AR postpone without exact cue string
    if any(x in notes_norm for x in ("ياجل", "تاجيل", "وعد بالدفع")) and any(
        x in notes_norm for x in ("دفع", "دفعه", "قسط", "استحقاق", "payment", "dues")
    ):
        return "payment_postpone_payment", "postpone_ar_mix"

    return None


def list_matching_issue_types(
    notes: str,
    *,
    min_score: float = 3.0,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Rank issue types for messy agent notes (intent first, then scoring)."""
    text = (notes or "").strip()
    if len(text) < 3:
        return []
    notes_norm = _normalize(text)
    ranked: list[tuple[float, int, dict[str, Any]]] = []
    seen: set[str] = set()

    intent = _intent_issue_id(notes_norm)
    if intent:
        issue_id, cue = intent
        item = _by_id().get(issue_id)
        if item:
            row = dict(item)
            row["_match_score"] = 100.0
            row["_match_reason"] = f"intent:{cue}"
            ranked.append((100.0, _depth(str(item.get("path") or "")), row))
            seen.add(issue_id)

    for item in list_issue_types():
        iid = str(item.get("id") or "")
        if iid in seen:
            continue
        score = _score_issue(notes_norm, item)
        # Prefer card over unable-to-pay when both score and notes mention card
        if (
            iid == "payment_unable_to_pay_pending_dues"
            and any(x in notes_norm for x in ("card", "بطاق"))
            and any(x in notes_norm for x in ("declined", "not accepted", "مرفوض", "مشكلة"))
        ):
            score -= 4.0
        # Prefer unable-to-pay over instore payment-link SMS when pending dues
        if "payment link" in notes_norm and "pending dues" in notes_norm:
            if "instore" in _normalize(str(item.get("path") or "")):
                score -= 5.0
            if iid == "payment_unable_to_pay_pending_dues":
                score += 4.0
        if score < min_score:
            continue
        row = dict(item)
        row["_match_score"] = round(score, 2)
        ranked.append((score, _depth(str(item.get("path") or "")), row))

    ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [row for _, _, row in ranked[:limit]]


def suggest_issue_type(notes: str) -> dict[str, Any] | None:
    hits = list_matching_issue_types(notes)
    return hits[0] if hits else None


def format_closure_suggestion(item: dict[str, Any] | None, notes: str = "") -> str:
    if not item:
        return (
            "Suggested Salesforce fields:\n\n"
            "• Issue Category: (no confident match — clarify notes)\n"
            "• Sub Category: —\n"
            "• Issue type: —\n"
            "• Interaction Type: Voice (confirm)\n"
            "• Tip: Focus on the primary reason for contact; ask TL if unsure."
        )
    return (
        "Suggested Salesforce fields (from [Customer] Issue Types KB):\n\n"
        f"• Issue Category (L1): {item.get('issue_category')}\n"
        f"• Sub Category (L2): {item.get('sub_category')}\n"
        f"• Issue type (L3): {item.get('issue_type')}\n"
        f"• Full path: {item.get('path')}\n"
        f"• Match score: {item.get('_match_score')}\n"
        "• Interaction Type: Voice (confirm in Salesforce)\n\n"
        f"Use case:\n{item.get('use_case')}\n"
    )
