# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ris2bib` is a bidirectional bibliography converter between RIS and BibTeX formats. It provides:
- CLI tools (`ris2bib` and `bib2ris`)
- A Tkinter GUI (`ris2bib-gui`) for RIS → BibTeX conversion
- Library functions for programmatic conversion

The project uses a setuptools-based build with source in `src/ris2bib/`.

## Development Setup

```bash
# Editable install with dev dependencies
pip install -e ".[dev]"

# Standard install
pip install .
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_conversion.py::test_ris_to_bib_includes_title_and_key

# Run with verbose output
pytest -v
```

Test files require sample files in `samples/` directory (sample1.ris, sample2.ris, sample1.bib).

## CLI Usage

```bash
# RIS → BibTeX
ris2bib input.ris -o output.bib
ris2bib input.ris  # writes to stdout

# BibTeX → RIS
bib2ris refs.bib -o output.ris
bib2ris refs.bib   # writes to stdout

# GUI
ris2bib-gui
python -m ris2bib.gui
```

## Architecture

### Module Structure

- **`core.py`**: RIS → BibTeX conversion logic
  - `parse_ris()`: Parses RIS format using regex tag pattern `^([A-Z0-9]{2})  -\s*(.*)$`
  - `record_to_bib()`: Converts parsed RIS record dict to BibTeX entry string
  - `convert_files()`: High-level function that reads files, parses, converts, and optionally writes output
  - Key generation: `{author_surname}{year}{first_significant_title_word}` (lowercase, deaccented)

- **`bib.py`**: BibTeX → RIS conversion using `bibtexparser` library
  - `convert_bib_files()`: Mirrors `convert_files()` API for reverse conversion
  - `_entry_to_ris()`: Converts bibtexparser entry dict to RIS format string

- **`cli.py`** and **`bib_cli.py`**: Thin CLI wrappers around conversion functions
  - Both use argparse with `inputs` (nargs="+") and optional `-o/--output`
  - Both write warnings to stderr and output to stdout/file

- **`gui.py`**: Tkinter GUI for RIS → BibTeX (does not support reverse conversion)

### Key Design Patterns

1. **Unified conversion API**: Both `convert_files()` and `convert_bib_files()` share the same signature:
   - `inputs`: List of file paths
   - `output`: Optional output path (None = return string only)
   - `on_warning`: Optional callback for warnings

2. **RIS parsing**: Uses line-by-line regex matching with state tracking for multi-line fields
   - Abstracts (AB/N2 tags) preserve line breaks with `\n`
   - Other multi-line fields join with spaces

3. **BibTeX key generation** (see core.py:141-145):
   - First author surname (cleaned, deaccented)
   - Year from PY/Y1/DA tags (regex: `\b(19|20|21)\d{2}\b`)
   - First significant title word (skips stopwords defined in `STOPWORDS` set)

4. **Type mappings**:
   - `RIS_TYPE_TO_BIB` (core.py:46-56): RIS → BibTeX entry types
   - `BIBTYPE_TO_RIS` (bib.py:13-26): BibTeX → RIS types

### Entry Points (pyproject.toml:26-31)

- `ris2bib` → `ris2bib.cli:main`
- `bib2ris` → `ris2bib.bib_cli:main`
- `ris2bib-gui` → `ris2bib.gui:main` (gui-scripts)

## Dependencies

- **Runtime**: `bibtexparser>=1.4` (only needed for BibTeX → RIS)
- **Dev**: `pytest>=7`
- **Standard library**: No external dependencies for RIS → BibTeX conversion

## Package Configuration

- Source layout: `src/ris2bib/` with `__init__.py`, `__main__.py`
- Type annotations: Includes `py.typed` marker for PEP 561 compliance
- Python requirement: `>=3.8`
- Build backend: setuptools with `pyproject.toml` configuration
