"""Env / LLM proxy settings for Zain."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_proxy_api_key: str
    llm_proxy_base_url: str
    llm_model: str


def get_settings() -> Settings:
    key = (os.getenv("LLM_PROXY_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
    base = (
        os.getenv("LLM_PROXY_BASE_URL") or "https://security-proxy.tamaratech.co/v1"
    ).strip()
    model = (
        os.getenv("LLM_MODEL") or "openrouter/deepseek/deepseek-v4-flash"
    ).strip()
    return Settings(
        llm_proxy_api_key=key,
        llm_proxy_base_url=base.rstrip("/"),
        llm_model=model,
    )


def has_api_key() -> bool:
    return bool(get_settings().llm_proxy_api_key)
