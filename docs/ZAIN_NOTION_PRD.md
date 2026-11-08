# Zain — Tamara CX AI Teammate
## Product Requirements Document (PRD) & Project Wiki

**Product name:** Zain  
**Owner / domain:** Tamara Customer Experience (CX) — Voice Care  
**Document type:** PRD + Project Wiki (Notion one-pager ready)  
**Status:** Hackathon prototype / MVP  
**Last updated:** November 2026  

---

## 1. Executive Summary & Vision

**Zain** is an AI-powered **CX Copilot** built for Tamara’s Customer Experience team. It acts as a **real-time, on-the-job AI teammate**: agents dump messy, unstructured after-call (“brain dump”) notes, and Zain turns them into **approved, actionable outputs** aligned with Tamara’s Knowledge Base and Care tone of voice.

### Vision
Empower Voice agents to handle **back-to-back calls** with consistent quality — so wrap-up is faster, documentation is QA-ready, and customers get clear bilingual communication without guesswork.

### Problem
Voice agents spend valuable After-Call Work (ACW) time rewriting notes into:
- Customer-facing talk tracks / macros  
- Bilingual emails (EN / AR)  
- Internal case comments  
- CRM closure fields  

Quality varies by tenure; new agents are more likely to miss formatting, miss required evidence asks, or send generic answers that increase customer effort.

### Solution (one line)
**Messy notes in → Zain drafts Macro + Case Comment + Email + Closure recommendation out.**

---

## 2. Core Features (How it Works)

### 2.1 Agent Input
- Agent types **rough, messy notes** during or immediately after the call (English, Arabic, or mixed).  
- No need for perfect grammar or structure — Zain interprets intent from the brain dump.  
- **Sensitive CX fields** (name, order ID, amounts, ARN, etc.) are left blank for the agent to fill — Zain does not invent or auto-fill personal data.

### 2.2 Zain’s Output — Four Pillars

| # | Pillar | What the agent gets |
|---|--------|---------------------|
| 1 | **What to tell CX (Macro)** | Exact approved talk track / script the agent should say or read (EN + AR). |
| 2 | **Case Comment** | QA-ready internal note structured as **CX Complaint** + **Action Taken**. |
| 3 | **Email Generation** | Formatted **Arabic / English** customer email, ready to send (agent fills blanks). |
| 4 | **Case Closure Recommendation** | Suggested Salesforce fields (e.g. Status, Interaction Type, Issue Category, Sub Category, Issue Type, Closure Reason). |

### 2.3 Current MVP behaviour (prototype)
- Streamlit **Zain Workspace** with Tamara-branded login (`@tamara.co` only).  
- Agent dumps notes → **Generate with Zain**.  
- **Email Generation** is wired to a local **Emails Virtual DB** (approved-style templates, bilingual).  
- Intent routing matches notes to a template; if intent is unclear → warning (no random/refund default).  
- Macro / Case Comment / Closure tabs are scaffolded for the full four-pillar UX (content expansion next).

### 2.4 Design principles
- **Agent-first UX:** input left, output right; bilingual readable cards.  
- **KB-aligned:** outputs follow approved macros / Care tone (not free-form invention).  
- **Safe by default:** synthetic/demo data in hackathon; blank sensitive fields; no random wrong email on vague input.  
- **Tamara brand:** login + sidebar use official Tamara wordmark and Care visual language.

---

## 3. Business Impact & Value Proposition

### 3.1 Efficiency & AHT / ACW
- **Target pain:** ~**1.5 minutes** typical wrap-up spent on emails + case notes per interaction *(assumption — validate with Voice ops)*.  
- Zain aims to **compress wrap-up** by drafting during/just after the call so agents can act in real time instead of rewriting from scratch.  
- **Illustrative estimate (assumptions stated):**  
  - If ACW drafting averages **1.5 min/call** and Zain saves **40–60%** of that drafting time → **~0.6–0.9 min saved/call**.  
  - Across **N agents × Z calls/day**, weekly hours saved scale linearly — replace N/Z with pilot numbers before leadership review.

