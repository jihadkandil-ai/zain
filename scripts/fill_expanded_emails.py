"""Fill missing email_en / email_ar in data/emails_db_expanded.json via Tamara LLM Proxy.

Resumable. Uses parallel single-item translates (more reliable than large batches).
"""

from __future__ import annotations

import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "emails_db_expanded.json"
PROGRESS_PATH = ROOT / "data" / "emails_db_expanded.fill_progress.json"

sys.path.insert(0, str(ROOT))
from src.config import get_settings  # noqa: E402

WORKERS = 6
CHUNK = 6
MAX_RETRIES = 3

SYSTEM = """You are a Tamara Care localization assistant.
Translate ONE customer-care email between English and Arabic.

Rules:
- Preserve ALL placeholders exactly (e.g. {customer_name}, {order_id}, {arn}).
- Preserve links, emails, phone numbers, and IDs.
- Keep Tamara Care tone: empathetic, clear, professional.
- Arabic: natural Gulf/Care Arabic. English: clear Care English.
- Do NOT invent facts, order IDs, amounts, or names.
- Return ONLY JSON: {"id":"...","email_en":"...","email_ar":"..."}
- Fill the missing language; keep the source language text unchanged.
"""


def load_db() -> dict[str, Any]:
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def save_db(data: dict[str, Any]) -> None:
    emails = data.get("emails") or []
    data["total_templates"] = len(emails)
    data["arabic_count"] = sum(1 for e in emails if str(e.get("email_ar") or "").strip())
    data["english_count"] = sum(1 for e in emails if str(e.get("email_en") or "").strip())
    data["bilingual_count"] = sum(
        1
        for e in emails
        if str(e.get("email_en") or "").strip() and str(e.get("email_ar") or "").strip()
    )
    DB_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def missing_jobs(emails: list[dict[str, Any]]) -> list[dict[str, str]]:
    jobs: list[dict[str, str]] = []
    for e in emails:
        eid = str(e.get("id") or "")
        en = str(e.get("email_en") or "").strip()
        ar = str(e.get("email_ar") or "").strip()
        if en and ar:
            continue
        if ar and not en:
            jobs.append({"id": eid, "direction": "ar_to_en", "title": str(e.get("title") or ""), "source": ar})
        elif en and not ar:
            jobs.append({"id": eid, "direction": "en_to_ar", "title": str(e.get("title") or ""), "source": en})
    return jobs


def extract_json(text: str) -> dict[str, Any]:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("not a json object")
    # unwrap {"translations":[...]} if model wraps anyway
    if "email_en" not in data and "email_ar" not in data:
        rows = data.get("translations") or data.get("items") or []
        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            data = rows[0]
    return data


def translate_one(client: OpenAI, model: str, job: dict[str, str]) -> dict[str, str]:
    payload = {
        "id": job["id"],
        "title": job["title"],
        "direction": job["direction"],
        "source_text": job["source"],
    }
    user = (
        "Translate this Care email. "
        "direction ar_to_en => produce English in email_en and copy Arabic source to email_ar. "
        "direction en_to_ar => produce Arabic in email_ar and copy English source to email_en.\n\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user},
                ],
                timeout=50.0,
                max_tokens=2200,
            )
            raw = extract_json(resp.choices[0].message.content or "")
            en = str(raw.get("email_en") or "").strip()
            ar = str(raw.get("email_ar") or "").strip()
            if job["direction"] == "ar_to_en":
                if not en:
                    raise ValueError("empty english")
                return {"id": job["id"], "email_en": en, "email_ar": job["source"]}
            if not ar:
                raise ValueError("empty arabic")
            return {"id": job["id"], "email_en": job["source"], "email_ar": ar}
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(0.8 * attempt)
    raise RuntimeError(f"{job['id']}: {last_err}")


def apply_one(emails: list[dict[str, Any]], row: dict[str, str]) -> bool:
    for e in emails:
        if str(e.get("id")) != row["id"]:
            continue
        changed = False
        if row.get("email_en") and not str(e.get("email_en") or "").strip():
            e["email_en"] = row["email_en"]
            changed = True
        if row.get("email_ar") and not str(e.get("email_ar") or "").strip():
            e["email_ar"] = row["email_ar"]
            changed = True
        if str(e.get("email_en") or "").strip() and str(e.get("email_ar") or "").strip():
            e["source_lang"] = "bilingual"
        return changed
    return False


def write_progress(bilingual: int, missing: int, note: str = "") -> None:
    PROGRESS_PATH.write_text(
        json.dumps(
            {
                "bilingual": bilingual,
                "missing": missing,
                "note": note,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def counts(emails: list[dict[str, Any]]) -> tuple[int, int]:
    bi = sum(
        1
        for e in emails
        if str(e.get("email_en") or "").strip() and str(e.get("email_ar") or "").strip()
    )
    miss = sum(
        1
        for e in emails
        if not str(e.get("email_en") or "").strip() or not str(e.get("email_ar") or "").strip()
    )
    return bi, miss


def main() -> None:
    settings = get_settings()
    if not settings.llm_proxy_api_key:
        raise SystemExit("LLM_PROXY_API_KEY missing")

    client = OpenAI(api_key=settings.llm_proxy_api_key, base_url=settings.llm_proxy_base_url)
    model = settings.llm_model

    data = load_db()
    jobs = missing_jobs(data["emails"])
    bi, miss = counts(data["emails"])
    print(f"start bilingual={bi} missing={miss} workers={WORKERS} model={model}", flush=True)
    write_progress(bi, miss, "started")

    failed: list[str] = []

    while True:
        data = load_db()
        jobs = missing_jobs(data["emails"])
        if not jobs:
            break
        # skip permanently failed in this run
        jobs = [j for j in jobs if j["id"] not in failed]
        if not jobs:
            break

        chunk = jobs[:CHUNK]
        results: list[dict[str, str]] = []
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futs = {pool.submit(translate_one, client, model, j): j for j in chunk}
            for fut in as_completed(futs):
                job = futs[fut]
                try:
                    results.append(fut.result())
                    print(f"ok {job['id']}", flush=True)
                except Exception as exc:  # noqa: BLE001
                    failed.append(job["id"])
                    print(f"FAIL {job['id']}: {exc}", flush=True)

        if results:
            data = load_db()
            applied = 0
            for row in results:
                if apply_one(data["emails"], row):
                    applied += 1
            save_db(data)
            bi, miss = counts(data["emails"])
            write_progress(bi, miss, f"applied={applied} failed_run={len(failed)}")
            print(f"saved applied={applied} bilingual={bi} missing={miss}", flush=True)
        else:
            # all failed in chunk — avoid tight loop
            time.sleep(1.0)

    data = load_db()
    bi, miss = counts(data["emails"])
    write_progress(bi, miss, f"finished failed={len(failed)}")
    print(f"DONE bilingual={bi} missing={miss} failed={len(failed)}", flush=True)
    if failed:
        print("failed_ids", failed[:40], flush=True)


if __name__ == "__main__":
    main()
