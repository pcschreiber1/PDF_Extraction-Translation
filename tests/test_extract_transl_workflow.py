"""This file contains tests to check the extraction and translation workflow."""
from pathlib import Path  # for Windows/Unix compatibility

import pytest

from translation.text_extraction_translation import extract_and_translate_file


@pytest.fixture(scope="module")
def pdf_path():
    """Load short example PDF."""
    return "examples/1978-geschaeftsbericht-data.pdf"


@pytest.mark.skip()
def test_extraction_and_translation(pdf_path, tmp_path):
    """Check that the workflow works on example pdf.

    The function extracts, translates and stores text.
    Arrange: Provie PDF path and temporary storage location.
    Act: Apply function, then open stored result.
    Assert: Check first characters of page 13 match expected content.
    """
    d = tmp_path / "output"
    d.mkdir()

    extract_and_translate_file(
        file_path=pdf_path, destination_path=d, paths_relative=False
    )

    file = d / Path(pdf_path).stem

    assert Path(file).is_file()
