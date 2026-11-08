# Zain — Tamara Voice Care AI Teammate

Zain helps Tamara Voice Care agents finish After-Call Work faster.

Paste messy after-call notes → Zain returns:

1. **What to tell CX (Macro)** — approved Care talk track / quicktext  
2. **Email Generation** — bilingual EN + AR email in a fixed Tamara shell  
3. **Case Comment** — QA-ready internal note  
4. **Case Closure** — suggested Salesforce Issue Category / Sub Category / Issue type  

Matching is **local retrieval** from Care databases (no fine-tuning).  
**No LLM API key is required** to run the core app.

> Use synthetic or anonymized notes for demos. Do not paste real customer PII into shared environments.

---

## Quick start (anyone)

### Prerequisites

- **Python 3.11+** ([python.org](https://www.python.org/downloads/) — on Windows, check “Add python.exe to PATH”)
- **Git**

### 1. Clone

```bash
git clone https://github.com/jihadkandil-ai/zain.git
cd zain
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

Your browser should open **http://localhost:8501**.  
If it does not, open that URL manually.

### 5. Sign in

Use any email ending in **`@tamara.co`** (example: `agent@tamara.co`).  
Other domains are rejected by design.

---

## Try it (2 minutes)

1. Paste one of these notes:
   - `cust didn't receive login OTP`
   - `late fee charged wants waiver`
   - `item damaged not as described`
   - `refund not received late refund`
2. Click **Generate with Zain**.
3. If several Care macros match, pick the right one.
4. Review the four tabs: **Macro · Email · Case Comment · Case Closure**.

---

## What works today

| Pillar | How it works |
|--------|----------------|
| Macro + Email | Retrieves from `data/emails_db_expanded.json`. Agent picks if several match. Email uses the fixed Tamara shell. |
| Case Comment | Built from notes + matched scenario / macro context |
| Case Closure | Retrieves from `data/issue_types_kb.json` (Salesforce L1 / L2 / L3) |

Optional LLM proxy settings (`.env` from `.env.example`) are **not needed** for this core flow.

---

## Common problems

| Problem | Fix |
|---------|-----|
| `python` / `pip` not found | Install Python 3.11+, reopen the terminal, confirm with `python --version` |
| PowerShell won’t activate `venv` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again |
| Wrong Python / packages missing | Make sure `(venv)` is active, then `pip install -r requirements.txt` again |
| Port 8501 already in use | `streamlit run app.py --server.port 8502` |
| Login rejected | Email must end with `@tamara.co` |
| Browser didn’t open | Go to http://localhost:8501 |

---

## Project layout

```
app.py                          # Streamlit workspace
requirements.txt                # Python deps (Streamlit)
.env.example                    # Optional LLM proxy (not required)
.streamlit/config.toml          # Tamara theme
data/
  emails_db_expanded.json       # Care email / macro DB
  issue_types_kb.json           # Salesforce issue types
  tamara_knowledge_base.json    # Case-comment helpers
src/                            # Matching + email shell logic
scripts/build_issue_types_kb.py # Rebuild issue types DB
docs/                           # One-pager / PRD
```

Rebuild issue types after KB updates (with venv active):

```bash
python scripts/build_issue_types_kb.py
```

---

## Docs

- [One-pager](docs/ZAIN_NOTION_ONE_PAGER.md)
- [PRD](docs/ZAIN_NOTION_PRD.md)
