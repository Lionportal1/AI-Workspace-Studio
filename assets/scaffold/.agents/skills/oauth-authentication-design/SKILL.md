---
name: oauth-authentication-design
description: "Design secure OAuth/OIDC sessions, scopes and identity integration."
---

# Oauth Authentication Design

1. Distinguish authentication, authorization, user consent and token storage boundaries.
2. Choose the documented flow for the client type, including PKCE where applicable.
3. Validate state, redirects, issuer, audience, nonce, expiration and token revocation as relevant.
4. Plan scoped credentials, rotation, secure cookies, CSRF protection and recovery paths.
5. Test privilege escalation, expired tokens, account switching and sign-out behavior locally.
