"""Wrap matched Care macro bodies in a fixed Tamara email shell (no free rewrite)."""

from __future__ import annotations

import re

CUSTOMER_NAME_PLACEHOLDER = "[Customer name]"
CUSTOMER_NAME_PLACEHOLDER_AR = "[اسم العميل]"

# Strip existing greetings / closings so we don't double them in the shell
_EN_GREETING = re.compile(
    r"^(?:hi|hello|dear|dear valued partner|dear partner)"
    r"[^\n,]*,?\s*(?:\{[^}]+\}|\[[^\]]+\]|[A-Za-z ]+)?\s*[,!]?\s*",
    re.IGNORECASE,
)
_AR_GREETING = re.compile(
    r"^(?:هلا وسهلا|أهلا وسهلا|اهلا وسهلا|مرحبا|مرحبًا|عزيزي|عزيزتي|شريكنا العزيز|شريك تمارا العزيز)"
    r"[^\n،]*,?\s*(?:\{[^}]+\}|\([^)]+\)|\[[^\]]+\])?\s*[،,]?\s*",
    re.IGNORECASE,
)
_EN_THANKS = re.compile(
    r"^(?:thanks|thank you)(?:\s+for\s+contacting\s+tamara)?[!.]?\s*",
    re.IGNORECASE,
)
_AR_THANKS = re.compile(
    r"^(?:شكرًا|شكرا)(?:ً)?\s+لتواصل(?:كم|ك)\s+مع\s+تمارا[!.]?\s*",
    re.IGNORECASE,
)
_EN_CLOSING = re.compile(
    r"(?:if you have any (?:other |further )?inquir(?:y|ies)|have a wonderful day|"
    r"we(?:'re| are) happy to (?:help|serve)|best regards|kind regards|"
    r"tamara care team|warm regards).*$",
    re.IGNORECASE | re.DOTALL,
)
_AR_CLOSING = re.compile(
    r"(?:أي خدمة ثانية|اذا عندك أي استفسار|إذا عندك أي استفسار|سعيدين بخدمتك|"
    r"مع أطيب|فريق رعاية تمارا|فريق دعم تمارا|حنا موجودين).*$",
    re.IGNORECASE | re.DOTALL,
)

_PROBLEM_CUES = (
    "problem",
    "issue",
    "angry",
    "complaint",
    "dispute",
    "refund",
    "delay",
    "not received",
    "failed",
    "error",
    "مشكلة",
    "اشكالية",
    "إشكالية",
    "شكوى",
    "غاضب",
    "مطالب",
    "نزاع",
    "استرداد",
    "استرجاع",
    "ريفاند",
    "ما وصل",
    "لم يصل",
    "تأخير",
)


def needs_apology(notes: str) -> bool:
    text = (notes or "").lower()
    return any(cue in text for cue in _PROBLEM_CUES)


def _strip_shell(text: str, *, arabic: bool) -> str:
    body = (text or "").strip()
    if not body:
        return ""
    # Normalize odd separators
    body = body.replace("\r\n", "\n").strip()
    for _ in range(3):
        prev = body
        if arabic:
            body = _AR_GREETING.sub("", body, count=1).strip()
            body = _AR_THANKS.sub("", body, count=1).strip()
        else:
            body = _EN_GREETING.sub("", body, count=1).strip()
            body = _EN_THANKS.sub("", body, count=1).strip()
        # Drop leftover leading punctuation/spaces
        body = re.sub(r"^[\s,،.]+", "", body)
        if body == prev:
            break
    if arabic:
        body = _AR_CLOSING.sub("", body).strip()
    else:
        body = _EN_CLOSING.sub("", body).strip()
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body


def _polish_english_body(body: str) -> str:
    text = (body or "").replace("\r\n", "\n").strip()
    if not text:
        return ""
    text = text.replace('""', '"')
    # Numbered steps each on their own line
    text = re.sub(r"(?<!\n)\s*(\d+)\s*[\.\-–—]\s+", r"\n\1. ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _polish_arabic_body(body: str) -> str:
    """Make dense Arabic Care copy readable + copy-ready (lists, spacing)."""
    text = (body or "").replace("\r\n", "\n").strip()
    if not text:
        return ""

    text = text.replace('""', '"').replace("''", "'")
    text = text.replace("{customer_name}", CUSTOMER_NAME_PLACEHOLDER_AR)
    text = text.replace("[Customer name]", CUSTOMER_NAME_PLACEHOLDER_AR)

    # Section headers on their own line + blank line before steps
    text = re.sub(r"\s*(الطريقة)\s*[:：]\s*", r"\n\n\1:\n\n", text)
    text = re.sub(r"\s*(الخطوات)\s*[:：]\s*", r"\n\n\1:\n\n", text)
    # Ensure blank line between "الطريقة:" and first step if missing
    text = re.sub(r"(الطريقة:)\n([١٢٣٤٥٦٧٨٩٠1-9])", r"\1\n\n\2", text)

    # Arabic-Indic or Western step numbers → each on a new line
    text = re.sub(
        r"(?<!\n)\s*([١٢٣٤٥٦٧٨٩٠]+)\s*[ـ\-–—\.]\s*",
        r"\n\1 ـ ",
        text,
    )
    text = re.sub(r"(?<!\n)\s*(\d+)\s*[\.\-–—]\s+", r"\n\1. ", text)

    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim spaces around lines
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text.strip()


def standardize_email_en(matched_en: str, *, apologize: bool) -> str:
    body = _polish_english_body(_strip_shell(matched_en, arabic=False))
    parts = [
        f"Hello {CUSTOMER_NAME_PLACEHOLDER},",
        "",
        "Thank you for contacting Tamara.",
    ]
    if apologize:
        parts.extend(["", "We apologize for the inconvenience."])
    if body:
        parts.extend(["", body])
    parts.extend(
        [
            "",
            "If you have any other inquiries, please don't hesitate to contact us again.",
            "Tamara Care Team",
        ]
    )
    return "\n".join(parts)


def standardize_email_ar(matched_ar: str, *, apologize: bool) -> str:
    body = _polish_arabic_body(_strip_shell(matched_ar, arabic=True))
    parts = [
        f"هلا وسهلا {CUSTOMER_NAME_PLACEHOLDER_AR}،",
        "",
        "شكرًا لتواصلك مع تمارا.",
    ]
    if apologize:
        parts.extend(["", "نعتذر عن الإشكالية."])
    if body:
        parts.extend(["", body])
    parts.extend(
        [
            "",
            "إذا عندك أي استفسار ثاني، لا تتردد تتواصل معنا مرة ثانية.",
            "فريق رعاية تمارا",
        ]
    )
    return "\n".join(parts)


def standardize_matched_emails(
    matched_en: str,
    matched_ar: str,
    notes: str,
) -> tuple[str, str]:
    """Keep matched Care content; wrap in one standard agent-facing shell."""
    apologize = needs_apology(notes)
    return (
        standardize_email_en(matched_en, apologize=apologize),
        standardize_email_ar(matched_ar, apologize=apologize),
    )