### 3.2 Business resilience
- Acts as a **quality buffer** on understaffed / high-volume shifts.  
- Agents can take **back-to-back calls** with less documentation debt and less burnout from repetitive rewrite work.

### 3.3 CSAT elevation & detractor prevention
- Reduces **wrong or incomplete next steps** from newer agents (e.g. missing evidence asks, unclear refund guidance).  
- Moves away from **generic directory dumps** toward **context-specific** answers (e.g. merchant / category questions) — lower customer effort *(full merchant assistant = roadmap)*.

### 3.4 Quality Assurance (QA)
- Standardizes case documentation toward **Critical Attribute** compliance.  
- Goal: **eliminate documentation-related Critical Attribute fails** caused by missing structure (Complaint / Action Taken) or inconsistent tone.

### 3.5 Coaching & management
- Frees Team Leaders from repetitive coaching on **basic formatting and process hygiene**.  
- TLs can focus coaching on **empathy, judgment, and complex scenarios**.

### 3.6 Seamless handoffs
- Standardized notes mean the **next agent** (or L2) immediately sees what happened and what to do next — fewer re-asks and fewer reopen loops.

### 3.7 Assumptions (for estimates — update with ops data)
| Assumption | Placeholder value | Source needed |
|------------|-------------------|---------------|
| Avg ACW email/docs time | 1.5 min / call | Voice WFM / TL sample |
| Time saved with Zain | 40–60% of drafting time | Pilot measurement |
| Agents in pilot | TBD | CX leadership |
| Calls / agent / day | TBD | WFM |
| QA fail rate on case docs | TBD | QA dashboards |

---

## 4. Product Roadmap

### 4.1 Current prototype (MVP) — Hackathon
**Focus:** prove the four-pillar UX + deliver **working Email Generation** from messy notes.

| Delivered | Detail |
|-----------|--------|
| Agent workspace | Login, sidebar, input + 4 output tabs |
| Email virtual DB | Approved-style bilingual templates; blanks for CX-sensitive fields |
| Intent routing | Keyword/DB match; unclear intent → explicit warning |
| Brand | Tamara logo + Care-aligned UI |

**In progress / next in MVP:** fill Macro, Case Comment, and Closure from the same notes + KB-style DBs (same pattern as Emails).

### 4.2 Near-term (post-hackathon pilot)
1. Connect **Tamara LLM Proxy** (approved virtual key) for adaptive drafting on top of macros/DB.  
2. Expand virtual DBs: **Macros**, **Case Comments**, **Closure field maps**.  
3. Soft-launch with Voice agents + QA scoring side-by-side.  
4. Embed **copy-to-clipboard / CRM paste** actions (then Salesforce embed).

### 4.3 Future iterations (long-term vision)

#### Merchant Directory & Category Assistant
- Train Zain on Tamara’s **merchant / partner** knowledge.  
- Agents ask: *“Who are our insurance merchants?”* / *“Is Merchant X a partner?”*  
- Zain returns the **exact list or status** for live call handling — not a generic link dump.

#### Escalation Routing
- Detect when L2 is needed (Tech, Trust & Safety, Collections, etc.).  
- Prompt for **mandatory fields**, generate escalation note, draft **customer update email**.

#### Phased rollouts
- Each version targets a **specific operational bottleneck**.  
- Strict evaluation set + Care/QA sign-off before wider adoption.

---

## 5. How It Was Built (for Notion one-pager)

| Layer | Choice |
|-------|--------|
| UI | Streamlit agent workspace (Tamara-branded) |
| Auth (demo) | `@tamara.co` email gate |
| Email knowledge | Local **Emails Virtual DB** (`data/emails_db.json`) |
| Routing | Intent match from notes → template (no random default) |
| LLM path (planned) | Tamara LLM Proxy (OpenAI-compatible), e.g. Gemini flash-class model |
| Safety | Synthetic samples only in hackathon; blank PII fields; unclear-intent warning |

