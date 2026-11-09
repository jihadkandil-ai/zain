"""Zain — Tamara Voice Team AI teammate (agent-facing workspace)."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from src.email_standardize import standardize_matched_emails
from src.emails_db import resolve_exact_macro
from src.issue_types import (
    format_closure_suggestion,
    list_matching_issue_types,
    suggest_issue_type,
)
from src.knowledge_base import generate_from_notes

CLEAR_OUTPUT_BUTTON_LABEL = "__zain_clear_output__"
TAMARA_LOGO_URL = (
    "https://cdn.prod.website-files.com/67c184892f7a84b971ff49d9/"
    "68931b49f2808979578bdc64_tamara-text-logo-black-en.svg"
)
TAMARA_LOGO_WHITE_URL = (
    "https://cdn.prod.website-files.com/67c184892f7a84b971ff49d9/"
    "68931b49898010539c86667f_tamara-text-logo-white-en.svg"
)

# Tamara brand tokens (Visual Identity Guidelines)
TAMARA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --tamara-lavender: #9600F1;
  --tamara-zingy: #5300BA;
  --tamara-dreamy: #CEA4FF;
  --tamara-light: #E5CFFF;
  --tamara-mist: #E6E6F3;
  --tamara-ink: #1A1033;
  --tamara-soft-grey: #707698;
}

html, body, [class*="css"] {
  font-family: Inter, "Segoe UI", sans-serif;
  color: var(--tamara-ink);
}

.stApp {
  background:
    radial-gradient(1200px 500px at 10% -10%, #E5CFFF 0%, transparent 55%),
    radial-gradient(900px 420px at 100% 0%, #CEA4FF55 0%, transparent 50%),
    #FFFFFF;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #5300BA 0%, #9600F1 55%, #CEA4FF 100%);
}
[data-testid="stSidebar"] * {
  color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: #F5EDFF !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: rgba(255,255,255,0.14);
  border: 1px solid rgba(255,255,255,0.35);
  color: #fff !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.28);
  border-color: #fff;
}

/* Login — aligned with tamara.co (clean white, navy type, lavender CTA) */
.zain-login-page {
  position: relative;
  max-width: 480px;
  margin: 6vh auto 2rem;
  padding: 2.5rem 2.25rem 2.1rem;
  border-radius: 28px;
  background: #FFFFFF;
  border: 1px solid #EEEAF6;
  box-shadow: 0 18px 50px rgba(29, 33, 48, 0.08);
  text-align: center;
  overflow: hidden;
}
.zain-login-page::before {
  content: "";
  position: absolute;
  width: 220px;
  height: 220px;
  top: -90px;
  right: -70px;
  background: radial-gradient(circle, rgba(150, 0, 241, 0.12) 0%, transparent 70%);
  pointer-events: none;
}
.zain-login-page::after {
  content: "";
  position: absolute;
  width: 160px;
  height: 160px;
  bottom: -70px;
  left: -50px;
  background: radial-gradient(circle, rgba(245, 166, 35, 0.14) 0%, transparent 70%);
  pointer-events: none;
}
.zain-login-logo {
  display: flex;
  justify-content: center;
  margin: 0.15rem 0 1.35rem;
}
.zain-login-logo img {
  width: 168px;
  height: auto;
}
.zain-login-kicker {
  margin: 0 0 0.45rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--tamara-lavender);
}
.zain-login-page h1 {
  margin: 0 0 1rem;
  font-size: 1.85rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #1D2130 !important;
  line-height: 1.2;
}
.zain-login-greeting {
  margin: 0 0 0.4rem;
  color: #1D2130;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.5;
}
.zain-login-greeting-ar {
  margin: 0 0 1.25rem;
  color: #707698;
  font-size: 1rem;
  line-height: 1.6;
  direction: rtl;
}
.zain-login-sub {
  margin: 0 0 0.25rem;
  color: #707698;
  font-size: 0.92rem;
}
.zain-login-star {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin: 0 0.35rem;
  background: var(--tamara-lavender);
  clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
  vertical-align: middle;
}
.zain-login-star.orange {
  background: #F5A623;
}

.zain-hero {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1.25rem;
  border-radius: 18px;
  background: linear-gradient(115deg, #5300BA 0%, #9600F1 48%, #CEA4FF 100%);
  color: #fff;
  box-shadow: 0 10px 28px rgba(150, 0, 241, 0.22);
}
.zain-mark {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.35rem;
}
.zain-hero h1 {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 700;
  color: #fff !important;
}
.zain-hero p {
  margin: 0.2rem 0 0;
  color: #F5EDFF !important;
  font-size: 0.95rem;
}

.zain-panel {
  background: #FFFFFF;
  border: 1px solid var(--tamara-mist);
  border-radius: 16px;
  padding: 1rem 1.1rem 1.15rem;
  box-shadow: 0 4px 18px rgba(83, 0, 186, 0.06);
  margin-bottom: 1rem;
}
.zain-panel h3 {
  color: var(--tamara-zingy) !important;
  margin-top: 0;
}

div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
  background: linear-gradient(90deg, #5300BA, #9600F1);
  border: none;
  color: white;
  font-weight: 600;
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="baseButton-primary"]:hover {
  background: linear-gradient(90deg, #4600A0, #7E00D0);
  color: white;
  border: none;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--tamara-lavender) !important;
}

/* Readable, wrapping script cards (no horizontal scroll) */
.zain-script-card {
  background: #F7F0FF;
  border: 1px solid var(--tamara-mist);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  margin: 0.35rem 0 1rem;
  overflow-x: hidden;
}
.zain-script-label {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--tamara-zingy);
  margin-bottom: 0.55rem;
}
.zain-script-body {
  margin: 0;
  font-family: Inter, "Segoe UI", sans-serif;
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--tamara-ink);
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: anywhere;
  overflow-x: hidden;
}
.zain-script-body.rtl {
  direction: rtl;
  text-align: right;
  unicode-bidi: plaintext;
  font-family: "Segoe UI", Tahoma, "Noto Naskh Arabic", "Arabic Typesetting", Arial, sans-serif;
  line-height: 1.85;
  letter-spacing: 0;
}
.zain-script-card.rtl-card {
  direction: rtl;
}
.zain-script-label.rtl-label {
  text-align: right;
}
textarea[data-zain-rtl="1"],
div[data-testid="stTextArea"]:has(textarea[aria-label="العربية — جاهز للنسخ"]) textarea {
  direction: rtl !important;
  text-align: right !important;
  unicode-bidi: plaintext !important;
  font-family: "Segoe UI", Tahoma, "Noto Naskh Arabic", Arial, sans-serif !important;
  line-height: 1.85 !important;
  font-size: 1.02rem !important;
}
</style>
"""

