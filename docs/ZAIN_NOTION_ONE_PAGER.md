# Zain — Tamara Voice Care AI Teammate
## Notion One-Pager (Hackathon Submission)

**Product:** Zain  
**Team domain:** Tamara CX — Voice Care  
**Type:** Internal AI Copilot (agent-facing)  
**Status:** Working prototype (MVP) → iterative roadmap to production  
**Deadline context:** Tamara 2026 AI Hackathon  

---

## 1. Executive Summary

**Zain** is a Copilot for Tamara CX agents. The agent writes a **messy note** (brain dump during or after the call). Zain processes that note and returns a structured, Care-ready response.

That response includes:

1. **What to tell the CX** — the approved talk track / macro the agent should say or read  
2. **Case comment** — a professional internal note with **CX complaint** + **action taken**  
3. **Email** — a ready draft when the agent needs to send a specific customer email (EN / AR)  
4. **Case closure recommendation** — suggested fields for the CRM currently in use (e.g. Salesforce)

All of this is grounded in **continuous training on Tamara’s Knowledge Base** (approved macros, processes, and Care guidance)—so output stays consistent with how Tamara wants customers to be served.

> **One-line vision:** Enable agents to handle back-to-back calls with speed *and* quality—Zain as a real-time teammate on every interaction.

---

## 2. How It Works (Agent Flow)

| Step | What happens |
|------|----------------|
| 1 | Agent dumps rough notes (EN, AR, or mixed)—no need for perfect formatting |
| 2 | Agent clicks **Generate with Zain** |
| 3 | Zain detects intent and drafts the relevant pillars |
| 4 | Agent **reviews**, fills any blank sensitive fields (order ID, amount, ARN, etc.), then uses the output on the call / in CRM |

**Design rule:** Zain drafts; the agent remains accountable for send and case update.

**Note (future milestones):** In later versions, Zain will also assist agents on **hard cases**—professionally guiding the right next action to reduce agent-side mistakes on scenarios such as **disputes, claims, and escalations**.

---

## 3. Business Impact & Value Proposition

### 3.1 Efficiency — AHT & wrap-up time
- Provides a **fast, real-time** draft when an agent needs to send an email **in the middle of a call**—reducing handle-time friction.  
- Targets the typical **~1.5 minute wrap-up** agents spend closing documentation after a call.  
- **Assumption (to validate in pilot):** If wrap-up drafting averages 1.5 min and Zain saves a material share of that work, team-level AHT/ACW improves without adding headcount.

### 3.2 Operational resilience (understaffed / high-volume shifts)
- On short-staffed queues, agents take **back-to-back calls**.  
- Zain reduces post-call delay so the next caller is not waiting because the previous case is still being written up.  
- Acts as a **quality buffer** when the floor is under pressure—not only a speed tool.

### 3.3 CSAT — prevent detractors from wrong or weak actions
Today, many pain points come from situations such as:
- A **new agent** takes the **wrong action** → customer waits longer → issue may remain unresolved → detractor risk.  

With Zain, when an agent writes something like *“customer wants to raise a claim”* and provides the required context, a KB-trained Zain can instruct:  
**“In this specific case, take this exact action.”**

That reduces guesswork, wrong paths, and avoidable follow-ups—**long-term CSAT lift**.

### 3.4 Quality Assurance — Critical Attributes & team metrics
- **Case comments** become standardized: exactly what the customer complained about + exactly what the agent told them / did.  
- Goal: **no agent fails a Critical Attribute on case comments** for missing or unstructured documentation.  
- Fewer **“0” scores** on documentation attributes → team QA metrics rise.  
- Less time spent by **Team Leaders** coaching basic formatting and process hygiene—coaching can shift to judgment, empathy, and complex cases.

### 3.5 Handoffs & next-agent clarity
- Any later agent reading the ticket sees a clear, professional record of the solution already given.  
- They know the **exact next step**—fewer re-asks, fewer loops, cleaner ownership across shifts and queues.

---

## 4. Current Prototype vs Long-Term Plan

### 4.1 Current prototype (this hackathon MVP)
Focused on proving the copilot loop end-to-end, with priority on:

- **Email generation** (bilingual drafts from messy notes + approved-style template DB)  
- **What to tell the customer** (macro / talk-track pillar in the product UX)  
- Full **four-pillar workspace** (Macro · Email · Case Comment · Case Closure) so agents experience the real workflow  

