#!/usr/bin/env python3
"""
scopus_sync.py — Fetch publications from Scopus for a given Author ID
and merge them into assets/publications.json.

Usage:
    python .github/scripts/scopus_sync.py

Required environment variables:
    SCOPUS_API_KEY   — Elsevier API key
    SCOPUS_AUTHOR_ID — Scopus numeric Author ID (e.g. 36437362600)
    PUBLICATIONS_JSON — path to publications.json (default: assets/publications.json)
"""

import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_KEY = os.environ.get("SCOPUS_API_KEY", "")
AUTHOR_ID = os.environ.get("SCOPUS_AUTHOR_ID", "36437362600")
PUB_JSON_PATH = Path(os.environ.get("PUBLICATIONS_JSON", "assets/publications.json"))

BASE_URL = "https://api.elsevier.com/content/search/scopus"
PAGE_SIZE = 25
REQUEST_DELAY = 0.5   # seconds between requests (rate limiting)
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0   # seconds (doubles on each retry)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def _get(url: str, params: dict) -> dict:
    """GET with simple retry/backoff on transient errors."""
    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/json",
    }
    delay = RETRY_BACKOFF
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 500, 502, 503, 504):
                print(f"  [retry {attempt}/{MAX_RETRIES}] HTTP {resp.status_code}, "
                      f"waiting {delay:.0f}s…")
                time.sleep(delay)
                delay *= 2
                continue
            resp.raise_for_status()
        except requests.RequestException as exc:
            last_err = exc
            print(f"  [retry {attempt}/{MAX_RETRIES}] Request error: {exc}, "
                  f"waiting {delay:.0f}s…")
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(
        f"Failed after {MAX_RETRIES} retries. Last error: {last_err}"
    )


# ---------------------------------------------------------------------------
# Scopus fetch
# ---------------------------------------------------------------------------
def fetch_all_documents() -> list[dict]:
    """Retrieve all documents for AUTHOR_ID from Scopus, handling pagination."""
    print(f"Fetching documents for Scopus Author ID: {AUTHOR_ID}")
    docs = []
    start = 0

    while True:
        params = {
            "query": f"AU-ID({AUTHOR_ID})",
            "field": (
                "eid,doi,title,publicationName,coverDate,creator,"
                "author,citedby-count,subtype,subtypeDescription"
            ),
            "count": PAGE_SIZE,
            "start": start,
            "sort": "-coverDate",
        }
        data = _get(BASE_URL, params)
        results = data.get("search-results", {})
        entries = results.get("entry", [])

        if not entries:
            break

        # Check for API-level error
        if len(entries) == 1 and "error" in entries[0]:
            print(f"  API error: {entries[0]['error']}")
            break

        docs.extend(entries)
        print(f"  Retrieved {len(docs)} docs so far (page start={start})…")

        total_str = results.get("opensearch:totalResults", "0")
        total = int(total_str) if total_str.isdigit() else 0
        start += PAGE_SIZE

        if start >= total:
            break

        time.sleep(REQUEST_DELAY)

    print(f"Total documents fetched from Scopus: {len(docs)}")
    return docs


# ---------------------------------------------------------------------------
# Mapping Scopus → publication schema
# ---------------------------------------------------------------------------
def _extract_authors(entry: dict) -> str:
    """Build a semicolon-separated authors string from the Scopus entry."""
    # Prefer the full author list when available
    authors_list = entry.get("author", [])
    if isinstance(authors_list, list) and authors_list:
        names = []
        for a in authors_list:
            given = a.get("given-name", "")
            surname = a.get("surname", "")
            if surname:
                if given:
                    names.append(f"{surname}, {given[0]}.")
                else:
                    names.append(surname)
        if names:
            return "; ".join(names)
    # Fallback: creator field
    creator = entry.get("dc:creator", "")
    return creator


def _extract_year(entry: dict) -> int | None:
    """Extract publication year from coverDate (YYYY-MM-DD)."""
    cover = entry.get("coverDate", "") or entry.get("prism:coverDate", "")
    if cover and len(cover) >= 4:
        try:
            return int(cover[:4])
        except ValueError:
            pass
    return None


def _extract_doi(entry: dict) -> str:
    """Extract and normalise DOI."""
    doi = entry.get("prism:doi", "") or entry.get("dc:identifier", "")
    if doi.upper().startswith("DOI:"):
        doi = doi[4:]
    return doi.strip()


def _extract_eid(entry: dict) -> str:
    return entry.get("eid", "").strip()


