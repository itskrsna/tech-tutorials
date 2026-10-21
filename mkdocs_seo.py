"""
mkdocs hook — gives every lesson its own <meta name="description">.

Lessons carry a `summary:` front-matter key, but Material only reads
`description:`, so all 393 pages fell back to the generic site_description —
poor for search snippets and link previews. Copy `summary` into `description`
when the page doesn't define one.
"""


def on_page_markdown(markdown, page, config, files):
    summary = page.meta.get("summary")
    if summary and not page.meta.get("description"):
        page.meta["description"] = str(summary)
    return markdown
