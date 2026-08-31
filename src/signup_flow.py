from dataclasses import dataclass
from html import escape
from typing import Callable

from .infrai_email import send_email


@dataclass(frozen=True)
class SignupRequest:
    email: str
    creator_name: str
    verification_token: str


@dataclass(frozen=True)
class SignupResult:
    status: str
    message_id: str | None


def signup(request: SignupRequest, subscriber_exists: Callable[[str], bool]) -> SignupResult:
    """Register a creator and send a verification link only for a new address."""
    if subscriber_exists(request.email):
        return SignupResult("already_subscribed", None)
    link = f"https://creator.example/verify?token={escape(request.verification_token)}"
    data = send_email(
        {
            "to": request.email,
            "subject": "Verify your creator account",
            "html": f"<p>Hi {escape(request.creator_name)},</p><p><a href=\"{link}\">Verify your email</a></p>",
        },
        idempotency_key=f"signup-verification:{request.email}:{request.verification_token}",
    )
    return SignupResult("verification_sent", data["message_id"])