LIVE_CLEAR_JS = f"""
<script>
(function () {{
  const CLEAR_LABEL = {CLEAR_OUTPUT_BUTTON_LABEL!r};
  const doc = window.parent.document;
  if (window.parent.__zainClearWired === 2) return;
  window.parent.__zainClearWired = 2;

  function findClearButton() {{
    const buttons = doc.querySelectorAll('button');
    for (const btn of buttons) {{
      if ((btn.textContent || '').trim() === CLEAR_LABEL) {{
        const wrap = btn.closest('[data-testid="stButton"]');
        if (wrap) wrap.style.display = 'none';
        btn.style.display = 'none';
        return btn;
      }}
    }}
    return null;
  }}

  function hideOutputNow() {{
    doc.querySelectorAll('.zain-script-card').forEach((el) => {{
      el.style.display = 'none';
    }});
  }}

  function requestClearOutput() {{
    hideOutputNow();
    const btn = findClearButton();
    if (btn) btn.click();
  }}

  function wireNotesBox(ta) {{
    if (!ta || ta.dataset.zainLiveClear === '1') return;
    ta.dataset.zainLiveClear = '1';

    // Only clear after the agent is actively editing — avoids false clears on Streamlit rerender
    let armed = doc.activeElement === ta;
    let wasEmpty = !(ta.value || '').trim();

    ta.addEventListener('focus', () => {{ armed = true; }});
    ta.addEventListener('blur', () => {{ armed = false; }});
    ta.addEventListener('input', (e) => {{
      if (!e.isTrusted || !armed) {{
        wasEmpty = !(ta.value || '').trim();
        return;
      }}
      const empty = !(ta.value || '').trim();
      if (empty && !wasEmpty) requestClearOutput();
      wasEmpty = empty;
    }});
  }}

  function scan() {{
    findClearButton();
    const areas = doc.querySelectorAll('[data-testid="stTextArea"] textarea');
    if (areas.length) wireNotesBox(areas[0]);
  }}

  scan();
  new MutationObserver(scan).observe(doc.body, {{ childList: true, subtree: true }});
}})();
</script>
"""

