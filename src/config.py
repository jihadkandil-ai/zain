"""Environment and model configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROXY_BASE_URL = "https://security-proxy.tamaratech.co/v1"
DEFAULT_MODEL = "openrouter/deepseek/deepseek-v4-flash"


@dataclass(frozen=True)
class Settings:
    """LLM access prefers Tamara LLM Proxy; optional direct Gemini for local experiments."""

    llm_proxy_api_key: str
    llm_proxy_base_url: str
    llm_model: str
    gemini_api_key: str


def get_settings() -> Settings:
    # Prefer LLM proxy virtual key; keep GEMINI_API_KEY as legacy alias for the same key.
    proxy_key = (
        os.getenv("LLM_PROXY_API_KEY", "").strip()
        or os.getenv("GEMINI_API_KEY", "").strip()
    )
    model = (
        os.getenv("LLM_MODEL", "").strip()
        or os.getenv("GEMINI_MODEL", "").strip()
        or DEFAULT_MODEL
    )
    return Settings(
        llm_proxy_api_key=proxy_key,
        llm_proxy_base_url=(
            os.getenv("LLM_PROXY_BASE_URL", DEFAULT_PROXY_BASE_URL).strip()
            or DEFAULT_PROXY_BASE_URL
        ),
        llm_model=model,
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
    )


def has_api_key() -> bool:
    return bool(get_settings().llm_proxy_api_key)


def provider_label() -> str:
    settings = get_settings()
    if settings.llm_proxy_api_key:
        if "tamara" in settings.llm_proxy_base_url.lower():
            return "Tamara LLM Proxy"
        return "LLM Proxy"
    return "none"
