import re
from pathlib import Path

import pytest

from ris2bib import convert_files
from ris2bib.bib import convert_bib_files


BASE = Path(__file__).resolve().parent.parent
SAMPLES = BASE / "samples"


def test_ris_to_bib_includes_title_and_key():
    output = convert_files([SAMPLES / "sample1.ris"])
    assert "@article{doe2020example," in output
    assert re.search(r"title\s*= \{Example Title About Science\}", output)
    assert re.search(r"author\s*= \{Doe, Jane and Roe, John\}", output)
    assert re.search(r"journal\s*= \{Journal of Examples\}", output)


def test_ris_to_bib_multiple_files():
    output = convert_files([SAMPLES / "sample1.ris", SAMPLES / "sample2.ris"])
    assert output.count("@") == 2
    assert "@article{doe2020example," in output
    assert "@inproceedings{smith2021short," in output


def test_bib_to_ris_basic_fields():
    output = convert_bib_files([SAMPLES / "sample1.bib"])
    assert output.startswith("TY  - JOUR")
    assert "AU  - Smith, Alice" in output
    assert "AU  - Johnson, Bob" in output
    assert "TI  - Testing Things" in output
    assert "JO  - Proceedings of Testing" in output
    assert "PY  - 2021" in output
    assert "SP  - 10" in output
    assert "EP  - 20" in output
    assert output.rstrip().endswith("ER  -")


def test_missing_inputs_raise():
    with pytest.raises(ValueError):
        convert_files([])