ALLOWED_EMAIL_DOMAIN = "@tamara.co"

PLACEHOLDER_MACRO_EN = """Hi, thanks for calling Tamara Care.

I understand you'd like help with your recent request. I've reviewed what we discussed and I'm sending you a clear summary by email shortly.

If anything is still unclear after you receive that email, reply to it and we'll continue from there.

Is there anything else I can help you with on this call?"""

PLACEHOLDER_MACRO_AR = """مرحبًا، شكرًا لاتصالك برعاية تمارا.

أفهم أنك تحتاج مساعدة بخصوص طلبك الأخير. راجعت ما ناقشناه وسأرسل لك ملخصًا واضحًا عبر البريد الإلكتروني قريبًا.

إذا بقي أي شيء غير واضح بعد استلام الرسالة، يرجى الرد عليها وسنكمل من هناك.

هل هناك أي شيء آخر أستطيع مساعدتك به في هذه المكالمة؟"""

PLACEHOLDER_CASE_COMMENT = """CX Asks/Complaint:
[Placeholder] Customer contacted Voice Care with a request related to their recent interaction. Agent captured messy after-call notes for Zain to structure.

Action Taken:
[Placeholder] Agent used Zain to draft bilingual customer email, CX talk track, and suggested Salesforce closure fields. Awaiting CRM connection / Gemini generation in a later iteration."""

PLACEHOLDER_CASE_CLOSURE = """Suggested Salesforce fields:

• Status: Closed
• Interaction Type: Voice
• Issue Category: (clarify from notes)
• Sub Category: —
• Issue type: —
• Tip: Focus on the primary reason for contact; consult TL if unsure."""


INTENT_UNCLEAR_MSG = (
    "⚠️ Zain couldn't match a Care macro in emails_db_expanded. "
    "Please add clearer notes (e.g. partners, dispute steps, refund ARN)."
)


