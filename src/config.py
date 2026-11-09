"""Env / LLM proxy settings for Zain."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class Settings:
    llm_proxy_api_key: str
    llm_proxy_base_url: str
    llm_model: str


def _secret(name: str, default: str = "") -> str:
    """Prefer env, then Streamlit Cloud secrets if available."""
    val = (os.getenv(name) or "").strip()
    if val:
        return val
    try:
        import streamlit as st  # type: ignore

        if hasattr(st, "secrets") and name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:  # noqa: BLE001
        pass
    return default


def get_settings() -> Settings:
    key = _secret("LLM_PROXY_API_KEY") or _secret("GEMINI_API_KEY")
    base = _secret(
        "LLM_PROXY_BASE_URL",
        "https://security-proxy.tamaratech.co/v1",
    )
    model = _secret("LLM_MODEL", "openrouter/deepseek/deepseek-v4-flash")
    return Settings(
        llm_proxy_api_key=key,
        llm_proxy_base_url=base.rstrip("/"),
        llm_model=model,
    )


def has_api_key() -> bool:
    return bool(get_settings().llm_proxy_api_key)
