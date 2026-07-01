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


def format_day_month(value):
    parsed = date.fromisoformat(value)
    return f"{parsed.day} {parsed:%B}"


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
                "date_label": format_day_month(iso_date),
                "year": str(sort_date.year),
                "sort_date": sort_date,
            }
        )

    return sorted(enriched, key=lambda item: (item["sort_date"], item["event"]), reverse=True)


def render_action(action):
    return f"""                <a class="talk-action" href="{escape(action["href"])}">
                  <img src="{escape(action["icon"])}" alt="" width="16" height="16">
                  <span>{escape(action["label"])}</span>
                </a>"""


def talks_list(items):
    if not items:
        return ""
    years = []
    for item in items:
        if item["year"] not in years:
            years.append(item["year"])

    groups = []
    for year in years:
        rows = "\n".join(
            f"""            <li class="talk-card">
            <article class="talk-link">
              <span class="talk-marker" aria-hidden="true">&gt;</span>
              <span class="talk-body">
                <span class="talk-date">{escape(item["date_label"])}</span>
                <span class="talk-event">{escape(item["event"])}</span>
                <span class="talk-title">{escape(item["title"])}</span>
              </span>
              <span class="talk-actions" aria-label="Talk formats">
{chr(10).join(render_action(action) for action in item["actions"])}
              </span>
            </article>
          </li>"""
            for item in items
            if item["year"] == year
        )
        groups.append(
            f"""          <section class="talk-year-section" aria-labelledby="talks-{escape(year)}-heading">
            <h2 id="talks-{escape(year)}-heading">{escape(year)}</h2>
            <ul class="talk-list">
{rows}
            </ul>
          </section>"""
        )

    return f"""        <section class="talk-section" aria-label="Talks">
          <p class="prompt-line">$ find talks -type f | sort --key=year</p>
{chr(10).join(groups)}
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
            "actions": [
                {
                    "href": f"{index.parent.name}/",
                    "label": "reveal.js",
                    "icon": "assets/icons/reveal_favicon.svg",
                }
            ],
        }
        for index in sorted(site.glob("*/index.html"))
    ]

    for deck in decks:
        pdf = site / deck["href"] / "slides.pdf"
        if pdf.exists():
            deck["actions"].append(
                {
                    "href": f"{deck['href']}slides.pdf",
                    "label": "PDF",
                    "icon": "assets/icons/pdf_favicon.svg",
                }
            )

    pdfs = [
        {
            "title": readable_slug(pdf),
            "href": pdf.name,
            "actions": [
                {
                    "href": pdf.name,
                    "label": "PDF",
                    "icon": "assets/icons/pdf_favicon.svg",
                }
            ],
        }
        for pdf in sorted(site.glob("*.pdf"))
    ]

    talks = apply_metadata([*decks, *pdfs], load_metadata(metadata_path))
    return render_template(talks_list(talks), template)


def main():
    site = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_site")
    (site / "index.html").write_text(build_index(site))


if __name__ == "__main__":
    main()
