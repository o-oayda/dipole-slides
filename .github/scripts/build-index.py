#!/usr/bin/env python3
from html import escape
import json
from pathlib import Path
import re
import sys
from datetime import date


ACRONYMS = {"asa", "asm", "apska", "csiro", "emu", "ska"}
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = SCRIPT_DIR.parent / "templates" / "index.html"
DEFAULT_METADATA = SCRIPT_DIR.parent / "talks.json"


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


def format_month(value):
    parsed = date.fromisoformat(value)
    return f"{parsed:%B} {parsed:%Y}"


def load_metadata(path=DEFAULT_METADATA):
    if not path.exists():
        raise FileNotFoundError(f"Missing talk metadata: {path}")
    try:
        metadata = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid talk metadata JSON in {path}: {error}") from error
    if not isinstance(metadata, dict):
        raise ValueError(f"Talk metadata must be a JSON object: {path}")
    return metadata


def apply_metadata(items, metadata):
    missing = [item["href"] for item in items if item["href"] not in metadata]
    if missing:
        missing_list = "\n".join(f"  - {href}" for href in missing)
        raise ValueError(f"Missing talk metadata for:\n{missing_list}")

    known_hrefs = {item["href"] for item in items}
    extra = sorted(set(metadata) - known_hrefs)
    if extra:
        extra_list = "\n".join(f"  - {href}" for href in extra)
        raise ValueError(f"Talk metadata exists for unknown slides:\n{extra_list}")

    enriched = []
    for item in items:
        entry = metadata[item["href"]]
        if not isinstance(entry, dict):
            raise ValueError(f"Metadata for {item['href']} must be an object")

        event = entry.get("event")
        title = entry.get("title")
        iso_date = entry.get("date")
        if not event or not isinstance(event, str):
            raise ValueError(f"Metadata for {item['href']} must include an event")
        if not title or not isinstance(title, str):
            raise ValueError(f"Metadata for {item['href']} must include a title")
        if not iso_date or not isinstance(iso_date, str):
            raise ValueError(f"Metadata for {item['href']} must include a date")

        try:
            sort_date = date.fromisoformat(iso_date)
        except ValueError as error:
            raise ValueError(
                f"Metadata date for {item['href']} must be YYYY-MM-DD: {iso_date}"
            ) from error

        enriched.append(
            {
                **item,
                "event": event,
                "title": title,
                "date": iso_date,
                "date_label": format_month(iso_date),
                "sort_date": sort_date,
            }
        )

    return sorted(enriched, key=lambda item: (item["sort_date"], item["event"]), reverse=True)


def section(title, items):
    if not items:
        return ""
    rows = "\n".join(
        f"""          <li class="talk-card">
            <a class="talk-link" href="{escape(item["href"])}">
              <span class="talk-marker" aria-hidden="true">&gt;</span>
              <span class="talk-body">
                <span class="talk-date">{escape(item["date_label"])}</span>
                <span class="talk-event">{escape(item["event"])}</span>
                <span class="talk-title">{escape(item["title"])}</span>
              </span>
            </a>
          </li>"""
        for item in items
    )
    anchor = title.lower()
    prompt = (
        "find talks -type f -name '*.html'"
        if title == "Interactive"
        else "find talks -type f -name '*.pdf'"
    )
    return f"""        <section class="talk-section" aria-labelledby="{escape(anchor)}-heading">
          <p class="prompt-line">$ {escape(prompt)}</p>
          <h2 id="{escape(anchor)}-heading">{escape(title)}</h2>
          <ul class="talk-list">
{rows}
          </ul>
        </section>"""


def render_template(sections, template=DEFAULT_TEMPLATE):
    if not template.exists():
        raise FileNotFoundError(f"Missing index template: {template}")
    return template.read_text().replace("{{ sections }}", sections)


def build_index(site, template=DEFAULT_TEMPLATE, metadata_path=DEFAULT_METADATA):
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

    talks = apply_metadata([*decks, *pdfs], load_metadata(metadata_path))
    decks = [item for item in talks if item["format"] == "reveal.js"]
    pdfs = [item for item in talks if item["format"] == "PDF"]

    sections = "\n\n".join(
        content
        for content in (section("Interactive", decks), section("PDF", pdfs))
        if content
    )
    return render_template(sections, template)


def main():
    site = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_site")
    (site / "index.html").write_text(build_index(site))


if __name__ == "__main__":
    main()
