---
title: "{{Lesson Title}}"
module: "{{NN-module-slug}}"
lesson_number: {{NN}}
slug: "{{kebab-case-slug}}"
summary: "{{One-sentence description, ~150-160 chars, for SEO/index use}}"
tags: ["{{tag1}}", "{{tag2}}"]
dotnet_version: ".NET 10"
csharp_version: "C# 14"
last_reviewed: "{{YYYY-MM-DD}}"
prerequisites:
  - "[{{Prerequisite Lesson Title}}](../{{module}}/{{prereq-slug}}.md)"
next:
  - "[{{Next Lesson Title}}](../{{module}}/{{next-slug}}.md)"
---

# {{Lesson Title}}

<!--
AUTHORING NOTES (delete before publishing):
- Total target length: ~2,000-2,500 words (longer for Real-Time Example-heavy topics).
- Every code block must be a complete, runnable .NET 10 / C# 14 example with an exact
  "Console Output" block underneath it — verify by actually running it with `dotnet run`
  (or `dotnet run app.cs` for file-based single-file examples) before publishing.
- Real-Time Example section must extend one of the three recurring case-study domains
  (E-Commerce Order Processing / Banking-ATM / Library-Inventory Management) rather than
  invent a new one-off scenario, so the domain classes deepen across the curriculum.
- Only cite a "Latest" C# 14 / .NET 10 feature callout if it is actually version-gated —
  don't force a callout where the feature has existed since C# 8-12.
-->

## Introduction

Before reading this lesson, you should already be comfortable with **[{{Prerequisite Concept}}]({{relative-link-to-prereq}})**. In this lesson we build directly on that foundation to introduce **{{Topic}}**.

By the end of this lesson, you will be able to:

- {{Objective 1}}
- {{Objective 2}}
- {{Objective 3}}
- {{Objective 4}}
- {{Objective 5 (optional)}}

## {{Topic}} — A Layman's Perspective

{{Real-world analogy narrative, 3-5 paragraphs, ~400-500 words. Use a relatable scenario
(a blueprint/form, a factory process, a filing cabinet, a relay race, a restaurant kitchen,
a post office, etc.) that maps cleanly onto the technical concept's *behavior*, not just its
name. Avoid technical vocabulary entirely in this section. End with a short bridge sentence
connecting the analogy back to the programming concept.}}

## {{Topic}} — A Programming Language Perspective

{{Formal technical definition, ~200 words. Define the construct precisely, name the
relevant C# keyword(s)/syntax, and state where it sits in the type system or execution
model. Cite the current language/runtime version if a feature is version-gated, e.g.
"Introduced in C# 14, {{feature}} allows...".}}

## How to {{Create / Use / Declare}} {{Topic}} in C#

{{~150 words of prose walking through syntax rules before the example.}}

```mermaid
{{diagram-type e.g. classDiagram / flowchart / sequenceDiagram}}
    {{diagram content — keep to 5-10 nodes/edges max for readability}}
```
*Figure 1: {{One-line caption explaining what the diagram shows}}*

```csharp
// Program.cs — .NET 10 / C# 14
{{Complete, minimal, runnable example that isolates just this lesson's new syntax/concept.
Prefer top-level statements / file-based app style for beginner modules; a full Program.cs
with Main once classes/DI are introduced. Comment only where it teaches, not narrates.}}
```

**Console Output:**

```text
{{Exact expected output}}
```

{{~100-150 words explaining what happened, tying output back to the concept.}}

## Real-Time Example: {{Topic}} in {{E-Commerce / Banking-ATM / Library-Inventory}}

{{~350-450 words. A second, more comprehensive example that applies this lesson's concept
inside one of the three recurring case-study domains, extending the same classes introduced
in earlier lessons rather than starting a new scenario from scratch. State up front which
domain and which existing types are being extended, e.g. "We continue building on the
`Order` and `Customer` classes from the OOP module..."}}

```mermaid
{{Optional supporting diagram if it clarifies the real-time scenario's structure/flow.}}
```

```csharp
// Program.cs — .NET 10 / C# 14 — Real-Time Example
{{Complete, runnable, realistic example — production-shaped naming, meaningful business
logic, not a renamed toy. Include validation/error handling where a real system would.}}
```

**Console Output:**

```text
{{Exact expected output}}
```

{{~100 words tying the example back to why this matters in a real application.}}

## {{Contrast Pairing, e.g. "X vs Y"}}

{{~250 words contrasting the two concepts side by side.}}

```mermaid
{{Second/third diagram — often comparison-oriented: two boxes side by side, or a
"before/after" / "compile-time vs run-time" flowchart.}}
```
*Figure 2: {{Caption}}*

| Aspect | {{Concept A}} | {{Concept B}} |
|---|---|---|
| {{Definition}} | {{...}} | {{...}} |
| {{When created / evaluated}} | {{...}} | {{...}} |
| {{Memory / lifetime}} | {{...}} | {{...}} |
| {{Typical use case}} | {{...}} | {{...}} |

## Types of {{Topic}} in C#

C# supports several variants of {{topic}}, several of which are covered in their own dedicated lessons:

1. **[{{Variant 1 Name}}]({{relative-link-1}})** — {{one-line description}}.
2. **[{{Variant 2 Name}}]({{relative-link-2}})** — {{one-line description}}.
3. **[{{Variant 3 Name}}]({{relative-link-3}})** — {{one-line description}}.
4. **[{{Variant 4 Name}}]({{relative-link-4}})** — {{one-line description}}.
5. **[{{Variant 5 Name}}]({{relative-link-5}})** — {{one-line description}} *(optional 6th)*.

## What You've Learned & What's Next

{{2-3 sentence recap of the core takeaway.}}

Continue your learning journey with **[{{Next Lesson Title}}]({{relative-link-to-next}})**, where we cover {{one-line teaser}}.

---
*Applies to: .NET 10 / C# 14. Last reviewed {{YYYY-MM-DD}}.*
