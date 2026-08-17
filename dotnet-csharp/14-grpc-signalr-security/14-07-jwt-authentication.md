---
title: "JWT Authentication"
module: "14-grpc-signalr-security"
lesson_number: 7
slug: "jwt-authentication"
summary: "How JSON Web Tokens pack a signed, self-contained identity into a compact string, and how AddJwtBearer validates that identity without a server-side session."
tags: ["jwt", "authentication", "aspnet-core", "security", "stateless-auth", "ecommerce-case-study"]
dotnet_version: ".NET 10"
csharp_version: "C# 14"
last_reviewed: "2026-08-16"
prerequisites:
  - "[Cookie Authentication in ASP.NET Core](../14-grpc-signalr-security/14-06-cookie-authentication.md)"
next:
  - "[OAuth 2.0 Fundamentals](../14-grpc-signalr-security/14-08-oauth2-fundamentals.md)"
---

# JWT Authentication

## Introduction

Before reading this lesson, you should already be comfortable with **[Cookie Authentication in ASP.NET Core](../14-grpc-signalr-security/14-06-cookie-authentication.md)**. That lesson's cookie worked because the server kept the authority to make sense of it and the browser always talked to the same origin that issued it. Neither of those assumptions holds for a mobile app calling an API, a single-page app calling a separate backend domain, or one microservice calling another — exactly the gap this lesson's **JSON Web Token (JWT)** fills, by making the token itself carry everything a server needs to trust it, with no session store involved at all.

By the end of this lesson, you will be able to:

- Describe a JWT's three-part structure — header, payload, signature — and why each part exists
- Explain what "stateless authentication" means and why it matters for APIs and microservices
- Configure JWT validation with `AddAuthentication().AddJwtBearer()`
- Generate a signed JWT for a user and validate it on incoming requests
- Decide when JWTs are the better fit over cookies, and when they aren't

## JWT Authentication — A Layman's Perspective

Picture a wristband handed out at a large music festival, the kind with three visible bands printed on it, tamper-evident and impossible to peel off and reattach without it looking obviously damaged. The first band tells the gate staff what *kind* of wristband it is — a single-day pass, say. The second band, printed right next to it, states the actual facts: which day, which gate this ticket-holder is allowed through, whether they're VIP. And the third part isn't information at all — it's the festival's own tamper-evident seal, pressed on by a machine only the festival organizers control, proving the first two bands weren't altered after the fact by anyone else.

Here's the crucial part: gate staff at *any* entrance can check that wristband on the spot, just by looking at it, without radioing back to a central office to confirm the person's identity every single time. The wristband itself already contains everything needed — who it's for, what it permits, and proof it's genuine. No lookup, no phone call, no shared list to consult. That's a JWT. The header is the "what kind of wristband" part, the payload is the "these are the actual facts" part — a user's ID, their roles, an expiration time — and the signature is the tamper-evident seal, cryptographically produced by whoever issued the token, checkable by anyone holding the matching key, without ever contacting the issuer again.

This is precisely why JWTs suit exactly the situations cookies don't: a chain of ticket booths, or a network of gates run by different companies at the same venue, none of which share a single central desk they could all phone to verify a guest. Each gate independently checks the seal itself. In software terms, that's a set of independent microservices, or an API being called by a mobile app that isn't a browser and has no session cookie mechanism to lean on — each service validates the token's signature locally, with the exact same math, and none of them need to ask a shared session database whether the bearer is who they claim to be.

The tradeoff follows the analogy just as directly: once a wristband is issued, festival security can't simply "erase" it from a list somewhere — it stays valid, readable, and honored at every gate until it physically expires (or someone spots it and confiscates it directly, gate by gate). That's the flip side of a JWT's independence: revoking one early is hard precisely because no gate had to ask permission to honor it in the first place. Short expiration times, paired with a separate refresh mechanism, are how real systems live with that tradeoff — a theme this lesson returns to and OAuth 2.0's access-token-versus-refresh-token split, in the next lesson, formalizes properly.

## JWT Authentication — A Programming Language Perspective

A **JSON Web Token** is a compact, URL-safe string composed of three Base64Url-encoded segments separated by dots: `header.payload.signature`. The header names the signing algorithm (commonly `HS256` or `RS256`); the payload is a JSON object of **claims** — standard ones like `sub` (subject/user ID) and `exp` (expiration), plus any application-defined claims; the signature is a cryptographic hash of the header and payload, computed with a secret or private key, that lets any holder of the corresponding public key or shared secret verify the token wasn't altered. **Stateless authentication** means the server validates a request purely by checking that signature and the token's claims — no database row, no in-memory session, no server-side state at all. In ASP.NET Core, `AddAuthentication().AddJwtBearer(options => ...)` registers a scheme that extracts the token from the `Authorization: Bearer <token>` header, validates its signature and expiration against `TokenValidationParameters`, and populates `HttpContext.User` from its claims — the same `ClaimsPrincipal` destination cookie authentication used, arrived at by a completely different, session-free mechanism.

