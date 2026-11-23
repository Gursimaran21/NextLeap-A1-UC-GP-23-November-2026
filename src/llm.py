"""Thin LLM wrapper with deterministic offline fallback.

Respects docs/constraints.md. No API key => callers use deterministic logic.
"""

from __future__ import annotations

import json
import os
from typing import Any

_client = None
_working_model: str | None = None
_last_used_llm = False

_MODEL_CANDIDATES = [
    os.getenv("GEMINI_MODEL", "").strip(),
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]


def _candidates() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for m in _MODEL_CANDIDATES:
        if m and m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _get_client() -> Any:
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from google import genai  # type: ignore
    except Exception:
        return None
    try:
        _client = genai.Client(api_key=api_key)
    except Exception:
        _client = None
    return _client


def available() -> bool:
    return _get_client() is not None


def active_model() -> str:
    return _working_model or (_candidates()[0] if _candidates() else "offline")


def used() -> bool:
    return _last_used_llm


def generate(system: str, prompt: str, temperature: float = 0.2) -> str | None:
    """Return model text, or None if unavailable/failing."""
    global _working_model, _last_used_llm
    _last_used_llm = False
    client = _get_client()
    if client is None:
        return None

    order = ([_working_model] if _working_model else []) + _candidates()
    seen: set[str] = set()
    for model in order:
        if not model or model in seen:
            continue
        seen.add(model)
        try:
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"system_instruction": system, "temperature": temperature},
            )
            text = getattr(resp, "text", None)
            if text:
                _working_model = model
                _last_used_llm = True
                return text.strip()
        except Exception:
            continue
    return None


def _strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.endswith("```"):
            s = s[:-3]
    return s.strip().removeprefix("json").strip()


def generate_json(system: str, prompt: str, temperature: float = 0.0) -> dict[str, Any] | None:
    """Generate strict JSON. Returns dict or None on failure."""
    sys = system + "\nReturn ONLY valid JSON. No markdown fences."
    raw = generate(sys, prompt, temperature=temperature)
    for attempt in range(2):
        if not raw:
            return None
        s = _strip_fences(raw)
        try:
            obj = json.loads(s)
            return obj if isinstance(obj, dict) else None
        except Exception:
            start, end = s.find("{"), s.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    obj = json.loads(s[start : end + 1])
                    return obj if isinstance(obj, dict) else None
                except Exception:
                    pass
        if attempt == 0:
            raw = generate(sys, prompt + "\n\nYour previous response was not valid JSON. Return ONLY a JSON object.", temperature)
    return None
