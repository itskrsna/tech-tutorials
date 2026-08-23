# CLAUDE.md

Guidance for future Claude Code sessions working in this repo.

## What this repo is

A published tutorial library, not an application — no build step in the software
sense, no tests, no runtime code. It's an [MkDocs](https://www.mkdocs.org/) +
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) documentation
site: 393 lessons across 18 modules under `dotnet-csharp/`, currently targeting
**.NET 10 (LTS)** and **C# 14**. Two more stacks (Java, Python) are planned per the
root `README.md` but not yet started.

## Preview locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

`site/` and `.venv/` are gitignored. Before pushing anything that touches
`mkdocs.yml`, cross-lesson links, or the module index, run a strict-mode build to
catch broken references across all 393 files:

```bash
mkdocs build --strict --site-dir /tmp/site-check
```

**Known, pre-existing `--strict` warnings** (unrelated to config/styling, both are
lesson-content bugs, not fixed here — see Known issues below):
- `03-collections-generics/03-20-icomparable-and-icomparer.md` links to a filename
  that doesn't exist (`03-08-sortedlist-and-sorteddictionary.md`; the real file is
  `03-06-sorteddictionary-and-sortedlist.md`).
- `16-azure-for-dotnet-developers/16-51-building-azure-dashboards.md` has a
  self-link to an anchor that doesn't match the heading's actual generated ID
  (the heading contains an em dash, which slugifies differently than the link
  assumes).

