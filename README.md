# Zain — Tamara Voice Care AI Teammate

Zain helps Tamara Voice Care agents finish After-Call Work faster.

Paste messy after-call notes → Zain returns:

1. **What to tell CX (Macro)** — approved Care talk track / quicktext  
2. **Email Generation** — bilingual EN + AR email in a fixed Tamara shell.  
3. **Case Comment** — QA-ready internal note  (milestone2)
4. **Case Closure** — suggested Salesforce **Issue Category / Sub Category / Issue type** (milestone2)

No fine-tuning for now(in the future with approval). Matching is retrieval from local Care databases (that will result in 100% accuracy).

> Use synthetic or anonymized notes for demos. Do not paste real customer PII into shared environments.

---

## What works today

| Pillar | How it works |
|--------|----------------|
| Macro + Email | Retrieves from `data/emails_db_expanded.json` (Care quicktexts). Agent picks if several match. Email body stays standardized Care text. |
| Case Comment | Built from notes + matched scenario / macro context |
| Case Closure | Retrieves from `data/issue_types_kb.json` built from **[Customer] Issue Types** |

**Not required to run the app:** LLM API key. Core flow is local retrieval + Streamlit UI.

---

## Install & run (Windows)

### 1. Prerequisites

- Python **3.11+** recommended  
- Git  

### 2. Clone

```powershell
git clone https://github.com/jihadkandil-ai/zain.git
cd zain
```

### 3. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. (Optional) Environment file

Only needed later if you re-enable LLM helpers. Core Zain runs without it.

```powershell
copy .env.example .env
```

### 6. Start Zain

```powershell
streamlit run app.py
```

Browser opens at `http://localhost:8501`.

---

## Install & run (macOS / Linux)

```bash
git clone https://github.com/jihadkandil-ai/zain.git
cd zain
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Try it (2 minutes)

1. Open the app and paste messy notes, for example:
   - `cust didn't receive login OTP`
   - `late fee charged wants waiver`
   - `item damaged not as described`
   - `refund not received late refund`
2. Click **Generate with Zain**.
3. If several Care macros match, pick the right one.
4. Check the four tabs: Macro · Email · Case Comment · Case Closure.

---

## Project layout

```
app.py                          # Streamlit workspace
requirements.txt
.env.example                    # Optional LLM proxy settings
.streamlit/config.toml          # Tamara theme
data/
  emails_db_expanded.json       # Care email / macro DB (retrieval)
  issue_types_kb.json           # Salesforce issue types L1/L2/L3
  tamara_knowledge_base.json    # Scenario / case-comment helpers
src/
  emails_db.py                  # Macro matching
  email_standardize.py          # Fixed Tamara email shell
  issue_types.py                # Issue type retrieval
  knowledge_base.py             # Case comment / scenario helpers
  debug_trace.py                # Optional debug (ZAIN_DEBUG=1)
scripts/
  build_issue_types_kb.py       # Rebuild issue_types_kb.json
docs/                           # Product one-pager / PRD
```

### Rebuild issue types DB (after KB article updates)

```powershell
.\venv\Scripts\python.exe scripts\build_issue_types_kb.py
```

---

## Deploy on Railway

1. Push this repo to GitHub (already configured as `origin`).
2. Open [railway.com/new](https://railway.com/new) → **Deploy from GitHub repo** → select `zain`.
3. Railway reads `railway.json` and starts Streamlit on `$PORT`.
4. After the first deploy: **Settings → Networking → Generate Domain**.

Core Zain needs no env vars. Optional LLM proxy keys (`LLM_PROXY_API_KEY`, etc.) can be added under **Variables** later.

## Optional: share locally via Cloudflare Tunnel

Quick temporary link (changes each run):

```powershell
cloudflared tunnel --url http://localhost:8501
```

For a permanent hostname, use a **named Cloudflare Tunnel** on a domain you control.


---

## Docs

- [One-pager](docs/ZAIN_NOTION_ONE_PAGER.md)
- [PRD](docs/ZAIN_NOTION_PRD.md)