## How to Generate and Validate a JWT in ASP.NET Core

Producing a JWT means building a `ClaimsIdentity`, signing it with a symmetric key using `JwtSecurityTokenHandler`, and returning the resulting string; validating one means configuring `AddJwtBearer` with the same key so incoming tokens can be checked without any external lookup.

```mermaid
sequenceDiagram
    participant Client
    participant AuthAPI as Auth Endpoint
    participant ResourceAPI as Protected Endpoint
    Client->>AuthAPI: POST /token (credentials)
    AuthAPI->>AuthAPI: Validate credentials, build signed JWT
    AuthAPI-->>Client: 200 OK { token: "header.payload.signature" }
    Client->>ResourceAPI: GET /data (Authorization: Bearer <token>)
    ResourceAPI->>ResourceAPI: Verify signature + expiration locally
    ResourceAPI-->>Client: 200 OK (no session lookup performed)
```
*Figure 1: The protected endpoint never contacts the auth endpoint again — it verifies the token entirely on its own.*

```csharp
// Program.cs — .NET 10 / C# 14
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

const string SigningKey = "this-is-a-demo-signing-key-32-bytes-min!";
var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(SigningKey));

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = key
        };
    });
builder.Services.AddAuthorization();

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();

app.MapPost("/token", (string username) =>
{
    var claims = new[] { new Claim(ClaimTypes.Name, username) };
    var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
    var token = new JwtSecurityToken(
        claims: claims,
        expires: DateTime.UtcNow.AddMinutes(30),
        signingCredentials: credentials);

    string jwt = new JwtSecurityTokenHandler().WriteToken(token);
    return Results.Ok(new { token = jwt });
});

app.MapGet("/secure-data", (HttpContext http) =>
    Results.Ok($"Hello, {http.User.Identity!.Name} — this required no session lookup."))
    .RequireAuthorization();

app.Run();
```

**Console Output:**

*Note: as with all authentication lessons, this shows HTTP request/response traffic rather than a console-app trace.*

```text
POST /token?username=alice
< HTTP/1.1 200 OK
{ "token": "eyJhbGciOiJIUzI1NiIs...header.eyJ1bmlxdWVfbmFtZSI6ImFsaWNlIn0...payload.4f9c...signature" }

GET /secure-data
> Authorization: Bearer eyJhbGciOiJIUzI1NiIs...header.eyJ1bmlxdWVfbmFtZSI6ImFsaWNlIn0...payload.4f9c...signature
< HTTP/1.1 200 OK
Hello, alice — this required no session lookup.

GET /secure-data
> (no Authorization header)
< HTTP/1.1 401 Unauthorized
```

`/token` never stores anything server-side — the returned string *is* the entire session. `/secure-data` proves the point: it authenticates the request purely by verifying the `Bearer` token's signature and expiration against the same `SymmetricSecurityKey`, with zero database or in-memory lookup. Remove the `Authorization` header entirely and the middleware rejects the request with `401` before the endpoint delegate even runs — identical to how `[Authorize]` behaved with cookies, but arrived at without any server-held state.

## Real-Time Example: JWT Authentication for the E-Commerce Order API

We extend the E-Commerce Order Processing domain with a mobile shopping app calling the store's order API directly — a genuinely cross-origin, non-browser client, exactly where JWTs outperform cookies. The customer authenticates once against an auth endpoint and attaches the resulting token to every subsequent call to place or check on an order, including from a completely different service than the one that issued the token.

```csharp
// Program.cs — .NET 10 / C# 14 — Real-Time Example (E-Commerce Order Processing)
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

const string SigningKey = "shared-signing-key-across-order-services-32b!";
var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(SigningKey));

var builder = WebApplication.CreateBuilder(args);
builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = false,
        ValidateAudience = false,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = key
    });
builder.Services.AddAuthorization();

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();

var orders = new Dictionary<int, string> { [5001] = "Shipped", [5002] = "Processing" };

app.MapPost("/auth/token", (string customerId) =>
{
    var claims = new[] { new Claim(ClaimTypes.NameIdentifier, customerId) };
    var token = new JwtSecurityToken(
        claims: claims,
        expires: DateTime.UtcNow.AddHours(1),
        signingCredentials: new SigningCredentials(key, SecurityAlgorithms.HmacSha256));
    return Results.Ok(new { token = new JwtSecurityTokenHandler().WriteToken(token) });
});

app.MapGet("/orders/{orderId:int}/status", (int orderId, HttpContext http) =>
{
    string customerId = http.User.FindFirstValue(ClaimTypes.NameIdentifier)!;
    if (!orders.TryGetValue(orderId, out string? status))
    {
        return Results.NotFound($"Order {orderId} not found.");
    }
    return Results.Ok($"Customer '{customerId}' — Order {orderId} status: {status}");
})
.RequireAuthorization();

app.Run();
```

