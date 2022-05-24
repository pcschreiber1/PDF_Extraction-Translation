"""This file contains tests to check the translation function."""
import pytest

from translation.auxiliary_extraction_translation import initialize_tokenizer
from translation.auxiliary_extraction_translation import translate_extracted


@pytest.fixture(scope="module")
def tokenizer():
    """Initialize english nltk tokenizer."""
    return initialize_tokenizer()


def test_inval_input_underscore(tokenizer):
    """Check that invalid input "_" is ignored."""
    text = "_"

    assert translate_extracted(text, tokenizer) == ""


def test_inval_input_5k_word(tokenizer):
    """Check that word of exactly 50000 bytes is ignored.

    5000bytes is the upload limit for translation engine.
    Translation seeks to find largest chunks below upload limit,
    but smallest unit is a word (i.e. not separated by " ").
    Arrange: Create String of 5k length (i.e. 5k chars)
    Act: Translate word.
    Assert: Check that output is message " <<Omitted Word longer than 5000bytes>>"
    Note: Function will add single empty space in front.
    """
    text = "a" * 5000

    assert translate_extracted(text, tokenizer) == " <<Omitted Word >= 5000bytes>>"


@pytest.mark.xfail(reason="Currently only implemented for extract_and_translate_file.")
def test_paragraph(tokenizer):
    r"""Check that paragraphs are maintained.

    Paragraphs are identified by "\n\n", but \n\n at the beginning
    of a string is ignored.
    Arrange: Create string with valid and invalid paragraph.
    Act: Translate string.
    Assert: Check that invalid paragraph is ignored and other maintained.
    """
    text = "\n\n Ich liebe Python." * 2
    translation = translate_extracted(text, tokenizer)

    assert translation.find("\n\n") > 0


def test_long_sentence(tokenizer):
    """Check that sentence longer 5000bytes is translated.

    Arrange: Create long sentence by adding long word.
    Act: Translate string.
    Assert: Check output contains "<<Omitted Word >= 5000bytes>>"
    """
    word = "a" * 6000
    text = "Ich liebe" + word + "Python. Ich liebe Python."
    translation = translate_extracted(text, tokenizer)

    assert translation.find("<<Omitted Word >= 5000bytes>>") > 0
