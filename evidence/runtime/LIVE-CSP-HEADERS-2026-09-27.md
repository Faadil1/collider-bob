# Live CSP / Security Headers Receipt — 2026-09-27

## Scope

Production response for:

https://collider-semantic-ci.faadil-casecraft.workers.dev/

Observed in Edge DevTools → Network → document request.

HTTP status was `304 Not Modified`, but the production response still exposed the relevant security headers.

## Observed response headers

```text
content-security-policy:
default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:;
connect-src 'self'; font-src 'self'; manifest-src 'self'; base-uri 'none';
form-action 'none'; frame-ancestors 'none'

cross-origin-opener-policy: same-origin
permissions-policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
referrer-policy: no-referrer
x-content-type-options: nosniff
x-frame-options: DENY
```

## Expected repository policy

These values match the shipped `demo-ui/_headers` policy.

## Verdict

**Live CSP / Security Headers: PROVEN**

The production page is serving the intended CSP and hardening headers.

This receipt does not claim a full penetration test or comprehensive security certification. It only proves that the configured page-level security headers are present on the live deployment.