**Console Output:**

```text
POST /auth/token?customerId=cust-9001
< HTTP/1.1 200 OK
{ "token": "eyJhbGciOiJIUzI1NiIs...header.eyJuYW1laWQiOiJjdXN0LTkwMDEifQ...payload.a71e...signature" }

GET /orders/5001/status
> Authorization: Bearer eyJhbGciOiJIUzI1NiIs...header.eyJuYW1laWQiOiJjdXN0LTkwMDEifQ...payload.a71e...signature
< HTTP/1.1 200 OK
Customer 'cust-9001' — Order 5001 status: Shipped
```

This is the shape most modern order-processing systems actually use: the mobile app's auth call might hit an entirely separate identity service, while the `/orders` endpoint above runs in a different microservice altogether — yet as long as both share the same signing key (or, more realistically at scale, the same trusted issuer's public key), the order service validates the customer's identity with zero shared session infrastructure between the two. That decoupling is precisely why JWTs, not cookies, are the default choice for API-driven and microservice architectures.

## JWT (Stateless) vs. Cookie (Stateful) Authentication

The fundamental split is where trust lives. A cookie is a reference the issuing server can revoke at will because the server owns the record behind it; a JWT is a self-contained credential that any service holding the verification key can check unilaterally, at the cost of not being able to revoke a single token early without extra machinery (a blocklist, or simply keeping tokens short-lived). Cookies also depend on the browser's automatic, same-origin cookie jar; JWTs are attached explicitly by client code via the `Authorization` header, which is exactly why they work identically from a browser, a mobile app, or a server-to-server call — none of which need to be the same origin as the issuer.

```mermaid
flowchart TB
    subgraph Stateful["Cookie: Stateful"]
    S1["Server holds session record"] --> S2["Cookie merely references it"]
    S2 --> S3["Revoke anytime\nby deleting the record"]
    end
    subgraph Stateless["JWT: Stateless"]
    J1["Token carries its own claims"] --> J2["Any verifier checks\nsignature independently"]
    J2 --> J3["Revoke only by\nwaiting for expiry (or a blocklist)"]
    end
```
*Figure 2: A cookie points at trust the server keeps; a JWT carries its own trust wherever it goes.*

| Aspect | Cookie Authentication | JWT Authentication |
|---|---|---|
| State location | Server-side session | Entirely inside the token |
| Revocation | Immediate | Requires expiry or a blocklist |
| Cross-origin / cross-service | Poor | Excellent |
| Attached by | Browser automatically | Client code, explicitly (`Authorization` header) |
| Typical consumer | Server-rendered web app | SPA, mobile app, microservice API |

## Types of Token-Based Authentication Concepts

1. **[Cookie Authentication in ASP.NET Core](../14-grpc-signalr-security/14-06-cookie-authentication.md)** — the stateful alternative this lesson contrasts against.
2. **[OAuth 2.0 Fundamentals](../14-grpc-signalr-security/14-08-oauth2-fundamentals.md)** — the authorization framework that standardizes how tokens like this lesson's JWT get issued in the first place.
3. **[OpenID Connect](../14-grpc-signalr-security/14-09-openid-connect.md)** — adds a standardized identity token on top of OAuth 2.0, often itself a JWT.
4. **[Authorization Policies and Claims](../14-grpc-signalr-security/14-10-authorization-policies-and-claims.md)** — how the claims carried inside a JWT drive fine-grained access rules.
5. **Refresh tokens** — the companion mechanism (covered as part of OAuth 2.0's token model in the next lesson) that lets short-lived JWTs be renewed without forcing a full re-login.

## What You've Learned & What's Next

A JWT packs a signed, self-contained identity into three dot-separated segments, letting any service holding the verification key authenticate a request without a shared session store — the trait that makes JWTs the default for APIs, mobile clients, and microservices, at the cost of harder early revocation than a cookie allows.

Continue your learning journey with **[OAuth 2.0 Fundamentals](../14-grpc-signalr-security/14-08-oauth2-fundamentals.md)**, where we step back from JWTs themselves to the standardized authorization framework that governs how tokens like this one actually get issued, delegated, and refreshed.

---
*Applies to: .NET 10 / C# 14. Last reviewed 2026-08-16.*
