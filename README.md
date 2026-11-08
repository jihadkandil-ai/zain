# Zain — The Voice Team's AI Teammate

Hackathon prototype for Tamara's 2026 AI Hackathon.

Zain helps CX Care Voice Agents finish After-Call Work faster by turning messy notes into:

- Professional **customer emails** in **English and Arabic**
- A **QA-ready case comment** (Customer Issue + Provided Solution)

**Issue types in MVP:** Refund ARN · Unrecognized charge · Evidence request

> **Data rule:** Use synthetic data only. Do not paste real or masked customer, merchant, or employee information.

**UI theme:** Tamara brand tokens (Lavender `#9600F1`, Zingy Purple `#5300BA`, Dreamy/Light Lilac) per Tamara Visual Identity Guidelines.

---

## Quick start

```powershell
cd C:\Zain-Copilot
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env and set LLM_PROXY_API_KEY=... (Tamara virtual key)
streamlit run app.py
```

Without a proxy key, the app still runs using synthetic macro templates (demo never blanks).

---

## Tamara LLM Proxy access

Preferred model path: **Tamara AI Platform LLM Proxy** (`https://llmproxy.dwh.tamara.co/v1`).

1. Complete the request form: https://forms.gle/rvu7rSrBjXt71Gcm6  
2. Post in `#it-helpdesk` (template below)  
3. After approval, DE places the virtual key in Jumpcloud — put it in local `.env` only  

Model list: https://llmproxy.dwh.tamara.co/ui/model_hub_table/

### Suggested `#it-helpdesk` message

```text
Requesting LLM Proxy virtual key for Tamara 2026 AI Hackathon.

Purpose: Developing Zain, an internal CX Voice Team copilot that turns messy after-call notes into bilingual (EN/AR) customer emails and QA-ready case comments (Refund ARN, unrecognized charge, evidence request).

Business value: Reduce ACW/AHT, improve QA consistency and Tamara tone of voice, free SMEs/TLs from repetitive coaching — prototype aimed at later CX pilot.

Team name: <YOUR_TEAM_NAME>
Team account or Personal account: <Team / Personal>
Application name: Zain (Voice Team AI Teammate)
Environment: development
LLM(s): gemini-2.0-flash (or equivalent flash/reasoning model from model hub — bilingual drafting + structured JSON)
Sensitive/confidential company data into LLM?: No
Measures: Synthetic data only for hackathon; light email/phone redaction in app; no real customer/merchant/employee PII
Budget allocation: ~$50–100 / month during hackathon + short pilot
Rate limit estimation: ~5–10 RPM, ~50K TPM (low; local demo + short evaluation runs)
```

---

## Demo script (≤5 minutes)

1. Open the app and show the Tamara-branded UI + sidebar samples (synthetic IDs only: `TMP-…`, `PAY-…`).
2. Load **Refund ARN — messy notes**. Point at the raw brain-dump on the left.
3. Click **Generate with Zain**. Show:
   - Polished English email
   - Arabic email
   - Case comment (Issue + Solution)
4. Optionally load **Unrecognized charge** or **Evidence request** to show adaptation beyond a single template.
5. Close with business impact: lower ACW/AHT, fewer QA documentation mistakes, bilingual consistency, path to CRM embed + KB + escalation guard — via Tamara LLM Proxy for production-aligned access.

---

## Notion one-pager outline (submission)

### Business impact and estimates (state assumptions)

- **Problem:** Voice agents spend ACW writing emails and case notes; quality varies; bilingual drafting is slow.
- **Assumption example:** If ACW email/docs averages X minutes/call and Zain cuts Y%, across N Voice agents / Z calls/day → hours saved / week.
- **Quality:** Fewer vague case comments and tone/macro deviations → fewer QA fails and less TL coaching on basics.
- **Resilience:** Consistent handling during high volume without linear headcount growth.

### How it was built

- Streamlit UI styled with Tamara Lavender brand tokens
- Tamara LLM Proxy (OpenAI-compatible) for generation
- Synthetic approved-style macros for tone + offline fallback
- Local `.env` for virtual key (no secrets in repo)

### Prototype performance

- Works for 3 high-volume scenarios with EN + AR output
- Structured case comment draft included
- Fallback templates if the model is unavailable
- Light PII pattern redaction (email/phone) for demo safety

### Where AI is used and what it adds

- AI adapts messy, incomplete agent notes into complete bilingual emails and structured CRM notes.
- Templates alone cannot interpret free-form brain-dumps or fill context-aware wording; the LLM does.
- Macros constrain tone so output stays production-credible.

### Remaining steps to production / adoption

1. Embed in the agent desktop / CRM (copy actions → one-click case update)
2. Connect approved Knowledge Base / real macros (Phase 3)
3. Escalation Guard with mandatory field checks (Phase 4)
4. Auth/SSO, audit logging, evaluation set, and Tamara LLM Proxy budget/rate limits
5. Pilot with Voice Team + QA scoring before wider rollout

---

## Project layout

```
app.py
.streamlit/config.toml
src/
  config.py
  prompts.py
  generator.py
  macros.py
data/
  sample_notes.json
.env.example
requirements.txt
```

## Hackathon compliance

- Synthetic sample notes and IDs only
- No real Tamara customer/merchant data
- LLM access via approved Tamara proxy when available
- Ownership of work belongs to Tamara per hackathon rules
