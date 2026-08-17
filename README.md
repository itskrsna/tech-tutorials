# Tech Tutorials

A from-scratch, continuously-current technical tutorial library — built to match the depth of the best-known tutorial sites, but without the years-stale content most of them carry.

**📖 Read it online:** https://itskrsna.github.io/tech-tutorials/

---

## What's Inside

| Stack | Status | Modules | Lessons |
|---|---|---|---|
| **.NET / C#** | ✅ Complete | 18 | 393 |
| Java | 🔜 Planned | — | — |
| Python | 🔜 Planned | — | — |
| JavaScript / TypeScript (React, Angular) | 🔜 Planned | — | — |

Each stack gets the same treatment: fundamentals through advanced, current language/runtime versions, and real, deployable examples — not just syntax demos.

## Philosophy

Every lesson in this library follows the same template, so the series reads as one coherent course rather than a pile of disconnected blog posts:

1. **Introduction** — what you need to already know, and what you'll be able to do after
2. **Layman's Perspective** — a real-world analogy, zero jargon
3. **Technical Perspective** — the formal, precise definition
4. **How To** — a minimal, runnable code example with exact output
5. **Real-Time Example** — the same concept applied inside a running case study, not a toy
6. **Comparison** — the concept contrasted against its nearest alternative
7. **Types/Variants** — a map of related lessons
8. **What's Next** — where the thread continues

Three recurring case studies — an **E-Commerce Order Processing** system, a **Banking/ATM** system, and a **Library/Inventory Management** system — grow across every module. By the time you reach the cloud-deployment lessons, you're not looking at a new toy example; you're looking at the same domain models you started with, finally running at scale.

Content is versioned against **current** language/runtime releases (e.g. .NET 10 / C# 14), and lessons explicitly call out what's genuinely new versus what's been true for years — the thing most tutorial content quietly gets wrong by never being updated.

## C#/.NET Curriculum Structure

| Module | Focus | Lessons |
|---|---|---|
| 00 | Orientation | 3 |
| 01 | Fundamentals | 25 |
| 02 | Object-Oriented Programming | 38 |
| 03 | Collections & Generics | 22 |
| 04 | LINQ | 22 |
| 05 | Exception Handling | 10 |
| 06 | Delegates & Events | 10 |
| 07 | Concurrency, Parallelism & Async | 30 |
| 08 | Memory Management | 10 |
| 09 | File I/O & Serialization | 10 |
| 10 | ASP.NET Core | 22 |
| 11 | EF Core | 15 |
| 12 | Advanced Concepts (SOLID, GoF patterns, performance, architecture) | 46 |
| 13 | Reflection, Source Generators & Low-Level C# | 15 |
| 14 | gRPC, SignalR & Security | 18 |
| 15 | Containers, Blazor & MAUI | 18 |
| 16 | Azure for .NET Developers | 78 |
| 17 | What's Next | 1 |

Full lesson-by-lesson index: [`dotnet-csharp/README.md`](dotnet-csharp/README.md)

## Running It Locally

```bash
git clone https://github.com/itskrsna/tech-tutorials.git
cd tech-tutorials

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
mkdocs serve
```

Then open http://127.0.0.1:8000.

The site is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and deploys automatically to GitHub Pages on every push to `main`.

## Roadmap

- Java, Python, and JavaScript/TypeScript curricula, following the same template and case-study pattern
- A dedicated testing/TDD module (xUnit, mocking, integration testing)
- Deeper Blazor/MAUI coverage
- AI integration lessons (`Microsoft.Extensions.AI`) once the API surface stabilizes

## Found an Issue?

If a lesson has an error, a stale claim, or a broken link, please [open an issue](https://github.com/itskrsna/tech-tutorials/issues).

## Support This Project

This library is free to read and will stay that way. If it's helped you, here's how to support continued work on it:

- ⭐ **Star this repo** — helps others find it
- 💖 **Sponsor** — a GitHub Sponsors button will appear here once the sponsor profile is set up ([`.github/FUNDING.yml`](.github/FUNDING.yml) has placeholders ready to fill in)
- 📣 **Share it** with someone learning .NET

The site may carry unobtrusive, clearly-disclosed ads in the future to help fund new content — this README will be updated if and when that changes.
