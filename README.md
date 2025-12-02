# ris2bib
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Convert RIS bibliography files to BibTeX (and BibTeX back to RIS) with a simple CLI and Tkinter GUI.

## Features
- RIS → BibTeX and BibTeX → RIS, powered by `bibtexparser`.
- Generates lowercase BibTeX keys based on author, year, and title.
- Handles multiple files at once; library-friendly helpers for scripting.
- Cross-platform GUI for quick RIS → BibTeX conversions.

## Quick start
```bash
git clone https://github.com/opisthofulax/ris2bib.git
cd ris2bib
pip install -e .[dev]

# Convert the bundled samples
ris2bib samples/sample1.ris -o output.bib
bib2ris samples/sample1.bib -o output.ris

# Launch the GUI (RIS → BibTeX)
ris2bib-gui
```

## Installation
- Local source: `pip install .`
- From GitHub: `pip install git+https://github.com/opisthofulax/ris2bib.git`
- Development mode: `pip install -e .[dev]`

## CLI usage
```
# RIS → BibTeX
ris2bib input1.ris [input2.ris ...] -o output.bib
ris2bib input.ris                        # writes BibTeX to stdout

# BibTeX → RIS
bib2ris refs1.bib [refs2.bib ...] -o output.ris
bib2ris refs.bib                         # writes RIS to stdout
```

## GUI usage
- Run `ris2bib-gui` (installed entry point), or `python -m ris2bib.gui`.
- Click “Choose RIS files…” to select one or more `.ris` files.
- Click “Convert” to generate BibTeX; the output appears in the text area.
- Click “Save output…” to write the BibTeX to disk.
  (GUI currently targets RIS → BibTeX; reverse conversion is via CLI.)

## Samples
- `samples/sample1.ris`, `samples/sample2.ris` — quick RIS examples to try.
- `samples/sample1.bib` — BibTeX example for reverse conversion.

## Library usage
```python
from ris2bib import convert_files
from ris2bib.bib import convert_bib_files

bibtex_text = convert_files(["references.ris"])
ris_text = convert_bib_files(["refs.bib"])
```

## Testing & development
- Run tests: `pytest` (after `pip install -e .[dev]`).
- Makefile shortcuts: `make dev`, `make test`, `make lint`, `make clean`.
- CI: GitHub Actions workflow in `.github/workflows/ci.yml`.

## Limitations
- GUI currently supports RIS → BibTeX only.
- Field mappings are intentionally simple; uncommon RIS/BibTeX tags may be omitted.

## License
MIT — see [LICENSE](LICENSE).
