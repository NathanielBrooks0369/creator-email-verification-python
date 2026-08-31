from src import signup_flow
from src.signup_flow import SignupRequest, signup


def test_existing_subscriber_does_not_receive_second_link(monkeypatch):
    calls = []
    monkeypatch.setattr(signup_flow, "send_email", lambda *args, **kwargs: calls.append(args))
    result = signup(SignupRequest("reader@example.com", "Mina", "token"), lambda _: True)
    assert result.status == "already_subscribed"
    assert calls == []

