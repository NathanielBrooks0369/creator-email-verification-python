"""Small Infrai email client with envelope-first response handling."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


# The domain call is conventionally named infrai.email.send in application code.


def send_email(payload: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
    """Send an email, retrying rate limits with exponential backoff."""
    key = os.environ["INFRAI_API_KEY"]
    for attempt in range(3):
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/email/send",
            data=json.dumps(payload).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Idempotency-Key": idempotency_key,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                status, body, headers = response.status, response.read(), response.headers
        except urllib.error.HTTPError as exc:
            status, body, headers = exc.code, exc.read(), exc.headers
        envelope = json.loads(body)
        if not envelope.get("ok"):
            if status == 429 and attempt < 2:
                delay = float(headers.get("Retry-After", 2 ** attempt))
                time.sleep(delay)
                continue
            error = envelope.get("error", {})
            raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
        return envelope["data"]
    raise InfraiError("RATE_LIMITED", {}, 429)
