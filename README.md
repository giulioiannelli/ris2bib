# ris2bib

Convert RIS bibliography files to BibTeX (and BibTeX back to RIS) with a simple CLI and Tkinter GUI.

## Features
- Generates lowercase BibTeX keys based on author, year, and title.
- Handles multiple RIS files at once and concatenates the output.
- Cross-platform GUI for quick drag-and-drop style workflows (works with file picker).
- Library-friendly conversion helpers for both directions.

## Installation
```
pip install .
```
or install directly from a Git clone:
```
pip install git+https://github.com/yourname/ris2bib.git
```

## CLI usage
```
# RIS → BibTeX
ris2bib input1.ris [input2.ris ...] -o output.bib
ris2bib input.ris              # writes BibTeX to stdout

# BibTeX → RIS
bib2ris refs1.bib [refs2.bib ...] -o output.ris
bib2ris refs.bib               # writes RIS to stdout
```

## GUI usage
- Run `ris2bib-gui` (installed entry point), or `python -m ris2bib.gui`.
- Click “Choose RIS files…” to select one or more `.ris` files.
- Click “Convert” to generate BibTeX; the output appears in the text area.
- Click “Save output…” to write the BibTeX to disk.
  (GUI currently targets RIS → BibTeX; reverse conversion is via CLI.)

## Library usage
```python
from ris2bib import convert_files
from ris2bib.bib import convert_bib_files

bibtex_text = convert_files(["references.ris"])
ris_text = convert_bib_files(["refs.bib"])
```

## Development
- Editable install: `pip install -e .`
- Linting/formatting: none required; standard library only.
- Packaging: `pyproject.toml` with setuptools backend; source lives in `src/`.
