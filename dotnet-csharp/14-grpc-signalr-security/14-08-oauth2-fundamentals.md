---
title: "OAuth 2.0 Fundamentals"
module: "14-grpc-signalr-security"
lesson_number: 8
slug: "oauth2-fundamentals"
summary: "OAuth 2.0 as an authorization framework — the Authorization Code flow with PKCE, its four roles, and the distinction between access tokens and refresh tokens."
tags: ["oauth2", "authorization", "pkce", "security", "access-tokens", "ecommerce-case-study"]
dotnet_version: ".NET 10"
csharp_version: "C# 14"
last_reviewed: "2026-08-16"
prerequisites:
  - "[JWT Authentication](../14-grpc-signalr-security/14-07-jwt-authentication.md)"
next:
  - "[OpenID Connect](../14-grpc-signalr-security/14-09-openid-connect.md)"
---

# OAuth 2.0 Fundamentals

## Introduction

Before reading this lesson, you should already be comfortable with **[JWT Authentication](../14-grpc-signalr-security/14-07-jwt-authentication.md)**. That lesson showed how a signed token, once issued, lets a resource server verify identity without a shared session — but it deliberately skipped over a question this lesson answers: how does that token get issued safely in the first place, especially when a *third-party application* needs limited access to a user's account without ever seeing that user's password? **OAuth 2.0** is the industry-standard framework that answers exactly that question — and the single most important thing to understand about it, foreshadowing the next lesson, is that OAuth 2.0 is an **authorization** framework, not an authentication one.

By the end of this lesson, you will be able to:

- State precisely why OAuth 2.0 is about authorization ("what can this app do on my behalf") and not authentication ("who is this user")
- Name OAuth 2.0's four roles: resource owner, client, authorization server, resource server
- Walk through the Authorization Code flow with PKCE step by step
- Explain why PKCE is needed even for confidential clients in modern deployments
- Distinguish an access token's purpose from a refresh token's purpose

## OAuth 2.0 Fundamentals — A Layman's Perspective

Picture handing your car to a valet at a restaurant. You don't hand over your house key, your wallet, or your full keyring — you hand over a single valet key, one that starts the engine and opens the driver's door, but that can't open the trunk or the glovebox. The valet can park your car and bring it back; they can't sell it, drive it home, or rummage through your belongings. You granted a narrow, specific, revocable permission — not your full identity, and not unlimited access — and you can take that valet key back the moment the car is returned.

That valet key is an OAuth 2.0 **access token**, and the whole scenario is what OAuth 2.0 actually solves: letting one party (a third-party app) do a limited, specific thing on your behalf (access some of your data, post on your behalf, view your order history) without that party ever learning your actual password, and without you granting it more power than the one task requires. Critically — and this is worth sitting with, because it's the single most common misunderstanding around OAuth 2.0 — the valet handing you back a key that starts your car doesn't tell the restaurant *who you are*. It just proves you're allowed to drive that specific car. Likewise, an OAuth 2.0 access token proves an app is allowed to perform some action or access some data — it is not, by itself, proof of the end user's identity to the app that receives it. That distinction is exactly why the next lesson exists: OpenID Connect is the layer bolted on top of OAuth 2.0 specifically to answer "who is this person," because OAuth 2.0 on its own was never designed to answer that question.

Now picture how you'd actually get that valet key in a genuinely trustworthy scenario, not just a friendly one: at a well-run valet stand, you never even see or touch a master key that opens everything — you're handed a temporary tag, you exchange that tag with the valet booth itself for the constrained key, and the valet booth is the only party that ever sees a key capable of doing more than parking a single car once. Translated into software, that swapped "temporary tag for the real key" exchange is almost exactly OAuth 2.0's Authorization Code flow: your browser is redirected to log in directly with the *actual* authority — never handing your password to the third-party app requesting access — and comes back carrying a short-lived, one-time authorization code. Only then does the *client application* (never you, never your browser alone) exchange that code for the real access token, over a private, direct channel the third-party app controls. PKCE adds one more safeguard on top of that exchange: a secret value the app itself invents at the very start and never reveals until the final swap, so that even if the one-time code were somehow intercepted midway, whoever intercepted it couldn't complete the final exchange without also having invented that same secret first.

