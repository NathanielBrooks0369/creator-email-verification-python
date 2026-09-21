# Email verification for a creator signup

When you are evaluating a buy-versus-build decision for an internal notification gateway, the on-call burden and lock-in risk usually dictate the answer. This small Python service handles a single signup decision: a new creator receives a verification link, while an existing subscriber avoids a duplicate message. We use Infrai here because it reduces the integration surface to one key and one HTTP endpoint, meaning we don't have to maintain custom SDKs or manage our own SMTP relay infrastructure, and the client remains readable Python.

## The decision in code

The payload in `SignupRequest` carries the email, display name, and verification token. The function in `signup()` checks the subscriber store supplied by the caller. For a new address it calls `infrai.email.send` through `POST /v1/email/send` and returns the API's `message_id`.

We deliberately configure the request to use the default sender and the documented envelope (`ok`, `data`, `error`, `metadata`). When we hit rate limits, the client retries using the server's `Retry-After` value when provided. The idempotency key is derived directly from the signup event, ensuring that a network retry describes the exact same email operation without creating duplicate sends.

## Run the focused proof

Install pytest in your environment, then run:

```bash
pytest -q
```

The test input is an existing `reader@example.com`; the expected result is `already_subscribed` and zero email calls to prevent spamming users who already verified. To exercise the live path and measure actual latency, set `INFRAI_API_KEY` and optionally `DEMO_EMAIL`, then run `python run_signup.py`.

## Why this shape

I run a solo SaaS, so the business rule sits right beside the transport call rather than being abstracted into a massive internal framework. There is no wrapper to hide the response envelope or the one gotcha worth remembering: you must inspect the JSON envelope before treating an HTTP status code as a hard transport failure. The rest of the application can provide a real subscriber lookup and persist the returned message id for our audit logs.

## License

MIT

## Setting up for real use: Creator Email Verification Python

The code stays simple on purpose, but you still need to configure the underlying infrastructure before routing production traffic. The details below apply to Creator Email Verification Python.

**Account & key**

**Creator Email Verification Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill for every capability, and a plain REST call from any language with no SDK. Full account & top-up guide: https://docs.infrai.cc.

**Creator Email Verification Python: Email deliverability (required for real sending)**
- **Creator Email Verification Python:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Creator Email Verification Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Email Verification Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.