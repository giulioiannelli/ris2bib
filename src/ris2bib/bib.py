"""
BibTeX → RIS conversion utilities.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Union

import bibtexparser

from .core import make_key

BIBTYPE_TO_RIS = {
    "article": "JOUR",
    "journal": "JOUR",
    "inproceedings": "CONF",
    "conference": "CONF",
    "incollection": "CHAP",
    "inbook": "CHAP",
    "book": "BOOK",
    "techreport": "RPRT",
    "report": "RPRT",
    "phdthesis": "THES",
    "mastersthesis": "THES",
    "unpublished": "UNPB",
}


def _split_authors(raw: str) -> List[str]:
    # Split on ' and ' respecting simple BibTeX author list syntax.
    parts = [p.strip() for p in raw.replace("\n", " ").split(" and ") if p.strip()]
    return parts


def _pages_to_sp_ep(pages: str) -> tuple[Optional[str], Optional[str]]:
    if not pages:
        return None, None
    m = re.split(r"[-–—]+", pages)
    if len(m) >= 2:
        return m[0].strip() or None, m[1].strip() or None
    return pages.strip(), None


def _entry_to_ris(entry: Dict[str, str]) -> str:
    raw_type = entry.get("ENTRYTYPE", "article").lower()
    ris_type = BIBTYPE_TO_RIS.get(raw_type, "GEN")

    lines: List[str] = [f"TY  - {ris_type}"]

    authors = _split_authors(entry.get("author", ""))
    for author in authors:
        lines.append(f"AU  - {author}")

    title = entry.get("title")
    if title:
        lines.append(f"TI  - {title}")

    journal = entry.get("journal") or entry.get("journaltitle")
    if journal:
        lines.append(f"JO  - {journal}")

    booktitle = entry.get("booktitle")
    if booktitle:
        lines.append(f"T2  - {booktitle}")

    year = entry.get("year")
    if year:
        lines.append(f"PY  - {year}")

    volume = entry.get("volume")
    if volume:
        lines.append(f"VL  - {volume}")

    number = entry.get("number")
    if number:
        lines.append(f"IS  - {number}")

    pages = entry.get("pages")
    sp, ep = _pages_to_sp_ep(pages or "")
    if sp:
        lines.append(f"SP  - {sp}")
    if ep:
        lines.append(f"EP  - {ep}")

    doi = entry.get("doi")
    if doi:
        lines.append(f"DO  - {doi}")

    url = entry.get("url")
    if url:
        lines.append(f"UR  - {url}")

    publisher = entry.get("publisher")
    if publisher:
        lines.append(f"PB  - {publisher}")

    issn = entry.get("issn")
    if issn:
        lines.append(f"SN  - {issn}")

    lines.append("ER  - ")
    return "\n".join(lines)


def _bib_entry_to_rec(entry: Dict[str, str]) -> Dict[str, List[str]]:
    """Map a BibTeX entry into a minimal RIS-like record for key generation."""
    rec: Dict[str, List[str]] = {}
    title = entry.get("title")
    if title:
        rec["TI"] = [title]
        rec["T1"] = [title]
    year = entry.get("year")
    if year:
        rec["PY"] = [str(year)]
    authors = _split_authors(entry.get("author", ""))
    if authors:
        rec["AU"] = authors
    return rec


def rekey_bib_entries(entries: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Regenerate BibTeX keys for a list of entries using the RIS key style.

    Deduplicates by appending a, b, c... if the same key repeats.
    """
    seen: Dict[str, int] = {}
    for entry in entries:
        rec = _bib_entry_to_rec(entry)
        base_key = make_key(rec)
        count = seen.get(base_key, 0)
        key = base_key if count == 0 else f"{base_key}{chr(ord('a') + count)}"
        seen[base_key] = count + 1
        entry["ID"] = key
    return entries


def rekey_bib_files(
    inputs: Sequence[Union[str, Path]],
    *,
    on_warning: Optional[Callable[[str], None]] = None,
) -> str:
    """Load one or more .bib files, regenerate keys, and return BibTeX text."""
    warn = on_warning or (lambda msg: None)
    entries: List[Dict[str, str]] = []

    for inp in inputs:
        path = Path(inp)
        if not path.exists():
            warn(f"File not found: {path}")
            continue
        with path.open("r", encoding="utf-8") as handle:
            try:
                bib_db = bibtexparser.load(handle)
            except Exception as exc:  # pragma: no cover
                warn(f"Failed to parse {path}: {exc}")
                continue
            if not bib_db.entries:
                warn(f"No BibTeX entries found in: {path}")
            entries.extend(bib_db.entries)

    if not entries:
        raise ValueError("No BibTeX entries found.")

    rekey_bib_entries(entries)
    writer = bibtexparser.bwriter.BibTexWriter()
    writer.order_entries_by = None
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = entries
    output_text = writer.write(db)
    return output_text


def convert_bib_files(
    inputs: Sequence[Union[str, Path]],
    output: Optional[Union[str, Path]] = None,
    *,
    on_warning: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Convert one or more BibTeX files to RIS text.

    Args:
        inputs: Paths to input BibTeX files.
        output: Optional output path to write RIS text.
        on_warning: Optional callback invoked with warning messages.

    Returns:
        The RIS string for all records.

    Raises:
        ValueError: If no BibTeX entries are found across all inputs.
    """

    warn = on_warning or (lambda msg: None)
    entries: List[Dict[str, str]] = []

    for inp in inputs:
        path = Path(inp)
        if not path.exists():
            warn(f"File not found: {path}")
            continue
        with path.open("r", encoding="utf-8") as handle:
            try:
                bib_db = bibtexparser.load(handle)
            except Exception as exc:  # pragma: no cover
                warn(f"Failed to parse {path}: {exc}")
                continue
            if not bib_db.entries:
                warn(f"No BibTeX entries found in: {path}")
            entries.extend(bib_db.entries)

    if not entries:
        raise ValueError("No BibTeX entries found.")

    ris_entries = [_entry_to_ris(entry) for entry in entries]
    output_text = "\n".join(ris_entries) + "\n"

    if output:
        Path(output).write_text(output_text, encoding="utf-8")

    return output_text


__all__ = ["convert_bib_files"]