**Repo layout (high level):** `app.py` (UI) · `src/emails_db.py` (loader + routing) · `data/emails_db.json` (templates) · `docs/` (this wiki)

---

## 6. Prototype Performance (current)

| Capability | Status |
|------------|--------|
| Login + agent dashboard | Working |
| Messy notes → Email EN/AR | Working (DB-backed) |
| Unclear intent handling | Working (warning, no wrong email) |
| Macro / Case Comment / Closure | UI present; content still placeholder / next DB wave |
| Multi-case generate/clear flow | Working |
| Production CRM write-back | Not yet |

**Demo tip (≤5 min):** Login → dump notes (e.g. ask for evidence / late refund) → Generate → show Email EN+AR → show warning on gibberish → mention roadmap pillars.

---

## 7. Where AI Is Used — and What It Adds

| Today (MVP) | What it adds |
|-------------|--------------|
| Structured virtual DB + intent routing | Instant bilingual email drafts grounded in approved wording |
| *(Planned)* Tamara LLM Proxy | Interprets free-form brain dumps beyond exact keywords; adapts tone while staying macro-constrained |

**What templates alone cannot do well:** understand incomplete, mixed-language brain dumps and still produce complete, context-aware Care language. **AI + KB/macros** together give speed *and* compliance.

---

## 8. Remaining Steps to Production / Adoption

1. **Content:** complete Macro + Case Comment + Closure virtual DBs (same pattern as Email).  
2. **LLM:** approved Tamara LLM Proxy key, evaluation set, rate limits / budget.  
3. **CRM:** Salesforce field mapping + one-click case update (after copy-paste pilot).  
4. **KB:** connect approved Knowledge Base / merchant directory (Phase: Merchant Assistant).  
5. **Escalation Guard:** mandatory fields + L2 routing (Phase: Escalation).  
6. **Security:** SSO, audit logs, no real PII in prompts during pilot; retention policy.  
7. **Pilot:** Voice + QA scorecard → iterate → wider rollout.

---

## 9. Success Metrics (suggested)

| Metric | Direction | Notes |
|--------|-----------|-------|
| ACW / wrap-up seconds on email+notes | ↓ | Primary efficiency KPI |
| Documentation Critical Attribute fail rate | ↓ | QA |
| Agent CSAT / effort (internal) | ↑ | Survey in pilot |
| Time-to-first-draft after call | ↓ | Stopwatch / tooling |
| % cases with complete Complaint + Action Taken | ↑ | Audit sample |

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Wrong template / wrong advice | Unclear-intent warning; human agent always reviews before send |
| PII leakage | Blanks for sensitive fields; synthetic data in demo; proxy + redaction later |
| Agent over-trust | UI framing: “draft — review & fill blanks” |
| KB drift | Versioned virtual DBs + Care ownership of templates |

---

## 11. Submission Checklist (Hackathon)

- [ ] **Prototype link** (working app)  
- [ ] **Code repository** link  
- [ ] **Demo video** (≤ 5 minutes)  
- [ ] **This Notion page** linked in the final submission form  
- [ ] Deadline: **Sunday 8 November, 11:59 PM KSA**

---

## 12. One-Paragraph Elevator Pitch (copy for Notion header)

> **Zain** is Tamara Voice’s AI teammate: agents paste messy after-call notes and instantly get a Care-ready talk track, a QA-structured case comment, a bilingual customer email, and suggested Salesforce closure fields — cutting wrap-up time, protecting CSAT, and standardizing quality so the team can handle high-volume days without sacrificing consistency.

---

*Ownership of hackathon work follows Tamara hackathon rules. Use synthetic data only in demos. Do not paste real customer, merchant, or employee PII into the prototype.*
