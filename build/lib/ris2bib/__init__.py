"""
ris2bib – Convert RIS references to BibTeX (CLI + GUI).
"""

from .core import convert_files, parse_ris, record_to_bib

__all__ = ["convert_files", "parse_ris", "record_to_bib"]
