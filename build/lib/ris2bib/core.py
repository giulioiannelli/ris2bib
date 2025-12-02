"""
Core conversion logic for RIS → BibTeX.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union

STOPWORDS = {
    "the",
    "a",
    "an",
    "on",
    "of",
    "and",
    "for",
    "to",
    "in",
    "with",
    "by",
    "from",
    "at",
    "into",
    "over",
    "under",
    "between",
    "within",
    "without",
    "across",
    "is",
    "are",
    "via",
    "using",
    "based",
    "towards",
    "toward",
    "as",
    "per",
    "vs",
    "versus",
}

RIS_TYPE_TO_BIB = {
    "JOUR": "article",
    "MGZN": "article",
    "CONF": "inproceedings",
    "CPAPER": "inproceedings",
    "CHAP": "incollection",
    "BOOK": "book",
    "RPRT": "techreport",
    "THES": "phdthesis",
    "UNPB": "unpublished",
}

TAG_PATTERN = re.compile(r"^([A-Z0-9]{2})  -\s*(.*)$")


def deaccent(s: str) -> str:
    """Strip accents/diacritics and return ASCII-only where possible."""
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def clean_for_key(s: str) -> str:
    """Lowercase, deaccent, and keep only letters/numbers (no spaces/punct)."""
    s = deaccent(s).lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def first_significant_word(title: str) -> str:
    # Take the first word not in STOPWORDS; split on non-letters to be safe.
    words = re.split(r"[^A-Za-z0-9]+", title)
    for w in words:
        if not w:
            continue
        wl = w.lower()
        if wl not in STOPWORDS:
            return clean_for_key(w)
    for w in words:
        if w:
            return clean_for_key(w)
    return "untitled"


def parse_ris(stream: Iterable[str]) -> List[Dict[str, List[str]]]:
    """Parse RIS into a list of records (dict of tag -> list[str])."""
    records: List[Dict[str, List[str]]] = []
    current: Dict[str, List[str]] = {}
    last_tag: Optional[str] = None

    for raw in stream:
        line = raw.rstrip("\n")
        match = TAG_PATTERN.match(line)
        if match:
            tag, value = match.group(1), match.group(2).strip()
            if tag == "ER":
                if current:
                    records.append(current)
                current = {}
                last_tag = None
                continue
            current.setdefault(tag, []).append(value)
            last_tag = tag
        else:
            if last_tag:
                # Preserve line breaks in abstracts; space otherwise.
                sep = "\n" if last_tag in {"AB", "N2"} else " "
                current[last_tag][-1] += sep + line.strip()

    if current:
        records.append(current)
    return records


def get_first_author_surname(rec: Dict[str, List[str]]) -> str:
    authors = rec.get("AU") or rec.get("A1") or []
    if not authors:
        corp = (rec.get("A2") or rec.get("A3") or rec.get("A4") or rec.get("C1") or ["anon"])[0]
        base = corp.split(",")[0]
    else:
        base = authors[0].split(",")[0]
    return clean_for_key(base) or "anon"


def get_year(rec: Dict[str, List[str]]) -> str:
    for tag in ("PY", "Y1", "DA"):
        vals = rec.get(tag)
        if vals:
            match = re.search(r"\b(19|20|21)\d{2}\b", vals[0])
            if match:
                return match.group(0)
    return "0000"


def get_title(rec: Dict[str, List[str]]) -> str:
    return (rec.get("TI") or rec.get("T1") or [""])[0]


def make_key(rec: Dict[str, List[str]]) -> str:
    first = get_first_author_surname(rec)
    year = get_year(rec)
    word = first_significant_word(get_title(rec))
    return f"{first}{year}{word}"


def choose_bibtype(rec: Dict[str, List[str]]) -> str:
    ty = (rec.get("TY") or ["JOUR"])[0].upper()
    return RIS_TYPE_TO_BIB.get(ty, "article")


def join_authors(authors: List[str]) -> str:
    cleaned = []
    for author in authors:
        author = re.sub(r"\s+", " ", author.strip())
        cleaned.append(author)
    return " and ".join(cleaned)


def pages_field(rec: Dict[str, List[str]]) -> Optional[str]:
    start_page = (rec.get("SP") or [None])[0]
    end_page = (rec.get("EP") or [None])[0]
    if start_page and end_page:
        return f"{start_page}--{end_page}"
    if start_page:
        return start_page
    return None


def title_field(rec: Dict[str, List[str]]) -> str:
    return get_title(rec)


def journal_field(rec: Dict[str, List[str]]) -> Optional[str]:
    for tag in ("JO", "JF", "T2"):
        vals = rec.get(tag)
        if vals:
            return vals[0]
    return None


def safe_bibtex_string(s: str) -> str:
    # Leave UTF-8 as-is; BibTeX/Biber handle UTF-8. Escape unmatched braces.
    s = s.replace("{", "\\{").replace("}", "\\}")
    return s


def record_to_bib(rec: Dict[str, List[str]]) -> str:
    btype = choose_bibtype(rec)
    key = make_key(rec)
    fields = []

    title = title_field(rec)
    if title:
        fields.append(("title", title))

    authors = rec.get("AU") or rec.get("A1") or []
    if authors:
        fields.append(("author", join_authors(authors)))

    journal = journal_field(rec)
    if journal:
        fields.append(("journal", journal))

    year = get_year(rec)
    if year:
        fields.append(("year", year))

    volume = (rec.get("VL") or [None])[0]
    if volume:
        fields.append(("volume", volume))

    number = (rec.get("IS") or [None])[0]
    if number:
        fields.append(("number", number))

    pages = pages_field(rec)
    if pages:
        fields.append(("pages", pages))

    doi = (rec.get("DO") or rec.get("M3") or [None])[0]
    if doi:
        fields.append(("doi", doi))

    url = (rec.get("UR") or [None])[0]
    if url:
        fields.append(("url", url))

    issn = (rec.get("SN") or [None])[0]
    if issn:
        fields.append(("issn", issn))

    publisher = (rec.get("PB") or [None])[0]
    if publisher and btype in {"article", "inproceedings", "incollection"}:
        fields.append(("publisher", publisher))

    abstract = (rec.get("AB") or rec.get("N2") or [None])[0]
    if abstract:
        fields.append(("abstract", abstract))

    lines = [f"@{btype}{{{key},"]
    for key_name, value in fields:
        value = safe_bibtex_string(value)
        lines.append(f"  {key_name:<11}= {{{value}}},")

    if len(lines) > 1 and lines[-1].endswith(","):
        lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def convert_files(
    inputs: Sequence[Union[str, Path]],
    output: Optional[Union[str, Path]] = None,
    *,
    on_warning: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Convert one or more RIS files to BibTeX text.

    Args:
        inputs: Paths to input RIS files.
        output: Optional path to write the output .bib file.
        on_warning: Optional callback invoked with warning messages.

    Returns:
        The BibTeX string for all records.

    Raises:
        ValueError: If no RIS records are found across all inputs.
    """

    warn = on_warning or (lambda msg: None)
    records: List[Dict[str, List[str]]] = []

    for inp in inputs:
        path = Path(inp)
        if not path.exists():
            warn(f"File not found: {path}")
            continue

        with path.open("r", encoding="utf-8") as handle:
            parsed = parse_ris(handle)

        if not parsed:
            warn(f"No RIS records found in: {path}")
        records.extend(parsed)

    if not records:
        raise ValueError("No RIS records found.")

    bib_entries = [record_to_bib(record) for record in records]
    output_text = "\n\n".join(bib_entries) + "\n"

    if output:
        Path(output).write_text(output_text, encoding="utf-8")

    return output_text


__all__ = [
    "convert_files",
    "parse_ris",
    "record_to_bib",
]
