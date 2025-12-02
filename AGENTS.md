# AGENTS – Working on `ris2bib`

This project converts RIS ↔ BibTeX with a CLI, a Tkinter GUI (RIS → BibTeX), and tests. Use this file as a quick onboarding for future agents.

## Repo layout
- `src/ris2bib/core.py` – RIS → BibTeX logic.
- `src/ris2bib/bib.py` – BibTeX → RIS logic.
- `src/ris2bib/cli.py` – `ris2bib` CLI.
- `src/ris2bib/bib_cli.py` – `bib2ris` CLI.
- `src/ris2bib/gui.py` – Tkinter GUI (toggle RIS → BibTeX or BibTeX → RIS, optional drag/drop).
- `samples/` – Example RIS/Bib files for smoke tests.
- `tests/` – Pytest suite.
- `pyproject.toml` – Packaging and dependencies (dev extra includes pytest).
- `Makefile` – `make dev`, `make test`, `make lint`, `make clean`.
- `.github/workflows/ci.yml` – CI on Python 3.8/3.11.

## Quick setup
```bash
pip install -e .[dev]      # editable install with pytest
make test                  # or: python -m pytest
```
Runtime deps are minimal: `bibtexparser` plus stdlib.

## Common commands
- RIS → BibTeX: `ris2bib samples/sample1.ris -o out.bib`
- BibTeX → RIS: `bib2ris samples/sample1.bib -o out.ris`
- GUI: `ris2bib-gui`

## Conventions
- Keep code in `src/ris2bib`; include `py.typed` for typing compliance.
- Use ASCII unless file already uses Unicode.
- Preserve existing behavior for key generation and field mappings unless requirements change.
- GUI currently only handles RIS → BibTeX; note any GUI changes in README.

## Testing/CI
- Use `pytest`; tests cover both directions and key/title handling.
- CI workflow runs `pip install -e .[dev]` then `pytest`.

## GUI specifics
- Drag-and-drop uses optional `tkinterdnd2`; if not installed, GUI falls back to file picker and shows a hint.
- Mode switch determines output (BibTeX aggregated; RIS entries emitted together). GUI accepts mixed `.ris`/`.bib` inputs and normalizes keys for BibTeX output.

## Versioning/Docs
- Update `CHANGELOG.md` and `pyproject.toml` version together when shipping changes.
- README has badges, quick start, and limitations; add screenshots/GIFs there if you modify UI.

## Caution
- Avoid destructive git commands; do not revert user changes.
- If adding dependencies, list them in `pyproject.toml` (and `requirements*.txt` if needed).
- Maintain cross-platform compatibility (Windows/macOS/Linux) and keep Tkinter usage minimal and portable.
