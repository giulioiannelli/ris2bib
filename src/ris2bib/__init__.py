"""
ris2bib – Convert RIS ↔ BibTeX (CLI + GUI).
"""

from .core import convert_files, parse_ris, record_to_bib
from .bib import convert_bib_files

__all__ = ["convert_files", "convert_bib_files", "parse_ris", "record_to_bib"]
