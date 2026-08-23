"""
mkdocs hook — fixes a Python-Markdown quirk that silently truncates headings.

Python-Markdown's core ATX heading processor treats *any* trailing run of
`#` characters as an optional closing sequence (the `# Heading #` style) and
strips it, even when the `#` is not preceded by whitespace. In this
curriculum that's destructive: every heading ending in "C#" (221 files, e.g.
"# Classes and Objects in C#") loses its final character and renders as
"...in C" instead of "...in C#".

Rather than reach into Markdown's internals (fragile across versions), this
hook runs before parsing and escapes just the offending pattern: a heading
line ending in "<word-character>#" with no preceding space. Escaping it as
"\\#" makes Python-Markdown treat it as a literal character instead of a
closing sequence, and the escape is invisible in the rendered output.
Genuine closed headings ("# Title #", with a space before the closing
hashes) are untouched — that behavior is left as-is.

Registered in mkdocs.yml via `hooks: [mkdocs_hashheader_fix.py]`, which
mkdocs imports directly from the config file's directory — no install step,
no PYTHONPATH.
"""

import re

# Heading line, ending in a word character immediately followed by a single
# '#' and nothing else (optionally trailing whitespace).
_TRAILING_HASH_RE = re.compile(r"^(#{1,6}\s+.*[A-Za-z0-9_])#\s*$")


def on_page_markdown(markdown, page, config, files):
    lines = markdown.split("\n")
    changed = False
    for i, line in enumerate(lines):
        m = _TRAILING_HASH_RE.match(line)
        if m:
            lines[i] = m.group(1) + "\\#"
            changed = True
    return "\n".join(lines) if changed else markdown
