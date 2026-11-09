"""Serve matched Care macro text exactly — fill known placeholders only, never invent copy."""

from __future__ import annotations

from src.field_extract import extract_fields, fill_care_placeholders


def standardize_matched_emails(
    matched_en: str,
    matched_ar: str,
    notes: str,
) -> tuple[str, str]:
    """Exact Care EN/AR with placeholder fill from notes (no shell rewrite / no LLM rewrite)."""
    fields = extract_fields(notes)
    return (
        fill_care_placeholders(matched_en, fields, arabic=False),
        fill_care_placeholders(matched_ar, fields, arabic=True),
    )


def exact_macro_texts(
    matched_en: str,
    matched_ar: str,
    notes: str,
) -> tuple[str, str, dict]:
    """Same as emails, also return extracted fields for case comment / debug."""
    fields = extract_fields(notes)
    return (
        fill_care_placeholders(matched_en, fields, arabic=False),
        fill_care_placeholders(matched_ar, fields, arabic=True),
        fields,
    )