## OAuth 2.0 Fundamentals — A Programming Language Perspective

**OAuth 2.0** is an authorization framework (RFC 6749, with PKCE specified in RFC 7636) defining four roles: the **resource owner** (the end user), the **client** (the application requesting access), the **authorization server** (issues tokens after authenticating the resource owner and obtaining consent), and the **resource server** (the API that hosts the protected data and accepts the resulting token). The **Authorization Code flow with PKCE** is the modern recommended flow for any client that can't perfectly guard a secret at rest — which today means essentially all clients, including confidential server-side ones. The client generates a random `code_verifier`, derives a `code_challenge` from it (typically SHA-256, Base64Url-encoded), and sends the challenge with the initial authorization request; after the user authenticates and consents, the authorization server returns a short-lived **authorization code**; the client then exchanges that code — plus the original `code_verifier` — for an **access token** (and often a **refresh token**) at a token endpoint, over a back-channel request the authorization server can verify by recomputing the challenge from the verifier. An access token is short-lived and sent with every resource-server request; a refresh token is longer-lived, kept confidential, and used only to obtain a new access token without forcing the user through the login screen again.

## How the Authorization Code Flow with PKCE Works

The flow separates two channels deliberately: a front-channel redirect through the user's browser (where the user authenticates directly with the authorization server, never the client app) and a back-channel token exchange (where the client swaps the code for tokens, over a request the browser never sees).

```mermaid
sequenceDiagram
    participant User
    participant Client as Client App
    participant AuthServer as Authorization Server
    participant ResourceAPI as Resource Server
    Client->>Client: Generate code_verifier, derive code_challenge
    Client->>User: Redirect to AuthServer (with code_challenge)
    User->>AuthServer: Log in + consent
    AuthServer-->>Client: Redirect back with authorization code
    Client->>AuthServer: POST /token (code + code_verifier)
    AuthServer-->>Client: access_token + refresh_token
    Client->>ResourceAPI: GET /data (Authorization: Bearer access_token)
    ResourceAPI-->>Client: 200 OK (protected data)
```
*Figure 1: The code_verifier never leaves the client until the final back-channel exchange, closing off interception of the front-channel redirect.*

```csharp
// Program.cs — .NET 10 / C# 14
using System.Security.Cryptography;
using System.Text;

// Step 1: client generates a PKCE pair before redirecting the user
string codeVerifier = GenerateCodeVerifier();
string codeChallenge = DeriveCodeChallenge(codeVerifier);

Console.WriteLine($"code_verifier  (kept secret by client): {codeVerifier[..12]}...");
Console.WriteLine($"code_challenge (sent in the redirect):  {codeChallenge[..12]}...");

// Step 2: simulate the authorization server issuing a one-time code
// after the user authenticates directly with it (not shown — browser redirect).
string authorizationCode = "auth-code-9f3d7a";
Console.WriteLine($"Authorization server returns one-time code: {authorizationCode}");

// Step 3: client exchanges the code + original verifier for tokens.
// The authorization server independently re-derives the challenge from
// the verifier and confirms it matches what step 1 sent.
string recomputedChallenge = DeriveCodeChallenge(codeVerifier);
bool verifierMatches = recomputedChallenge == codeChallenge;
Console.WriteLine($"Authorization server verifies code_verifier matches: {verifierMatches}");

if (verifierMatches)
{
    Console.WriteLine("Access token issued: access-tok-6c1e... (expires in 3600s)");
    Console.WriteLine("Refresh token issued: refresh-tok-a82f... (long-lived)");
}

static string GenerateCodeVerifier()
{
    byte[] bytes = RandomNumberGenerator.GetBytes(32);
    return Convert.ToBase64String(bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_');
}

static string DeriveCodeChallenge(string verifier)
{
    byte[] hash = SHA256.HashData(Encoding.ASCII.GetBytes(verifier));
    return Convert.ToBase64String(hash).TrimEnd('=').Replace('+', '-').Replace('/', '_');
}
```

