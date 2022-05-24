"""This file contains tests to check the extraction function."""
from pathlib import Path  # for Windows/Unix compatibility

import pdfplumber
import pytest

from translation.auxiliary_extraction_translation import extract


@pytest.fixture(scope="module")
def pdf():
    """Open PDF example object with PDF Plumber.

    Clean-up: close pdf after tests have run.
    """
    example_path = "examples/1978-geschaeftsbericht-data.pdf"
    pdf = pdfplumber.open(Path(example_path))
    yield pdf
    pdf.close()


def test_exclusion_tables_page13(pdf):
    """Check that tables are excluded from text.

    For legibility of the file and challenges in translation
    tables are currently ignored when extracting text from PDF.
    Arrange: Open PDF and select page with table at the top (Page 13)
    Act: Extract text from PDF into string
    Assert: Check that first characters of string are correct sentence
    """
    page = pdf.pages[12]  # 13th page contains table at the top
    extracted, _ = extract(page, "?")

    assert extracted[:36] == "des Produktionspotentials anzusehen."


@pytest.mark.xfail(
    reason="PDFplumber is currently not recognising the table on Page 17 as a table."
)
def test_exclusion_tables_page17(pdf):
    """Check that tables are excluded from text.

    For legibility of the file and challenges in translation
    tables are currently ignored when extracting text from PDF.
    Arrange: Open PDF and select page with only table (Page 17)
    Act: Extract text from page into string
    Assert: Check that string is empty
    """
    table_page = pdf.pages[16]  # 17th page contains only tables
    extracted, _ = extract(table_page, "?")

    assert extracted == ""


def test_empty_page(pdf):
    """Check that, that empty pdf page is empty string.

    For purpose of translation, important that empty page
    is not translated into arbitrary amount of whitespaces.
    Arrange: Open PDF and select empty page (Page 2)
    Act: Extract text from page into string
    Assert: Check string is empty
    """
    table_page = pdf.pages[1]  # 17th page contains only tables
    extracted, _ = extract(table_page, "?")

    assert extracted == ""
