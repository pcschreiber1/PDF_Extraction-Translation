"""This file contains tests to check the extraction and translation workflow."""
from pathlib import Path  # for Windows/Unix compatibility

import pytest

from translation.auxiliary_extraction_translation import create_destination_dir
from translation.auxiliary_extraction_translation import find_pdfs
from translation.text_extraction_translation import extract_and_translate_file


@pytest.fixture(scope="module")
def pdf_path():
    """Load short example PDF."""
    return "examples/1978-geschaeftsbericht-data_subset.pdf"


def test_workflow_creates_file(pdf_path, tmp_path):
    """Check that the workflow works on example pdf.

    `extract_and_translate_file()` extracts text from a PDF,
    translates it and stores it again in a PDF.
    Arrange: Provie PDF path and temporary storage location.
    Act: Apply function.
    Assert: Check whether file exists in temp location.
    """
    d = tmp_path / "output/"
    d.mkdir()

    extract_and_translate_file(
        file_path=pdf_path, destination_path=(str(d) + "/"), paths_relative=False
    )

    file = str(d) + "/" + Path(pdf_path).stem + ".pdf"

    assert Path(file).exists()


def test_find_example_pdf():
    """Check that find_pdfs() works.

    Arrange: The project reposiotry contains pdfs.
    Act: Let find_pdfs() search at root dir of project.
    Assert: Check that path is as expected.
    """
    pdf_path = find_pdfs([""], ".", "")
    pdf_path.sort()

    assert pdf_path == [
        "examples/1978-geschaeftsbericht-data.pdf",
        "examples/1978-geschaeftsbericht-data_subset.pdf",
    ]


def test_create_destination_dir(tmp_path):
    """Check creation of identical tree structure.

    Arrange: Create temporary directory with sub-dir and file.
    Act: Let create_destination_dir() create dir at parent.
    Assert: Check in new that subfolder exists but not file.
    """
    dir_path = tmp_path / "sub/"
    dir_path.mkdir()
    file_path = dir_path / "hello.txt"
    file_path.write_text("Content")

    create_destination_dir(str(tmp_path), str(file_path))

    assert Path(tmp_path / "output/sub").exists()
    assert not Path(tmp_path / "output/sub/hello.txt").exists()