def scopus_to_pub(entry: dict) -> dict:
    """Map a Scopus search entry to the publications.json schema."""
    doi = _extract_doi(entry)
    link = f"https://doi.org/{doi}" if doi else entry.get("prism:url", "")
    return {
        "authors": _extract_authors(entry),
        "year": _extract_year(entry),
        "title": entry.get("dc:title", "").strip(),
        "venue": (entry.get("prism:publicationName", "") or "").strip(),
        "doi": doi,
        "link": link,
        "pdf": "",
        "tech": [],
        "project": "Miscellaneous",
        "_eid": _extract_eid(entry),   # internal; stripped before writing
    }


# ---------------------------------------------------------------------------
# De-duplication keys
# ---------------------------------------------------------------------------
def _norm_doi(doi: str) -> str:
    return doi.lower().strip().lstrip("https://doi.org/").lstrip("http://doi.org/")


def _norm_title(title: str) -> str:
    """Lowercase, remove punctuation & extra spaces for fuzzy matching."""
    s = title.lower()
    s = unicodedata.normalize("NFD", s)
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def make_keys(pub: dict) -> tuple[str, str, str]:
    """Return (doi_key, eid_key, title_year_key) for a publication."""
    doi_key = _norm_doi(pub.get("doi", ""))
    eid_key = pub.get("_eid", "").strip()
    title_key = _norm_title(pub.get("title", ""))
    year = str(pub.get("year", ""))
    title_year_key = f"{title_key}|{year}"
    return doi_key, eid_key, title_year_key


# ---------------------------------------------------------------------------
# Merge logic
# ---------------------------------------------------------------------------
def merge_publications(existing: list[dict], new_from_scopus: list[dict]) -> tuple[list[dict], int]:
    """
    Merge new_from_scopus into existing list.
    Returns (merged_list, count_added).
    Existing entries are never overwritten (tech/project preserved).
    """
    # Build lookup sets from existing entries
    existing_dois: set[str] = set()
    existing_eids: set[str] = set()
    existing_title_years: set[str] = set()

    for pub in existing:
        doi_k, eid_k, ty_k = make_keys(pub)
        if doi_k:
            existing_dois.add(doi_k)
        if eid_k:
            existing_eids.add(eid_k)
        if ty_k.strip("|"):
            existing_title_years.add(ty_k)

    added = 0
    merged = list(existing)  # start with all existing

    for pub in new_from_scopus:
        doi_k, eid_k, ty_k = make_keys(pub)

        # Check for duplicates
        is_dup = False
        if doi_k and doi_k in existing_dois:
            is_dup = True
        elif eid_k and eid_k in existing_eids:
            is_dup = True
        elif ty_k.strip("|") and ty_k in existing_title_years:
            is_dup = True

        if is_dup:
            continue

        # Strip internal _eid before adding
        clean = {k: v for k, v in pub.items() if k != "_eid"}
        merged.append(clean)
        added += 1

        # Update lookup sets
        if doi_k:
            existing_dois.add(doi_k)
        if eid_k:
            existing_eids.add(eid_k)
        if ty_k.strip("|"):
            existing_title_years.add(ty_k)

        print(f"  + Adding: {clean.get('year', '?')} — {clean.get('title', '')[:80]}")

    return merged, added


def sort_publications(pubs: list[dict]) -> list[dict]:
    """Sort by year descending (None last), then title ascending."""
    def sort_key(p):
        year = p.get("year")
        y = -year if year is not None else 1  # None → 1 (after negatives)
        title = (p.get("title") or "").lower()
        return (y, title)
    return sorted(pubs, key=sort_key)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not API_KEY:
        print("ERROR: SCOPUS_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # Load existing publications
    if PUB_JSON_PATH.exists():
        with open(PUB_JSON_PATH, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"Loaded {len(existing)} existing publications from {PUB_JSON_PATH}")
    else:
        existing = []
        print(f"No existing file at {PUB_JSON_PATH}; starting fresh.")

    # Fetch from Scopus
    raw_docs = fetch_all_documents()
    scopus_pubs = [scopus_to_pub(d) for d in raw_docs]

    # Merge
    merged, added = merge_publications(existing, scopus_pubs)
    print(f"\nMerge complete: {added} new publication(s) added, "
          f"{len(existing)} existing entries preserved.")

    if added == 0:
        print("No updates — publications.json unchanged.")
        # Write an env file hint for the workflow
        _set_output("ADDED_COUNT", "0")
        return

    # Sort
    sorted_pubs = sort_publications(merged)

    # Write back
    with open(PUB_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted_pubs, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Written {len(sorted_pubs)} publications to {PUB_JSON_PATH}")

    _set_output("ADDED_COUNT", str(added))


def _set_output(name: str, value: str):
    """Write a GitHub Actions output variable if GITHUB_OUTPUT is set."""
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as fh:
            fh.write(f"{name}={value}\n")
    else:
        print(f"::set-output name={name}::{value}")


if __name__ == "__main__":
    main()