def init_state() -> None:
    defaults = {
        "authenticated": False,
        "user_email": "",
        "agent_notes": "",
        "show_output": False,
        "selected_email_id": "",
        "generation_warning": "",
        "generation_result": None,
        "macro_candidates": [],
        "macro_choice_id": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def start_new_case() -> None:
    st.session_state.agent_notes = ""
    st.session_state.show_output = False
    st.session_state.selected_email_id = ""
    st.session_state.generation_warning = ""
    st.session_state.generation_result = None
    st.session_state.macro_candidates = []
    st.session_state.macro_choice_id = ""


def clear_output_only() -> None:
    """Hide generated output without touching the notes widget value."""
    st.session_state.show_output = False
    st.session_state.selected_email_id = ""
    st.session_state.generation_warning = ""
    st.session_state.generation_result = None
    st.session_state.macro_candidates = []
    st.session_state.macro_choice_id = ""


def on_agent_notes_change() -> None:
    """When notes are cleared/edited and committed, drop stale output."""
    notes = (st.session_state.get("agent_notes") or "").strip()
    if not notes or st.session_state.get("show_output"):
        clear_output_only()


def _closure_from_notes(notes: str) -> tuple[str, list[dict[str, Any]]]:
    """Retrieve L1/L2/L3 issue type from [Customer] Issue Types KB."""
    hits = list_matching_issue_types(notes, limit=5)
    top = hits[0] if hits else suggest_issue_type(notes)
    text = format_closure_suggestion(top, notes)
    if len(hits) > 1:
        alts = "\n".join(
            f"  {i}. {h.get('path')} (score {h.get('_match_score')})"
            for i, h in enumerate(hits[1:], start=2)
        )
        text += f"\nOther close matches:\n{alts}\n"
    return text, hits


def _result_from_macro(template: dict[str, Any], notes: str) -> dict[str, Any]:
    """Match Care macro content, then wrap Email tab in a fixed Tamara shell.

    - Email Generation: standardized structure (greeting / thanks / body / closing)
    - What to tell CX: exact matched quicktext (no rewrite)
    - Case Closure: issue type L1/L2/L3 from issue_types_kb
    """
    raw_en = str(template.get("email_en") or "").strip()
    raw_ar = str(template.get("email_ar") or "").strip()
    email_en, email_ar = standardize_matched_emails(raw_en, raw_ar, notes)
    tid = str(template.get("id") or "")
    title = str(template.get("title") or tid)
    reason = str(template.get("_match_reason") or "retrieve")
    closure, issue_hits = _closure_from_notes(notes)
    return {
        "source": "emails_db_expanded",
        "scenario_id": tid,
        "scenario_title": title,
        "topic": "Care macros (quicktext)",
        # Exact matched Care text for the agent talk-track tab
        "macro_en": raw_en or PLACEHOLDER_MACRO_EN,
        "macro_ar": raw_ar or PLACEHOLDER_MACRO_AR,
        "case_comment": (
            "CX Asks/Complaint:\n"
            f"{notes.strip()}\n\n"
            "Action Taken:\n"
            f"Matched Care macro `{title}` and sent standardized Tamara email."
        ),
        "email_en": email_en,
        "email_ar": email_ar,
        "case_closure": closure,
        "issue_type_matches": issue_hits,
        # Future pillars (DBs to be shared)
        "claim_guidance": "",
        "escalation_guidance": "",
        "email_source": "macros_expanded_standardized",
        "email_template_id": tid,
        "email_match_reason": reason,
        "email_confidence": float(template.get("_match_score") or 0) / 100.0,
    }


def _apply_selected_macro(macro: dict[str, Any], notes: str) -> None:
    from src.debug_trace import zain_debug

    kb_result = generate_from_notes(notes)
    zain_debug(
        "app_using_macro",
        id=macro.get("id"),
        title=macro.get("title"),
        reason=macro.get("_match_reason"),
        score=macro.get("_match_score"),
        source_file="emails_db_expanded.json",
        en_start=(macro.get("email_en") or "")[:160],
        ar_start=(macro.get("email_ar") or "")[:160],
    )
    result = _result_from_macro(macro, notes)
    if kb_result:
        result["case_comment"] = kb_result.get("case_comment") or result["case_comment"]
        result["source"] = "emails_db_expanded+kb"
    # Always prefer Issue Types KB for Salesforce L1/L2/L3
    closure, issue_hits = _closure_from_notes(notes)
    result["case_closure"] = closure
    result["issue_type_matches"] = issue_hits
    st.session_state.generation_result = result
    st.session_state.selected_email_id = result.get("email_template_id") or ""
    st.session_state.macro_choice_id = str(macro.get("id") or "")
    st.session_state.generation_warning = ""
    st.session_state.show_output = True
    zain_debug(
        "app_run_generation_done",
        id=macro.get("id"),
        title=macro.get("title"),
        reason=macro.get("_match_reason"),
        issue_path=(issue_hits[0].get("path") if issue_hits else None),
    )


def run_generation(notes: str) -> None:
    """Retrieval shortlist → LLM picks exact Care macro → standardize Email shell."""
    from src.debug_trace import zain_debug

    try:
        zain_debug("app_run_generation_start", notes=notes)
        match = resolve_exact_macro(notes)
        zain_debug(
            "app_exact_macro",
            id=(match or {}).get("id"),
            title=(match or {}).get("title"),
            reason=(match or {}).get("_match_reason"),
        )

        if not match:
            closure, issue_hits = _closure_from_notes(notes)
            st.session_state.macro_candidates = []
            st.session_state.macro_choice_id = ""
            st.session_state.selected_email_id = ""
            st.session_state.generation_result = {
                "source": "issue_types_kb",
                "scenario_id": "",
                "scenario_title": "",
                "topic": "",
                "macro_en": "",
                "macro_ar": "",
                "case_comment": (
                    "CX Asks/Complaint:\n"
                    f"{notes.strip()}\n\n"
                    "Action Taken:\n"
                    "No Care macro matched; suggested Salesforce issue type from KB."
                ),
                "email_en": "",
                "email_ar": "",
                "case_closure": closure,
                "issue_type_matches": issue_hits,
            }
            st.session_state.generation_warning = INTENT_UNCLEAR_MSG
            st.session_state.show_output = True
            zain_debug(
                "app_run_generation_no_macro",
                issue_path=(issue_hits[0].get("path") if issue_hits else None),
            )
            return

        # Single exact macro — no multi-choice noise
        card = {
            "id": str(match.get("id") or ""),
            "title": str(match.get("title") or match.get("id") or ""),
            "score": float(match.get("_match_score") or 0),
            "reason": str(match.get("_match_reason") or ""),
            "email_en": str(match.get("email_en") or ""),
            "email_ar": str(match.get("email_ar") or ""),
        }
        st.session_state.macro_candidates = [card]
        st.session_state.macro_choice_id = card["id"]
        _apply_selected_macro(card, notes)
    except TimeoutError:
        st.session_state.selected_email_id = ""
        st.session_state.generation_result = None
        st.session_state.macro_candidates = []
        st.session_state.generation_warning = (
            "⚠️ Zain timed out while generating. Please try again."
        )
        st.session_state.show_output = True
    except Exception as exc:  # noqa: BLE001 — keep agent UI stable
        st.session_state.selected_email_id = ""
        st.session_state.generation_result = None
        st.session_state.macro_candidates = []
        st.session_state.generation_warning = (
            f"⚠️ Zain hit an error and couldn't generate safely. ({exc})"
        )
        st.session_state.show_output = True


def render_login() -> None:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown(
            f"""
            <div class="zain-login-page">
              <div class="zain-login-logo">
                <img src="{TAMARA_LOGO_URL}" alt="Tamara" />
              </div>
              <p class="zain-login-kicker">Care Voice · Internal</p>
              <h1>Welcome to Zain Workspace</h1>
              <p class="zain-login-greeting">
                <span class="zain-login-star"></span>
                Hello, I am Zain, your personal AI teammate.
                <span class="zain-login-star orange"></span>
              </p>
              <p class="zain-login-greeting-ar">
                أهلاً بك، أنا زين، مساعدك الذكي لفريق الدعم في تمارا.
              </p>
              <p class="zain-login-sub">Sign in with your Tamara email to continue.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        email = st.text_input(
            "Work email",
            placeholder="name@tamara.co",
            key="login_email_input",
        )
        if st.button("Log in", type="primary", use_container_width=True):
            cleaned = (email or "").strip().lower()
            if cleaned.endswith(ALLOWED_EMAIL_DOMAIN) and cleaned != ALLOWED_EMAIL_DOMAIN:
                st.session_state.authenticated = True
                st.session_state.user_email = cleaned
                st.rerun()
            else:
                st.error("Only @tamara.co email addresses are allowed.")

        st.caption("Inspired by [tamara.co](https://tamara.co/en-sa) · For Tamara Care agents only")


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding:0.35rem 0 0.9rem;">
              <img src="{TAMARA_LOGO_WHITE_URL}" alt="Tamara"
                   style="width:140px; height:auto; display:inline-block;" />
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.header("Agent Dashboard")
        st.write(f"Logged in as: {st.session_state.user_email}")
        st.divider()
        if st.button("🆕 Start New Case", use_container_width=True):
            start_new_case()
            st.rerun()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()


def render_script_card(label: str, text: str, *, rtl: bool = False) -> None:
    """Full-width wrapping card for Macro / Case / Closure (not Email tab)."""
    cleaned = text.strip()
    body_class = "zain-script-body rtl" if rtl else "zain-script-body"
    card_class = "zain-script-card rtl-card" if rtl else "zain-script-card"
    label_class = "zain-script-label rtl-label" if rtl else "zain-script-label"
    dir_attr = ' dir="rtl" lang="ar"' if rtl else ""
    safe = html.escape(cleaned)
    st.markdown(
        f"""
        <div class="{card_class}">
          <div class="{label_class}">{html.escape(label)}</div>
          <div class="{body_class}"{dir_attr}>{safe}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_output_tabs() -> None:
    result = st.session_state.get("generation_result") or {}
    warning = (st.session_state.generation_warning or "").strip()

    tab_macro, tab_email, tab_case, tab_closure, tab_claim, tab_escalation = st.tabs(
        [
            "💬 What to tell CX (Macro)",
            "✉️ Email Generation",
            "📝 Case Comment",
            "⚙️ Case Closure",
            "🧾 Claim",
            "🚨 Escalation",
        ]
    )

    with tab_macro:
        st.markdown("**Talk track / macro for the agent**")
        if warning or not result:
            st.info("Generate with a clear scenario to load the talk track.")
        else:
            title = result.get("scenario_title") or ""
            topic = result.get("topic") or ""
            if title or topic:
                st.caption(f"{topic} · {title}".strip(" ·"))
            render_script_card("English", str(result.get("macro_en") or PLACEHOLDER_MACRO_EN))
            render_script_card(
                "العربية",
                str(result.get("macro_ar") or PLACEHOLDER_MACRO_AR),
                rtl=True,
            )

    with tab_email:
        st.markdown("**Generated Arabic / English email**")
        if warning:
            st.info("No email draft shown until Zain can detect a clear issue from your notes.")
        elif not result:
            st.info("Generate from agent notes to load the matching email.")
        else:
            email_en = str(result.get("email_en") or "").strip()
            email_ar = str(result.get("email_ar") or "").strip()
            st.text_area(
                "English — ready to copy",
                value=email_en,
                height=280,
                key="copy_email_en",
                help="Select all (Ctrl+A) then copy (Ctrl+C) — ready to send to the customer.",
            )
            st.text_area(
                "العربية — جاهز للنسخ",
                value=email_ar,
                height=280,
                key="copy_email_ar",
                help="حدد الكل ثم انسخ — جاهز للإرسال للعميل.",
            )

    with tab_case:
        st.markdown("**QA-ready internal note**")
        if warning or not result:
            st.info("Generate with a clear scenario to load the case comment.")
        else:
            render_script_card(
                "Case comment",
                str(result.get("case_comment") or PLACEHOLDER_CASE_COMMENT),
            )

    with tab_closure:
        st.markdown("**Suggested Salesforce Issue Category / Sub Category / Issue type**")
        closure_text = str((result or {}).get("case_closure") or "").strip()
        if closure_text:
            render_script_card("Case closure", closure_text)
            hits = (result or {}).get("issue_type_matches") or []
            if hits:
                st.caption(
                    f"Top match from issue_types_kb ({len(hits)} ranked): "
                    f"`{hits[0].get('path')}`"
                )
        elif warning or not result:
            st.info("Generate from agent notes to suggest Salesforce issue type fields.")
        else:
            render_script_card(
                "Case closure",
                PLACEHOLDER_CASE_CLOSURE,
            )

    with tab_claim:
        st.markdown("**Claim guidance**")
        st.info(
            "Coming soon — Claim pillar will use a dedicated claims article DB "
            "(e.g. CX disputing / following up on a claim). Share the article to wire it."
        )
        render_script_card(
            "Claim (placeholder)",
            str(
                result.get("claim_guidance")
                or "No claim DB yet. Paste claim-related notes later once the article is loaded."
            ),
        )

    with tab_escalation:
        st.markdown("**Escalation scenarios**")
        st.info(
            "Coming soon — Escalation pillar will use a dedicated escalation scenarios DB. "
            "Share the article to wire it."
        )
        render_script_card(
            "Escalation (placeholder)",
            str(
                result.get("escalation_guidance")
                or "No escalation DB yet. Paste escalation notes later once the article is loaded."
            ),
        )


def render_workspace() -> None:
    st.markdown(
        """
        <div class="zain-hero">
          <div class="zain-mark">Z</div>
          <div>
            <h1>🎧 Zain: Tamara's AI Teammate</h1>
            <p>Dump messy after-call notes — get talk track, bilingual email, case comment, and closure fields.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="zain-panel">', unsafe_allow_html=True)
        st.subheader("Agent input")

        # Hidden control: JS clicks this when the agent empties the notes box.
        # Never rewrite agent_notes here — that broke multi-question Generate.
        if st.button(CLEAR_OUTPUT_BUTTON_LABEL, key="_zain_auto_clear"):
            clear_output_only()

        st.text_area(
            "Messy after-call notes (Dump everything here):",
            key="agent_notes",
            height=320,
            placeholder="e.g. cust angry wants refund arn order TMP-88421 …",
            on_change=on_agent_notes_change,
        )
        components.html(LIVE_CLEAR_JS, height=0, width=0)

        notes_now = (st.session_state.agent_notes or "").strip()
        if not notes_now:
            clear_output_only()

        if st.button("Generate with Zain", type="primary", use_container_width=True):
            notes = (st.session_state.agent_notes or "").strip()
            if not notes:
                st.error("Paste agent notes first, then generate.")
                clear_output_only()
            else:
                with st.spinner(
                    "Zain is picking the exact Care macro…"
                ):
                    run_generation(notes)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="zain-panel">', unsafe_allow_html=True)
        st.subheader("Zain output")
        if st.session_state.show_output:
            warning = (st.session_state.generation_warning or "").strip()
            if warning:
                st.warning(warning)
            else:
                candidates = st.session_state.get("macro_candidates") or []
                notes = (st.session_state.get("agent_notes") or "").strip()
                if len(candidates) > 1:
                    st.markdown("**Matched Care macros — choose one:**")
                    labels: dict[str, str] = {}
                    for c in candidates:
                        mid = c.get("id") or ""
                        title = c.get("title") or mid
                        if not mid:
                            continue
                        labels[mid] = title
                    choice = st.radio(
                        "Macro",
                        options=list(labels.keys()),
                        format_func=lambda mid: labels.get(mid, mid),
                        key="macro_choice_radio",
                        label_visibility="collapsed",
                    )
                    if choice and choice != st.session_state.get("macro_choice_id"):
                        selected = next(
                            (c for c in candidates if c["id"] == choice),
                            None,
                        )
                        if selected:
                            _apply_selected_macro(selected, notes)
                            st.rerun()
                elif len(candidates) == 1:
                    st.caption(f"Matched Care macro: `{candidates[0].get('title')}`")

                result = st.session_state.get("generation_result") or {}
                title = result.get("scenario_title") or ""
                if title:
                    st.caption(f"Selected macro: `{title}`")
            render_output_tabs()
        else:
            st.info("Generate to see talk track, bilingual email, case comment, and closure fields.")
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="Zain Workspace",
        page_icon="Z",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(TAMARA_CSS, unsafe_allow_html=True)
    init_state()

    if not st.session_state.authenticated:
        render_login()
        return

    render_sidebar()
    render_workspace()


if __name__ == "__main__":
    main()
