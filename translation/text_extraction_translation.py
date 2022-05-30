"""This file contains the script for extracting and translating text from pdf."""
from pathlib import Path  # for Windows/Unix compatibility

import pdfplumber

import translation.auxiliary_extraction_translation as auxiliary


def extract_and_translate_file(file_path, destination_path, paths_relative=True):
    """Extract, translate and store text from files.

    Extraction, translation and storing are performed
    for each page, which are written into a single pdf.
    """
    # Initialize nltk sentence tokenizer
    tokenizer = auxiliary.initialize_tokenizer()

    # Initialize FPDF file to write on
    fpdf = auxiliary.initialize_pdf_storage()

    # Open PDF
    with pdfplumber.open(Path(file_path)) as pdf:
        # Initialize page counter
        page_counter = "?"
        for page in pdf.pages:
            ##################
            #  Extraction  ###
            ##################
            extracted, page_number = auxiliary.extract(page, page_counter)
            page_counter = page_number  # Update page counter

            ##################
            #  Translate   ###
            ##################
            if extracted != "":
                # Translate paragraphs individually to keep
                paragraphs = extracted.split("\n\n")
                translated = "\n\n".join(
                    [
                        auxiliary.translate_extracted(paragraph, tokenizer)
                        for paragraph in paragraphs
                    ]
                )
            else:
                translated = extracted

            #######################
            #  Store PDF Page   ###
            #######################
            page_number = f"{page.page_number}/{len(pdf.pages)}"
            fpdf = auxiliary.write_to_page(translated, page_number, pdf=fpdf)

    # Bring all pages together, save pdf
    # Find subfolders of file
    if paths_relative:
        subdirectory_path = str(Path(file_path).relative_to(destination_path).parent)
        dest_path = destination_path + "/output/" + subdirectory_path + "/"

    else:
        dest_path = destination_path

    auxiliary.save_to_pdf(
        fpdf,
        file_name=str(Path(file_path).stem),
        destination_folder=dest_path,
    )


def main():
    """Translate specified PDF reports."""
    # Set-up
    desired = [
        "BEL/CB_Reports",
        (
            "Bel/CASSIERS et al. - 1998 - Les banques belges"
            "face a l'etat une rétrospectiv.pdf"
        ),
    ]
    # TODO: would a change of working directory make things easier?
    dest_path = "C:/Users/Philipp/OneDrive/available_historical_documents"

    # Find all pdfs
    pdf_list = auxiliary.find_pdfs(dest_path=dest_path, desired_path=desired)

    _ = [auxiliary.create_destination_dir(dest_path, f) for f in pdf_list]

    for file in pdf_list:
        print(file)
        extract_and_translate_file(file_path=file, destination_path=dest_path)


if __name__ == "__main__":
    main()