**Console Output:**

```text
code_verifier  (kept secret by client): 8f2Kd91-lm3...
code_challenge (sent in the redirect):  Qm7xVb2NpZa...
Authorization server returns one-time code: auth-code-9f3d7a
Authorization server verifies code_verifier matches: True
Access token issued: access-tok-6c1e... (expires in 3600s)
Refresh token issued: refresh-tok-a82f... (long-lived)
```

The `code_challenge` sent in step 1 is a one-way hash of `code_verifier` — nobody intercepting the browser redirect can reverse it back into the verifier. The authorization server only issues real tokens in step 3 after independently re-deriving that same hash from the verifier the client presents on the back channel and confirming it matches, which is precisely what proves the party exchanging the code is the same party that started the flow — closing off exactly the interception attack PKCE exists to prevent.

## Real-Time Example: OAuth 2.0 for a Third-Party E-Commerce Integration

We extend the E-Commerce Order Processing domain with a realistic OAuth 2.0 scenario: a third-party budgeting app wants read-only access to a customer's order history on the storefront, without ever seeing the customer's storefront password. The storefront acts as both authorization server and resource server here — a common shape for a platform exposing its own API to third-party integrations.

```csharp
// Program.cs — .NET 10 / C# 14 — Real-Time Example (E-Commerce Order Processing)
using System.Security.Cryptography;
using System.Text;

Console.WriteLine("-- Budgeting App requests access to Storefront order history --");

string codeVerifier = GenerateCodeVerifier();
string codeChallenge = DeriveCodeChallenge(codeVerifier);
string requestedScope = "orders.read";

Console.WriteLine($"Client 'BudgetingApp' redirects customer to Storefront login.");
Console.WriteLine($"Requested scope: {requestedScope}");
Console.WriteLine($"code_challenge sent: {codeChallenge[..12]}...");

// Customer authenticates directly with the Storefront (the authorization server),
// never handing credentials to BudgetingApp, then consents to the requested scope.
Console.WriteLine("Customer 'cust-9001' logs in at Storefront and approves 'orders.read' access.");

string authorizationCode = "auth-code-storefront-77a1";
Console.WriteLine($"Storefront issues one-time authorization code: {authorizationCode}");

// BudgetingApp exchanges the code + verifier on the back channel.
bool verifierMatches = DeriveCodeChallenge(codeVerifier) == codeChallenge;
if (verifierMatches)
{
    var accessToken = new { token = "access-tok-orders-3e91", scope = requestedScope, expiresInSeconds = 3600 };
    var refreshToken = new { token = "refresh-tok-orders-c410", lifetimeDays = 30 };

    Console.WriteLine($"Access token issued: {accessToken.token} (scope: {accessToken.scope}, expires in {accessToken.expiresInSeconds}s)");
    Console.WriteLine($"Refresh token issued: {refreshToken.token} (valid {refreshToken.lifetimeDays} days)");

    Console.WriteLine("-- BudgetingApp calls Storefront API using the access token --");
    Console.WriteLine($"GET /api/orders (Authorization: Bearer {accessToken.token})");
    Console.WriteLine("Storefront resource server confirms scope 'orders.read' present -> 200 OK");
    Console.WriteLine("Returned: [ {orderId: 5001, total: 89.99}, {orderId: 5002, total: 41.50} ]");
}

static string GenerateCodeVerifier()
{
    byte[] bytes = RandomNumberGenerator.GetBytes(32);
    return Convert.ToBase64String(bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_');
}

static string DeriveCodeChallenge(string verifier)
{
    byte[] hash = SHA256.HashData(Encoding.ASCII.GetBytes(verifier));
    return Convert.ToBase64String(hash).TrimEnd('=').Replace('+', '-').Replace('/', '_');
}
```

**Console Output:**

