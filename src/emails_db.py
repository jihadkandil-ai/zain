"""Load Tamara email macros (quicktext) and retrieve the best standardized template."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EMAILS_DB_EXPANDED_PATH = ROOT / "data" / "emails_db_expanded.json"

# High-precision Arabic/English intent → Salesforce macro id in expanded DB
# More specific intents MUST come first.
INTENT_MACROS: list[tuple[str, tuple[str, ...]]] = [
    (
        # Care quicktext for OTP SMS not arriving (login / registration / checkout)
        "574Sg0000007OqQIAU",  # MFA - OTP Not Received
        (
            "didn't receive login otp",
            "didnt receive login otp",
            "didn't receive otp",
            "didnt receive otp",
            "otp not received",
            "not receiving otp",
            "not receive otp",
            "login otp",
            "registration otp",
            "otp login",
            "otp sms",
            "لم يصل otp",
            "ما وصل otp",
            "ما يوصل otp",
            "ما يجيني otp",
            "رمز التحقق ما وصل",
            "ما وصل رمز",
        ),
    ),
    (
        "574Sg0000004gtHIAQ",  # Promise to Pay Reject (no postpone / due-date change)
        (
            "promise to pay",
            "promise-to-pay",
            "postpone payment",
            "postpone the payment",
            "postpone installment",
            "postpone due date",
            "defer payment",
            "delay payment",
            "change due date",
            "change payment date",
            "adjust payment plan",
            "change payment plan",
            "reschedule payment",
            "extend payment",
            "يأجل دفعه",
            "يأجل الدفعة",
            "عايز يأجل",
            "عايزه تأجل",
            "يبغي يأجل",
            "تأجيل دفعه",
            "تأجيل الدفعة",
            "تأجيل الدفع",
            "تأجيل قسط",
            "تعديل خطة الدفع",
            "تغيير خطة الدفع",
            "تغيير تاريخ الاستحقاق",
            "يغير تاريخ الاستحقاق",
            "يغيّر تاريخ الاستحقاق",
            "تغيير موعد الدفع",
            "يغير موعد الدفع",
            "وعد بالدفع",
        ),
    ),
    (
        "574Sg0000004gxYIAQ",  # Late Fee Removal Decline (charged / wants waiver)
        (
            "late fee charged",
            "late fees charged",
            "late fee waiver",
            "waive late fee",
            "waive the late fee",
            "remove late fee",
            "late fee removal",
            "رسوم تأخير",
            "رسوم التأخير",
            "اعفاء رسوم التأخير",
            "إعفاء رسوم التأخير",
            "يلغي رسوم التأخير",
        ),
    ),
    (
        "574Sg0000004gzBIAQ",  # Ask for more evidence - Item not as Described
        (
            "item damaged",
            "damaged item",
            "not as described",
            "not as describe",
            "item not as described",
            "wrong item",
            "counterfeit",
            "تالف",
            "مو زي الوصف",
            "مش زي الوصف",
            "غير مطابق",
            "منتج تالف",
            "الخامة غلط",
        ),
    ),
    (
        "574Sg0000004gsCIAQ",  # Wants to Return/cancel the order
        (
            "cx want to cancel",
            "want to cancel",
            "wants to cancel",
            "cancel order",
            "cancel the order",
            "return/cancel",
            "return cancel",
            "wants to return",
            "want to return",
            "cancelation",
            "cancellation",
            "يلغي",
            "يلغي او يكنسل",
            "يكنسل",
            "كنسل طلب",
            "الغاء طلب",
            "إلغاء طلب",
            "عايز يلغي",
            "عايز يكنسل",
            "يبغي يلغي",
            "ارجاع الطلب",
            "return the order",
        ),
    ),
    (
        "574Sg0000004gseIAA",  # Dispute steps
        (
            "dispute steps",
            "dispute step",
            "claim steps",
            "claim step",
            "raise a claim",
            "how to claim",
            "how to dispute",
            "رفع مطالبة",
            "خطوات المطالبة",
            "مشترياتي",
            "تواصل مع دعم تمارا",
            "get help from tamara",
            "72 ساعة",
            "بعد مرور 72",
        ),
    ),
    (
        # Successful CKO refund (amount/date/ARN already processed)
        "574Sg0000004gsfIAA",
        (
            "successful cko refund",
            "refund processed",
            "refunded on",
            "refund arn",
            "share arn",
            "reference number (arn)",
            "حقك محفوظ",
            "تم استرداد",
            "استرداد المبلغ",
            "رقم مرجعي",
            "نفس البطاقة",
        ),
    ),
    (
        # Waiting / within SLA refund follow-up
        "574Sg0000004h2xIAA",
        (
            "successful refund - within sla",
            "within sla",
            "refund status",
            "track your refund",
            "requested a refund",
            "refund follow",
            "waiting refund",
            "refund mail",
            "send refund",
            "refund",
            "ريفاند",
            "ريفند",
            "استرجاع",
            "استرداد",
            "حالة الإسترجاع",
            "لاحظنا إنك طلبت استرجاع",
        ),
    ),
]

# Exclude merchant / Partner Care / Refund-block macros from Voice CX matching
_EXCLUDED_TITLE_NEEDLES = (
    "who are your partners",
    "partner portal",
    "partner store",
    "partner care",
    "[merchant]",
    "merchant]",
    "channel partners",
    "[refund block]",
    "refund block",
    "شركاء",
)
_EXCLUDED_BODY_NEEDLES = (
    "partner care team",
    "dear partner",
    "dear valued partner",
    "dear valued partner",
    "فريق رعاية الشركاء",
    "partner.care@tamara.co",
)
_EXCLUDED_IDS = {
    "574Sg0000004gvGIAQ",  # Request to cancel - Retention (Partner Care)
    "574Sg0000004gsTIAQ",  # Who are your partners?
    "574Sg0000004gpRIAQ",  # [Refund block] - Refund processed
    "574Sg0000004h2rIAA",  # [Refund block] - Refund processed (dup)
    "574Sg0000004gpNIAQ",  # [Refund block] - Sama case refund processed
}


def _db_path() -> Path:
    if not EMAILS_DB_EXPANDED_PATH.exists():
        raise FileNotFoundError(f"Missing macros DB: {EMAILS_DB_EXPANDED_PATH}")
    return EMAILS_DB_EXPANDED_PATH


@lru_cache(maxsize=1)
def _load_raw(mtime_ns: int) -> list[dict[str, Any]]:
    del mtime_ns  # cache key only
    path = _db_path()
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    emails = payload.get("emails") or []
    if not isinstance(emails, list):
        raise ValueError(f"{path.name}: 'emails' must be a list")
    return emails


def _is_excluded_macro(item: dict[str, Any]) -> bool:
    eid = str(item.get("id") or "")
    if eid in _EXCLUDED_IDS:
        return True
    title = _normalize(str(item.get("title") or ""))
    if any(needle in title for needle in _EXCLUDED_TITLE_NEEDLES):
        return True
    en = _normalize(str(item.get("email_en") or ""))
    ar = str(item.get("email_ar") or "")
    blob = f"{en} {ar}"
    return any(needle in blob.lower() or needle in en for needle in _EXCLUDED_BODY_NEEDLES)


def load_emails_db() -> list[dict[str, Any]]:
    """Load macros DB (prefers emails_db_expanded.json). Cache busts on file mtime."""
    path = _db_path()
    return [item for item in _load_raw(path.stat().st_mtime_ns) if not _is_excluded_macro(item)]


def list_email_options() -> list[tuple[str, str]]:
    return [(item["id"], item["title"]) for item in load_emails_db()]


def get_email_by_id(email_id: str) -> dict[str, Any]:
    for item in load_emails_db():
        if item.get("id") == email_id:
            return item
    raise KeyError(f"Unknown email template id: {email_id}")


def _normalize(text: str) -> str:
    t = (text or "").strip().lower()
    t = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه")
    t = t.replace("'", "").replace("’", "").replace("`", "")
    # Light stemming so "didn't receive" overlaps "not received"
    t = re.sub(r"\breceived\b", "receive", t)
    t = re.sub(r"\bdidnt\b", "did not", t)
    t = re.sub(r"\s+", " ", t)
    return t


# Related Care macros to offer together when any one of the family matches
_MACRO_FAMILIES: tuple[frozenset[str], ...] = (
    frozenset(
        {
            "574Sg0000004gsfIAA",  # Successful CKO refund
            "574Sg0000004ge8IAA",  # Successful CKO refund (alt format)
            "574Sg0000004h2xIAA",  # Successful refund - within SLA
        }
    ),
    frozenset(
        {
            "574Sg0000007OqQIAU",  # MFA - OTP Not Received
            "574Sg0000007OqPIAU",  # MFA - OTP Requirement
            "574Sg0000007OyTIAU",  # MFA - Retry Checkout
        }
    ),
)


def _intent_macro_ids(notes: str) -> list[tuple[str, str]]:
    """Return all intent macro ids that match notes (id, cue)."""
    from src.debug_trace import zain_debug

    text = _normalize(notes)
    hits: list[tuple[str, str]] = []
    seen: set[str] = set()
    for macro_id, cues in INTENT_MACROS:
        for cue in cues:
            cue_n = _normalize(cue)
            if cue_n and cue_n in text and macro_id not in seen:
                hits.append((macro_id, cue))
                seen.add(macro_id)
                zain_debug("intent_alias_hit", cue=cue, macro_id=macro_id, notes=notes)
                break

    # Non-contiguous OTP miss: "didn't receive … order … otp"
    otp_id = "574Sg0000007OqQIAU"
    if otp_id not in seen and "otp" in text:
        missed = any(
            x in text
            for x in (
                "not receive",
                "did not receive",
                "didnt receive",
                "لم يصل",
                "ما وصل",
                "ما يوصل",
                "ما يجيني",
            )
        )
        if missed:
            hits.insert(0, (otp_id, "otp+not_receive"))
            seen.add(otp_id)
            zain_debug("intent_alias_hit", cue="otp+not_receive", macro_id=otp_id, notes=notes)

    # Late fee + waiver/remove even if words are split
    late_id = "574Sg0000004gxYIAQ"
    if late_id not in seen and ("late fee" in text or "late fees" in text or "رسوم تأخير" in text or "رسوم التأخير" in text):
        wants_help = any(
            x in text
            for x in ("waiver", "waive", "remove", "charged", "اعفاء", "إعفاء", "يلغي", "اشيل")
        )
        if wants_help:
            hits.insert(0, (late_id, "late_fee+waiver"))
            seen.add(late_id)
            zain_debug("intent_alias_hit", cue="late_fee+waiver", macro_id=late_id, notes=notes)

    # Damaged / not-as-described even with typos ("describe")
    item_id = "574Sg0000004gzBIAQ"
    if item_id not in seen:
        damaged = any(x in text for x in ("damaged", "damage", "تالف", "مكسور"))
        nas = any(
            x in text
            for x in (
                "not as described",
                "not as describe",
                "item not as",
                "مو زي الوصف",
                "مش زي الوصف",
                "غير مطابق",
            )
        )
        if damaged or nas:
            hits.insert(0, (item_id, "item_not_as_described"))
            seen.add(item_id)
            zain_debug(
                "intent_alias_hit",
                cue="item_not_as_described",
                macro_id=item_id,
                notes=notes,
            )

    # Postpone / PTP / adjust plan even when phrasing is mixed EN+AR
    ptp_id = "574Sg0000004gtHIAQ"
    if ptp_id not in seen:
        postpone = any(
            x in text
            for x in (
                "postpone",
                "defer",
                "reschedule",
                "promise to pay",
                "ptp",
                "يأجل",
                "تأجيل",
                "تاجيل",
            )
        )
        paymentish = any(
            x in text
            for x in (
                "payment",
                "installment",
                "due date",
                "payment plan",
                "دفع",
                "دفعه",
                "دفعة",
                "قسط",
                "استحقاق",
                "خطة الدفع",
            )
        )
        adjust_plan = any(
            x in text
            for x in (
                "adjust payment plan",
                "change payment plan",
                "change due date",
                "تعديل خطة الدفع",
                "تغيير خطة الدفع",
                "يغير تاريخ",
                "يغيّر تاريخ",
                "يغير موعد",
                "تغيير تاريخ الاستحقاق",
            )
        )
        if adjust_plan or (postpone and paymentish):
            hits.insert(0, (ptp_id, "postpone_or_ptp"))
            seen.add(ptp_id)
            zain_debug(
                "intent_alias_hit",
                cue="postpone_or_ptp",
                macro_id=ptp_id,
                notes=notes,
            )

    if not hits:
        zain_debug("intent_alias_miss", notes=notes)
    return hits


def _intent_macro_id(notes: str) -> str | None:
    hits = _intent_macro_ids(notes)
    return hits[0][0] if hits else None


def _expand_families(ids: set[str]) -> set[str]:
    out = set(ids)
    for family in _MACRO_FAMILIES:
        if out & family:
            out |= set(family)
    return out


def _score_template(notes_norm: str, item: dict[str, Any]) -> float:
    title = _normalize(str(item.get("title") or ""))
    when = _normalize(str(item.get("when_to_use") or ""))
    body = _normalize(
        f"{item.get('email_en') or ''} {item.get('email_ar') or ''}"
    )[:1200]
    score = 0.0
    if title and title in notes_norm:
        score += 12.0
    # token overlap on title
    title_tokens = [tok for tok in re.split(r"[^\w\u0600-\u06FF]+", title) if len(tok) > 2]
    note_tokens = set(re.split(r"[^\w\u0600-\u06FF]+", notes_norm))
    hits = sum(1 for tok in title_tokens if tok in note_tokens)
    if title_tokens:
        score += 6.0 * (hits / len(title_tokens))
    for tok in title_tokens:
        if len(tok) >= 4 and tok in notes_norm:
            score += 1.5
    if when:
        when_tokens = [tok for tok in re.split(r"[^\w\u0600-\u06FF]+", when) if len(tok) > 3]
        score += sum(0.4 for tok in when_tokens if tok in notes_norm)
    # OTP not-received: notes rarely include the full Care title "MFA - OTP Not Received"
    if "otp" in notes_norm and "otp" in title:
        score += 2.0
        if any(x in notes_norm for x in ("not receive", "did not receive", "لم يصل", "ما وصل")):
            if "not receive" in title or "otp not receive" in title:
                score += 5.0
    # light body cue
    for cue in ("partner", "شركاء", "dispute", "مطالب", "refund", "استرداد", "stores"):
        if cue in notes_norm and cue in body:
            score += 0.8

    # Require multi-signal overlap — one shared word (e.g. "order") is not enough
    if hits <= 1 and score < 8.0:
        score *= 0.45
    return score


def retrieve_macro(notes: str, *, min_score: float = 4.0) -> dict[str, Any] | None:
    """Return best standardized macro for agent notes, or None if unclear."""
    from src.debug_trace import zain_debug

    text = (notes or "").strip()
    zain_debug("retrieve_macro_start", notes=text, db_path=str(_db_path()))
    if len(text) < 3:
        zain_debug("retrieve_macro_skip_short_notes")
        return None

    intent_id = _intent_macro_id(text)
    if intent_id:
        try:
            item = dict(get_email_by_id(intent_id))
            item["_match_score"] = 100.0
            item["_match_reason"] = "intent_alias"
            zain_debug(
                "retrieve_macro_intent",
                id=item.get("id"),
                title=item.get("title"),
                en_start=(item.get("email_en") or "")[:120],
                ar_start=(item.get("email_ar") or "")[:120],
            )
            return item
        except KeyError as exc:
            zain_debug("retrieve_macro_intent_missing_id", id=intent_id, error=exc)

    notes_norm = _normalize(text)
    best: dict[str, Any] | None = None
    best_score = 0.0
    top3: list[tuple[float, str, str]] = []
    for item in load_emails_db():
        score = _score_template(notes_norm, item)
        top3.append((score, str(item.get("id")), str(item.get("title"))))
        if score > best_score:
            best_score = score
            best = dict(item)
            best["_match_score"] = score
            best["_match_reason"] = "title_overlap"

    top3.sort(reverse=True)
    zain_debug(
        "retrieve_macro_scoreboard",
        top3="; ".join(f"{s:.1f}:{tid}:{title}" for s, tid, title in top3[:5]),
    )

    if best is None or best_score < min_score:
        zain_debug("retrieve_macro_no_match", best_score=best_score, min_score=min_score)
        return None
    zain_debug(
        "retrieve_macro_title_overlap",
        id=best.get("id"),
        title=best.get("title"),
        score=best_score,
        en_start=(best.get("email_en") or "")[:120],
    )
    return best


def suggest_email_id(notes: str) -> str | None:
    """Backward-compatible helper — returns expanded (or legacy) macro id."""
    hit = retrieve_macro(notes)
    return str(hit["id"]) if hit else None


def top_macro_candidates(notes: str, limit: int = 12) -> list[dict[str, Any]]:
    """Ranked candidates for LLM picker when intent is ambiguous."""
    notes_norm = _normalize(notes)
    ranked: list[tuple[float, dict[str, Any]]] = []
    for item in load_emails_db():
        score = _score_template(notes_norm, item)
        if score <= 0:
            continue
        row = {
            "id": item.get("id"),
            "title": item.get("title"),
            "score": round(score, 2),
            "when_to_use": (item.get("when_to_use") or "")[:160],
        }
        ranked.append((score, row))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [row for _, row in ranked[:limit]]


def list_matching_macros(
    notes: str,
    *,
    min_score: float = 6.5,
    limit: int = 8,
    expand_families: bool = False,
) -> list[dict[str, Any]]:
    """Return ranked Care macros. Prefer intent hits; keep title matches strict."""
    from src.debug_trace import zain_debug

    text = (notes or "").strip()
    zain_debug("list_matching_macros_start", notes=text)
    if len(text) < 3:
        return []

    by_id: dict[str, dict[str, Any]] = {}

    # 1) Intent aliases (primary)
    for macro_id, cue in _intent_macro_ids(text):
        try:
            item = dict(get_email_by_id(macro_id))
        except KeyError:
            continue
        if _is_excluded_macro(item):
            continue
        item["_match_score"] = 100.0
        item["_match_reason"] = f"intent_alias:{cue}"
        by_id[macro_id] = item

    # 2) Optional family expand (refund formats / related MFA) — off by default
    if expand_families:
        for mid in list(_expand_families(set(by_id))):
            if mid in by_id:
                continue
            try:
                item = dict(get_email_by_id(mid))
            except KeyError:
                continue
            if _is_excluded_macro(item):
                continue
            item["_match_score"] = 90.0
            item["_match_reason"] = "family_expand"
            by_id[mid] = item

    # 3) Title/score pool for LLM / fallback (always collect a short shortlist)
    notes_norm = _normalize(text)
    scored: list[tuple[float, dict[str, Any]]] = []
    for item in load_emails_db():
        mid = str(item.get("id") or "")
        if mid in by_id:
            continue
        score = _score_template(notes_norm, item)
        if score < min_score:
            continue
        row = dict(item)
        row["_match_score"] = score
        row["_match_reason"] = "title_overlap"
        scored.append((score, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    for score, row in scored[:limit]:
        mid = str(row.get("id") or "")
        if mid and mid not in by_id:
            by_id[mid] = row

    results = sorted(
        by_id.values(),
        key=lambda r: float(r.get("_match_score") or 0),
        reverse=True,
    )[:limit]

    zain_debug(
        "list_matching_macros_result",
        count=len(results),
        titles="; ".join(
            f"{r.get('_match_score')}:{r.get('id')}:{r.get('title')}" for r in results
        ),
    )
    return results


def resolve_exact_macro(notes: str) -> dict[str, Any] | None:
    """Retrieval shortlist → LLM picks one exact Care macro (fallback: top score)."""
    from src.debug_trace import zain_debug
    from src.macro_picker import pick_macro_id_with_llm, redact_light

    matches = list_matching_macros(notes, limit=10)
    if not matches:
        return None

    # Strong unique intent → trust it without LLM noise
    top = matches[0]
    reason = str(top.get("_match_reason") or "")
    if reason.startswith("intent_alias") and float(top.get("_match_score") or 0) >= 100:
        if len(matches) == 1 or float(matches[1].get("_match_score") or 0) < 80:
            top = dict(top)
            top["_match_reason"] = reason + "+exact"
            zain_debug("resolve_exact_intent", id=top.get("id"), title=top.get("title"))
            return top

    cleaned = redact_light(notes)
    picked_id, conf = pick_macro_id_with_llm(cleaned, matches)
    if picked_id:
        for item in matches:
            if str(item.get("id")) == picked_id:
                row = dict(item)
                row["_match_score"] = max(float(item.get("_match_score") or 0), 95.0)
                row["_match_reason"] = f"llm_pick:{conf:.2f}"
                zain_debug(
                    "resolve_exact_llm",
                    id=row.get("id"),
                    title=row.get("title"),
                    confidence=conf,
                )
                return row

    # Fallback: single best retrieval hit only
    best = dict(matches[0])
    best["_match_reason"] = str(best.get("_match_reason") or "top_score") + "+fallback"
    zain_debug("resolve_exact_fallback", id=best.get("id"), title=best.get("title"))
    return best


def resolve_standardized_macro(notes: str) -> dict[str, Any] | None:
    """Best single match (first of list_matching_macros)."""
    from src.debug_trace import zain_debug

    matches = list_matching_macros(notes)
    if not matches:
        zain_debug("resolve_no_match")
        return None
    hit = matches[0]
    zain_debug(
        "resolve_final",
        source="list_matching_macros",
        reason=hit.get("_match_reason"),
        id=hit.get("id"),
        title=hit.get("title"),
        alternatives=len(matches),
        file=str(_db_path().name),
    )
    return hit
