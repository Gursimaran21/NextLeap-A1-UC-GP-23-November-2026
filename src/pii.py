"""PII redaction and safety checks.

Pure module (no pandas). Respect docs/constraints.md (C7).
"""

from __future__ import annotations

import re

REDACTED = "[REDACTED]"

# Order matters: URLs before handles, emails before generic @ patterns, phones before long numbers.
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_URL_RE = re.compile(r"\b(?:https?://|www\.)[^\s<>'\"]+", re.IGNORECASE)
_HANDLE_RE = re.compile(r"(?<!\w)@[A-Za-z0-9_]{2,30}\b")
# Indian phone numbers: +91, 0, or plain 10-digit mobile, with flexible separators.
_PHONE_RE = re.compile(
    r"(?<!\d)(?:\+91[\-\s]*|0[\-\s]*)?[6-9](?:[\-\s]*\d){9}(?!\d)"
)
# UPI-like ids: name@bankhandle (simple heuristic; runs after email redaction).
_UPI_RE = re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b")
# Standalone long numbers (order/ticket/account-like IDs): 8+ digits.
_LONG_NUMBER_RE = re.compile(r"(?<!\d)\d{8,}(?!\d)")
_REPEATED_REDACTED_RE = re.compile(r"(?:\[REDACTED\][\s,;:/-]*){2,}")


def _collapse_redacted(text: str) -> str:
    """Collapse repeated [REDACTED] markers into one."""
    prev = None
    out = text
    while prev != out:
        prev = out
        out = _REPEATED_REDACTED_RE.sub(REDACTED + " ", out)
    return re.sub(r"\s{2,}", " ", out).strip()


def redact_pii_counted(text: str) -> tuple[str, int]:
    """Redact PII from text and return (cleaned_text, replacement_count)."""
    if not isinstance(text, str) or not text:
        return ("" if text is None else str(text), 0)

    out = text
    total = 0
    patterns = [_EMAIL_RE, _URL_RE, _HANDLE_RE, _PHONE_RE, _UPI_RE, _LONG_NUMBER_RE]
    for pattern in patterns:
        out, n = pattern.subn(REDACTED, out)
        total += n

    collapsed = _collapse_redacted(out)
    return collapsed, total


def redact_pii(text: str) -> str:
    """Redact PII from text and return cleaned text."""
    cleaned, _ = redact_pii_counted(text)
    return cleaned


def contains_pii(text: str) -> bool:
    """Return True if text appears to contain PII patterns."""
    if not isinstance(text, str) or not text:
        return False
    patterns = [_EMAIL_RE, _URL_RE, _HANDLE_RE, _PHONE_RE, _UPI_RE, _LONG_NUMBER_RE]
    return any(p.search(text) for p in patterns)


if __name__ == "__main__":
    samples = [
        "Contact me at rahul.sharma@example.com or +91 98765 43210.",
        "Order 123456789 was bad, see https://example.com/ticket/1 and @supporthandle",
        "Pay to rahul@oksbi or call 09876543210",
        "Plain text with no personal information.",
    ]
    for s in samples:
        cleaned, n = redact_pii_counted(s)
        print("BEFORE:", s)
        print("AFTER :", cleaned)
        print("REDACTIONS:", n)
        print("---")
        assert not contains_pii(cleaned), f"PII remains: {cleaned}"
    print("no PII remains")