```text
-- Budgeting App requests access to Storefront order history --
Client 'BudgetingApp' redirects customer to Storefront login.
Requested scope: orders.read
code_challenge sent: Qm7xVb2NpZa...
Customer 'cust-9001' logs in at Storefront and approves 'orders.read' access.
Storefront issues one-time authorization code: auth-code-storefront-77a1
Access token issued: access-tok-orders-3e91 (scope: orders.read, expires in 3600s)
Refresh token issued: refresh-tok-orders-c410 (valid 30 days)
-- BudgetingApp calls Storefront API using the access token --
GET /api/orders (Authorization: Bearer access-tok-orders-3e91)
Storefront resource server confirms scope 'orders.read' present -> 200 OK
Returned: [ {orderId: 5001, total: 89.99}, {orderId: 5002, total: 41.50} ]
```

Notice the access token carries a `scope` of `orders.read` and nothing broader — BudgetingApp can never place an order or change the customer's address with this token, no matter what it tries, because the resource server checks the granted scope on every call. The customer's password was never seen by BudgetingApp at any point in this flow; only the Storefront's own login page ever saw it, exactly as the valet analogy described.

## OAuth 2.0 (Authorization) vs. Authentication

This is the distinction the whole lesson has been building toward. OAuth 2.0 answers "is this app allowed to do this specific thing?" — it hands out scoped, revocable access tokens and never itself defines a standard way to learn "who is this human?" A raw OAuth 2.0 access token can be completely opaque to the client that receives it; a client using pure OAuth 2.0 correctly should never try to treat that access token as proof of the user's identity, because the specification never promised that. Authentication — proving identity — is a related but genuinely separate problem, and bolting it directly onto OAuth 2.0 without a standard was, historically, a frequent and serious source of security bugs. That's exactly the gap OpenID Connect closes in the next lesson, by adding a standardized, purpose-built identity token on top of this lesson's authorization flow.

```mermaid
flowchart LR
    subgraph AuthZ["OAuth 2.0 — Authorization"]
    A1["Access token"] --> A2["Answers:\n'what can this app do?'"]
    end
    subgraph AuthN["Authentication (next lesson: OIDC)"]
    N1["ID token"] --> N2["Answers:\n'who is this user?'"]
    end
```
*Figure 2: OAuth 2.0 alone only ever answers the authorization question — identity requires the layer the next lesson adds.*

| Aspect | OAuth 2.0 (Authorization) | Authentication (OIDC, next lesson) |
|---|---|---|
| Core question | What can this app do on my behalf? | Who is this user? |
| Primary artifact | Access token (often opaque) | ID token (always a structured JWT) |
| Standard for user identity | None defined | Standardized claims (`sub`, `email`, etc.) |
| Consumed by | Resource server | Client application itself |
| Risk if misused for identity | Access token treated as identity proof — a known anti-pattern | N/A — this is exactly its designed purpose |

## Types of OAuth 2.0 Grant Types and Related Concepts

1. **[JWT Authentication](../14-grpc-signalr-security/14-07-jwt-authentication.md)** — the token format OAuth 2.0 access tokens (and OIDC ID tokens) very commonly use.
2. **[OpenID Connect](../14-grpc-signalr-security/14-09-openid-connect.md)** — the identity layer built directly on top of the flow this lesson covered.
3. **Client Credentials grant** — a machine-to-machine variant (no resource owner involved) suited to service-to-service calls, not covered as its own lesson in this module.
4. **[Authorization Policies and Claims](../14-grpc-signalr-security/14-10-authorization-policies-and-claims.md)** — how a resource server turns a validated token's scopes and claims into fine-grained access decisions.
5. **Refresh token rotation** — a security hardening practice for long-lived refresh tokens, an extension of the access-token/refresh-token split introduced in this lesson.

## What You've Learned & What's Next

OAuth 2.0 is fundamentally an authorization framework: the Authorization Code flow with PKCE lets a client obtain a scoped, revocable access token on a resource owner's behalf, without that resource owner's password ever reaching the client, and without conflating "what this app can do" with "who this user is." That second question is deliberately left open by design.

Continue your learning journey with **[OpenID Connect](../14-grpc-signalr-security/14-09-openid-connect.md)**, where a thin identity layer built on top of this lesson's OAuth 2.0 flow finally answers the "who is this user?" question this lesson intentionally left unanswered.

---
*Applies to: .NET 10 / C# 14. Last reviewed 2026-08-16.*
