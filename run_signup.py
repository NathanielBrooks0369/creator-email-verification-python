import os

from src.signup_flow import SignupRequest, signup


def main() -> None:
    if "INFRAI_API_KEY" not in os.environ:
        raise SystemExit("Set INFRAI_API_KEY before running")
    recipient = os.environ.get("DEMO_EMAIL", "you@example.com")
    result = signup(SignupRequest(recipient, "Mina", "demo-token"), lambda _: False)
    print(result)


if __name__ == "__main__":
    main()