Because of these two, CI runs a **non-strict** `mkdocs build` as its safety net
(see Deployment below), not `--strict`. If you fix both, feel free to switch the
CI step to `--strict` for stronger guarantees going forward.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy-docs.yml`:
`pip install` → `mkdocs build` (sanity check) → `mkdocs gh-deploy --force --clean`
→ force-pushes the built site to the `gh-pages` branch → served at
<https://itskrsna.github.io/tech-tutorials/>.

**There is no staging step or PR preview — a bad commit to `main` is live within
minutes.** GitHub Pages also caches assets aggressively, so after a deploy,
hard-reload (Cmd+Shift+R) before concluding a change didn't take effect.

## Non-obvious structure

- `docs_dir: dotnet-csharp` in `mkdocs.yml` means the curriculum folder *is* the
  site root — `dotnet-csharp/README.md` becomes the homepage (`index.html`), and
  `site_url` / `edit_uri` are written relative to that. Adding a second stack
  (Java/Python) means moving `docs_dir` up to a parent directory and relocating
  all 393 files, not just adding a sibling folder.
- **No `nav:` block in `mkdocs.yml`.** Lesson order comes entirely from
  zero-padded numeric filename prefixes (`02-01-…`, `16-78-…`) — default
  alphabetical sort already produces the right sequence. Section (module) labels
  come from a one-line `title:` in each module folder's `.pages` file
  (`mkdocs-awesome-pages-plugin`). **Adding a module ⇒ add a `.pages` file**, or
  the sidebar falls back to the raw directory slug (e.g. `07-concurrency-parallel-async`).
  Never set `order_by: title` in a `.pages` file — lesson titles have no numbers,
  so that would scramble the sequence alphabetically.
- `dotnet-csharp/.pages` (root) pins `README.md` and `curriculum-status.md` to
  the top of the nav; everything else falls through via the `...` wildcard.
- **`navigation.sections` must stay off** in `theme.features`. It was on
  originally and, combined with 393 pages, forced the *entire* lesson tree open
  and expanded on every single page — the original complaint that started this
  cleanup. The current setup uses `navigation.prune` instead: only the active
  module's lessons render in the sidebar HTML.

## Lesson conventions

Every lesson follows `dotnet-csharp/_template/lesson-template.md` (excluded from
the build via `exclude_docs`): a fixed set of frontmatter keys (`title`, `module`,
`lesson_number`, `slug`, `summary`, `tags`, `dotnet_version`, `csharp_version`,
`last_reviewed`, `prerequisites`, `next`), an 8-section body (Introduction →
Layman's Perspective → Programming Language Perspective → How-To → Real-Time
Example → Comparison → Types/Variants → What's Next), ~2,000–2,500 words, every
code block runnable with an exact Console Output block, and one of three
recurring case-study domains (E-Commerce Order Processing, Banking/ATM,
Library/Inventory Management) for the Real-Time Example section.

`tags`, `prerequisites`, and `next` are present in every lesson's frontmatter but
are **currently inert** — no `tags` plugin consumes `tags`, and no template
renders `prerequisites`/`next` as links. They're written by convention/for future
use, not by any active theme feature.

## Styling

All visual customization lives in **`dotnet-csharp/stylesheets/extra.css`**,
wired via `extra_css` in `mkdocs.yml` (the path is relative to `docs_dir`, so no
`dotnet-csharp/` prefix in the config). It targets Material 9.x class names.
Load-bearing decisions worth preserving when editing it:

- **Scheme tokens live on `[data-md-color-scheme="…"]` (i.e. `<body>`), never on
  `:root`.** Material sets its palette CSS variables at the body level via that
  attribute, so a `:root`-level override loses. Every `--tt-*` color is defined
  twice — once under `default` (light), once under `slate` (dark) — check any
  color change in **both** schemes.
- `.md-grid` is widened to `84rem` (Material's default is `61rem`) while prose
  elements are separately capped at `--tt-measure: 76ch`. That split — wide
  layout, narrow paragraphs — is the whole design: it lets 4–6 column tables and
  Mermaid diagrams use real width without making body text hard to read.
- `.md-typeset__table` is forced to `display: block`. Material's default
  `display: inline-block` on that wrapper makes tables shrink-to-fit their
  content and silently ignore `width: 100%` — this override is what lets tables
  actually use the widened column. (Note: Material adds `.md-typeset__scrollwrap`
  / `.md-typeset__table` to tables **client-side via JS** at page load, so they
  never appear in `mkdocs build`'s raw HTML output — only check this in an actual
  browser, not by grepping the built files.)
- Only font weights 400 and 700 exist in the type scale. Material's `theme.font`
  fetches just `300/400/700` from Google Fonts for `Inter` (text) and
  `JetBrains Mono` (code) — a `600` would be browser-synthesized and look muddy.
- Code ligatures are explicitly disabled (`font-variant-ligatures: none` etc.).
  JetBrains Mono ligates `=>`, `!=`, `>=` into single glyphs by default, which
  would misrepresent the actual C# source characters being taught.

## Known issues (pre-existing, not fixed here — out of scope for a styling pass)

- The two broken cross-references listed under Preview locally above.
- `mkdocs_hashheader_fix.py` (see next section) fixes a *rendering* bug, not a
  content bug — no lesson files were edited to produce that fix.

## `mkdocs_hashheader_fix.py`

A small mkdocs **hook** (registered via `hooks:` in `mkdocs.yml`, not a Markdown
extension) that works around a Python-Markdown quirk: its core ATX heading
processor strips *any* trailing run of `#` characters as an optional closing
sequence — even when not preceded by whitespace. In a C# curriculum this
silently truncated 221 files' headings, e.g. `# Classes and Objects in C#`
rendered as "Classes and Objects in C" with the final character eaten. The hook
runs before parsing and escapes only that exact pattern (`\#`), leaving genuine
closed headings (`# Title #`) and everything else untouched. This required no
edits to any of the 393 lesson files — it's a pure rendering-pipeline fix.

## Gotchas

- **Mermaid works out of the box** — Material lazily loads `mermaid@11` from
  unpkg via its own JS bundle. Don't add a `mermaid2`/mermaid mkdocs plugin.
- **Do not add** `pymdownx.smartsymbols`, `pymdownx.caret`, `pymdownx.tilde`, or
  `pymdownx.mark`. They rewrite `!=`/`-->`/`(c)`, claim `^`/`~`, or claim `==`
  respectively — all of which appear in C# prose outside code spans
  (`arr[^1]`, `~Finalizer()`, operator discussions) and would get silently
  corrupted across hundreds of files.
- `navigation.indexes` is enabled but currently inert — no module folder has an
  `index.md`. It becomes useful (clickable module landing pages) if those are
  ever added.
- `content.code.annotate` is not enabled — zero `# (1)!` code annotations exist
  in any lesson yet. Add it the day the first one is written.

## Dependencies

`requirements.txt` is pinned deliberately
(`mkdocs-material>=9.6,<10`, `mkdocs-awesome-pages-plugin>=2.10,<3`) so a future
major release can't silently restyle or break the live site — `extra.css`
targets Material 9.x class names specifically. To bump: change the pin,
`mkdocs serve`, check the sidebar and a table-heavy lesson (e.g.
`02-oop/02-01-classes-and-objects.md`) in both light and dark mode, then commit.
