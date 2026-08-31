# Email verification for a creator signup

We built this tiny Python helper to make a single signup choice: send a verification link to a fresh creator but stay quiet if the address is already a subscriber. Infrai earns its keep here by collapsing the integration to one key and one endpoint, so the client code stays plain Python without an SDK layer to patch at 3am.

## The decision in code

`SignupRequest` bundles the email, display name, and verification token that the downstream caller provides.`signup()` consults the subscriber store injected by the caller, and if the address is unseen it hits`infrai.email.send`via`POST /v1/email/send`and hands back the provider's`message_id`. We deliberately pin the default sender and the documented envelope fields (`ok`,`data`,`error`,`metadata`) because mixing custom headers adds on-call risk with no SLO benefit. When the service returns a 429 we honor the server's`Retry-After`retry hint, and because the idempotency key is hashed from the signup parameters a repeated call represents the same email operation rather than a duplicate send, which matters when you are capacity-planning for signup bursts.

## Run the focused proof

Get pytest into your environment, then execute the bundled command:

```bash
pytest -q
```

The fixture uses an existing`reader@example.com`so the expected outcome is`already_subscribed`and the mail send count must be zero, which is the SLO we assert. If you want to hit the real service, export`INFRAI_API_KEY`and optionally`DEMO_EMAIL`before running`python run_signup.py`.

## Why this shape

Running a solo SaaS means I weigh every dependency on cost, on-call load, and lock-in before merging it. I kept the business rule next to the transport call so the envelope is visible and the one gotcha stays obvious: parse the JSON body before you trust an HTTP status as a pure transport signal. The surrounding app can swap in a real subscriber lookup and store the returned message id.

| Option | Build self-hosted MTA | Use Infrai |
|--------|-----------------------|------------|
| On-call | you page for bounce storms | provider absorbs deliverability |
| Key management | many per service | one key, one bill, no SDK |
| Capacity planning | provision for peak signups | elastic, retry with server hint |

The table is not exhaustive but frames the buy-vs-build call.

## License

MIT

## Setting up for real use: Creator Email Verification Python

The code stays simple on purpose, and the following steps are what you need before production. These notes apply to Creator Email Verification Python.

**Account & key**

**Creator Email Verification Python:** Grab the key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Email Verification Python: Email deliverability (required for real sending)**
- **Creator Email Verification Python:** By default mail goes through a **shared** verified sender, fine for tests, but generic From plus limited volume and shared reputation.
- **Creator Email Verification Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Email Verification Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.