**Built as:** Streamlit agent workspace, Tamara-branded login, local emails knowledge DB, intent routing with safe handling when notes are unclear (no random wrong email).

### 4.2 Long-term iterative releases
Zain will ship **version by version**. Each release solves a **specific operational bottleneck**, with a deliberate plan for:

1. Knowledge / scenario training  
2. Output evaluation (Care + QA sign-off)  
3. Controlled pilot  
4. Wider adoption  

---

## 5. Future Work (High-Impact Use Cases)

### 5.1 Escalation intelligence
Instead of agents wasting time hunting for the correct escalation path, Zain—trained on escalation scenarios—will instruct:

- **Escalate to:** [Specific team]  
- **Attach:** [Required information]  
- **Ask the customer for:** [Specific details]  
- **Also generate** the customer-facing email explaining the next step  

This reduces mis-routes, incomplete escalations, and repeat contacts.

### 5.2 Merchant & category assistant (CSAT / detractor prevention)
**Today’s friction:** Customers ask about a specific merchant or category; agents often can only send a **generic directory link** and ask the customer to search alone—high effort, weak help, detractor risk.

**Future Zain:** Trained on Tamara merchant lists by category, so agents can ask:

- *“Who are our insurance merchants?”* → exact answer  
- *“Is Merchant X one of our partners?”* → yes/no + guidance  

**Impact:** Faster, more precise help on the call → **higher CSAT** and fewer detractors caused by “insufficient help.”

---

## 6. Where AI Adds Value (vs templates alone)

| Capability | Why AI matters |
|------------|----------------|
| Interpreting messy, mixed-language brain dumps | Templates cannot reliably parse free-form agent notes |
| Choosing the right action / macro / email path | Continuously trained on Tamara KB and scenarios |
| Drafting bilingual Care-ready language | Speed + consistency across tenures |
| Future: escalations & merchant Q&A | Instant retrieval + instruction beyond static links |

**Guardrail:** AI drafts are constrained by approved KB/macros; agents always review before send.

---

## 7. Remaining Steps to Production / Adoption

1. Complete content DBs for **Macro**, **Case Comment**, and **CRM closure** maps (same pattern as Email).  
2. Connect **Tamara LLM Proxy** (approved virtual key) for adaptive generation on top of KB.  
3. Evaluation set + QA/Care review of outputs.  
4. Pilot with Voice agents; measure wrap-up time, QA Critical Attributes, and agent effort.  
5. CRM embed (copy actions → Salesforce update).  
6. Release **Escalation** and **Merchant Assistant** versions with dedicated training + evaluation.  
7. SSO, audit logging, and PII-safe prompting for production scale.

---

## 8. Success Metrics (Suggested)

| Metric | Target direction |
|--------|------------------|
| Wrap-up / ACW time after call | ↓ (vs ~1.5 min baseline) |
| Mid-call email draft time | ↓ |
| Critical Attribute fails on case comments | ↓ (toward zero for doc structure) |
| Team QA “0” scores on documentation | ↓ |
| TL coaching hours on basic formatting | ↓ |
| CSAT / detractors on “insufficient help” / wrong action | Improve |
| Time to correct escalation path | ↓ *(future version)* |
| Merchant inquiry resolution without generic link-only | ↑ *(future version)* |

---

## 9. Elevator Pitch (Notion header / demo close)

> **Zain** is Tamara Voice’s AI teammate. Agents paste messy notes; Zain returns what to tell the customer, a QA-ready case comment, the right email draft, and CRM closure guidance—trained on Tamara’s Knowledge Base. It cuts wrap-up time, protects CSAT, raises QA scores, and scales quality on high-volume days. This prototype proves email + talk-track assistance; the roadmap adds escalation intelligence and merchant answers that replace generic directory links.

---

## 10. Submission Links (fill before Sunday 8 Nov, 11:59 PM KSA)

| Deliverable | Link / status |
|-------------|----------------|
| Working prototype | *[add trycloudflare / Streamlit Cloud URL]* |
| Code repository | *[add repo URL]* |
| Demo video (≤ 5 min) | *[add recording link]* |
| This Notion page | *[add Notion share link]* |

---

*Hackathon note: demos use synthetic data only. Do not paste real customer, merchant employee, or production PII into the prototype.*
