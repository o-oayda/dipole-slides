#!/usr/bin/env python3
from html import escape
from pathlib import Path
import re
import sys


ACRONYMS = {"asa", "asm", "apska", "csiro", "emu", "ska"}


def readable_slug(path):
    stem = path.stem if path.is_file() else path.name
    words = re.sub(r"[-_]+", " ", stem).split()
    return " ".join(
        word.upper() if word.lower() in ACRONYMS else word.capitalize()
        for word in words
    )


def html_title(index):
    text = index.read_text(errors="ignore")
    match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return readable_slug(index.parent)
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return title or readable_slug(index.parent)


def section(title, items):
    if not items:
        return ""
    rows = "\n".join(
        f"""          <li class="talk">
            <a href="{escape(item["href"])}">
              <span class="talk-title">{escape(item["title"])}</span>
              <span class="talk-meta">{escape(item["format"])}</span>
            </a>
          </li>"""
        for item in items
    )
    anchor = title.lower()
    return f"""      <section aria-labelledby="{escape(anchor)}-heading">
        <h2 id="{escape(anchor)}-heading">{escape(title)}</h2>
        <ul class="talk-list">
{rows}
        </ul>
      </section>"""


def build_index(site):
    decks = [
        {
            "title": html_title(index),
            "href": f"{index.parent.name}/",
            "format": "reveal.js",
        }
        for index in sorted(site.glob("*/index.html"))
    ]

    pdfs = [
        {
            "title": readable_slug(pdf),
            "href": pdf.name,
            "format": "PDF",
        }
        for pdf in sorted(site.glob("*.pdf"))
    ]

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Slides</title>
    <style>
      :root {{
        --bg: #f7f6f3;
        --fg: #26383c;
        --muted: #657477;
        --line: #d8d3c8;
        --accent: #eb811b;
        --card: #ffffff;
      }}

      body {{
        background: var(--bg);
        color: var(--fg);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.5;
        margin: 0;
      }}

      main {{
        margin: 0 auto;
        max-width: 860px;
        padding: 4rem 1.5rem;
      }}

      header {{
        border-bottom: 1px solid var(--line);
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
      }}

      h1 {{
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.05;
        margin: 0 0 0.6rem;
      }}

      h2 {{
        font-size: 1rem;
        letter-spacing: 0.04em;
        margin: 2rem 0 0.75rem;
        text-transform: uppercase;
      }}

      p {{
        color: var(--muted);
        margin: 0;
      }}

      .talk-list {{
        display: grid;
        gap: 0.75rem;
        list-style: none;
        margin: 0;
        padding: 0;
      }}

      .talk {{
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 6px;
      }}

      .talk a {{
        color: inherit;
        display: grid;
        gap: 0.2rem;
        padding: 1rem 1.1rem;
        text-decoration: none;
      }}

      .talk a:hover,
      .talk a:focus-visible {{
        box-shadow: inset 4px 0 0 var(--accent);
        outline: none;
      }}

      .talk-title {{
        font-weight: 650;
      }}

      .talk-meta {{
        color: var(--muted);
        font-size: 0.95rem;
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1>Slides</h1>
        <p>Academic talks and conference presentations by Oliver Oayda.</p>
      </header>

{section("Interactive", decks)}

{section("PDF", pdfs)}
    </main>
  </body>
</html>
"""


def main():
    site = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_site")
    (site / "index.html").write_text(build_index(site))


if __name__ == "__main__":
    main()
