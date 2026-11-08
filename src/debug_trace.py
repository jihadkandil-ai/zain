"""Optional debug traces (off by default). Set ZAIN_DEBUG=1 to enable shell logs."""

from __future__ import annotations

import os
import sys
from typing import Any


def zain_debug(message: str, **fields: Any) -> None:
    if os.getenv("ZAIN_DEBUG", "").strip() not in {"1", "true", "TRUE", "yes", "YES"}:
        return
    extra = ""
    if fields:
        parts = []
        for key, value in fields.items():
            text = str(value).replace("\n", "\\n")
            if len(text) > 220:
                text = text[:220] + "…"
            parts.append(f"{key}={text}")
        extra = " | " + " ".join(parts)
    print(f"[ZAIN_DEBUG] {message}{extra}", file=sys.stderr, flush=True)
