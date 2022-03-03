"""This file contains the script for extracting and translating text from pdf."""
from pathlib import Path # for Windows/Unix compatibility
from functools import partial
import os
from shutil import copytree, ignore_patterns, rmtree

# Extraction
import pdfplumber
# from pdfminer.high_level import extract_text
# from pdfminer.layout import LAParams # for specifying line margin

# Translation
import nltk.data # natural language processing
from deep_translator import (GoogleTranslator)

# Save to pdf
from fpdf import FPDF
class CustomPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        #self.cell(0, 10, "Original Page " + str(self.page_no), 0, 0, "C")
        self.cell(0, 10, f'Page {self.page_no}', 0, 0, "C")

def find_pdfs(desired_path,
              dest_path="scripts/sources/"
              ):
    """Search a set of specific (sub) folders for pdf files.

    Exclude everything that is in "English Folder" 
    Returns: List with strings of full path
    """
    container = []
    for path in desired_path:
        folder = dest_path + "/" + path
        # Add Files directly
        if os.path.isfile(folder):
            container.append(folder)
        
        else:
            # Recursively step through directory
            for dirpath, _, filenames in os.walk(Path(folder)):
                # Select only ".pdf" files
                for filename in [f for f in filenames if f.endswith(".pdf")]:
                    # Exclude folders that are not in subset of interest
                    if set(["English"]).isdisjoint(Path(dirpath).parts):
                        container.append(dirpath + "/" + filename)

    return container

def create_destination_dir(destination_folder, file_path):
    """Creates a copy of the desired directory structure, no files.
    
    The new directory under which the strucutre is created is called "ouput/".
    Args:
        destination_folder: string with absolute path to destination folder
        file_path: string with absolute path to desired file
    """
    # Check that folder exists locally
    assert Path(destination_folder).exists(), (f"The Destination directory {destination_folder}"
                                                " does not exist locally.")

    # Check that file is part of destination folder
    assert Path(file_path).is_relative_to(destination_folder)

    # Check that file_path leads to a file
    # NOTE: Otherwise taking the parent does not make sense
    assert os.path.isfile(Path(file_path)), f"The File Path {file_path} does not exist locally"

    # Create "output/" subdirectory if not already exist
    if not Path(destination_folder + "/output").exists():
        try:
            os.mkdir(destination_folder + "/output")
        except OSError:
            print (f"Creation of the '/output' directory failed")
        else:
            print (f"Successfully created the '/output' directory")

    # Get parent of file as relative path
    file_parent = str(Path(file_path
                      ).parent.relative_to(
                      destination_folder))

    # Create output/ subdirectory from specified path, if not already exist
    if not Path(destination_folder + "/output/" + file_parent).exists():
        try:
            os.makedirs(destination_folder + "/output/" + file_parent)
        except OSError:
            print (f"Creation of the {file_parent} directory failed")
        else:
            print (f"Successfully created the {file_parent} directory")

def get_table_settings(p):
    """Dictionary used by PDF Plumber .find_tables().
    
    Args: pdfplumber page Object
    Returns: dictionary
    """
    def curves_to_edges(cs):
        """See https://github.com/jsvine/pdfplumber/issues/127"""
        edges = []
        for c in cs:
            edges += pdfplumber.utils.rect_to_edges(c)
        return edges

    # Table settings.
    ts = {
        "vertical_strategy": "explicit",
        "horizontal_strategy": "explicit",
        "explicit_vertical_lines": curves_to_edges(p.curves + p.edges),
        "explicit_horizontal_lines": curves_to_edges(p.curves + p.edges),
        "intersection_y_tolerance": 10,
    }
    return ts


def not_within_bboxes(obj, bboxes): # or add bboxes?
    """Check if the object is in any of the table's bbox."""
    def obj_in_bbox(_bbox):
        """See https://github.com/jsvine/pdfplumber/blob/stable/pdfplumber/table.py#L404"""
        v_mid = (obj["top"] + obj["bottom"]) / 2
        h_mid = (obj["x0"] + obj["x1"]) / 2
        x0, top, x1, bottom = _bbox
        return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)
    return not any(obj_in_bbox(__bbox) for __bbox in bboxes)


def extract(page, page_counter):
    """Wrapper for pdfplumber function, to be applied to a Page Object.
    
    Eliminates tables, page numbers and in-paragraph line breaks. Returns a string and page number.
    Uses the global variable page_counter
    """
    # Assert is class pdfplumber page
    assert isinstance(page, pdfplumber.page.Page), "`page` needs to be object of type pdfplumber.page.Page"

    # Step 1: Extract text, exclude tables
    if page.find_tables() != []:
        # Get the bounding boxes of the tables on the page.
        # Adapted From https://github.com/jsvine/pdfplumber/issues/242#issuecomment-668448246
        ts = get_table_settings(page)
        bboxes = [table.bbox for table in page.find_tables(table_settings=ts)]
        
        bbox_not_within_bboxes = partial(not_within_bboxes, bboxes=bboxes) 

        # Filter-out tables from page
        page = page.filter(bbox_not_within_bboxes)
    
    # Extract text
    extracted = page.extract_text()

    # Step 2: Get Page Number
    ## First line should be page number
    if extracted[:extracted.find("\n")-1].isdigit():
        page_number = extracted[:extracted.find("\n")-1]
        # # update page counter to identified page
        # page_counter = int(page_number)

        # Delete page_number (i.e. first line) from text
        extracted = extracted[extracted.find("\n"):]
    else:
        #raise AssertionError #first line is not page number
        #print(extracted[:extracted.find("\n")-1])
        # See if we can count forward from previously identified page number
        if page_counter != "?":
            #page_counter += 1
            page_number = int(page_counter) + 1
        else:
            page_number = page_counter

    # Step 3: Delete in-paragraph line breaks
    extracted = extracted.replace(".\n", "**\m" # keep paragraph breaks
                        ).replace(". \n", "**\m" # keep paragraph breaks
                        ).replace("\n", "" # delete in-paragraph breaks (i.e. all remaining \n)
                        ).replace("**\m", ".\n\n") # restore paragraph breaks

    return extracted, page_number

def initialize_tokenizer():
    # Set-up natural language processing
    # TODO: need different tokenizer for different language?
    nltk.data.path.append("/tmp/") # Tell the NLTK data loader to look for resource files in /tmp/
    nltk.download('punkt', download_dir='/tmp/') # Download NLTK tokenizers to /tmp/
    
    return nltk.data.load('tokenizers/punkt/english.pickle') # Load the English language tokenizer

def translate_extracted(Extracted, tokenizer):
    """Wrapper for Google Translate with upload workaround.
    
    This functions works around the upload limit of 50000 chars by
    collecting chuncks of sentences that are below this limit and translate
    them individually - sentences longer than 5000 chars are divided in half.
    Sentences are identified using `nltk` natural language processing.
 
    Returns: a string
    """
    ###################################
    ####     Set-up       #############
    ###################################

    # Set-up and wrap translation client
    translate = GoogleTranslator(source='auto', target='en').translate

    # Split input text into a list of sentences
    sentences = tokenizer.tokenize(Extracted)

    ###################################
    ####     Translation     ##########
    ###################################    

    # Initialize containers
    translated_text = ''
    source_text_chunk = ''

    # collect chuncks of sentences below limit and translate them individually
    for sentence in sentences:
        # if chunck together with current sentence is below limit, add the sentence
        if ((len(sentence.encode('utf-8')) + len(source_text_chunk.encode('utf-8')) < 5000)):
            source_text_chunk += ' ' + sentence
        
        # else translate chunck and start new one with current sentence
        else:
            translated_text += ' ' + translate(source_text_chunk)

            # if current sentence smaller than 5000 chars, start new chunck
            if (len(sentence.encode('utf-8')) < 5000):
                source_text_chunk = sentence

            #########################################
            ##   ISSUE 1: Long sentences          ###   
            #########################################
            # else, divide-up sentence, translate each part and start chunck from zero
            else:    
                # # Divide long sentence in half
                # sentence_list = sentence.split(" ")
                # cut_off = round(len(sentence_list)/2)
                
                # half1, half2 = " ".join(sentence_list[:cut_off]), " ".join(sentence_list[cut_off:])

                # # Translate and add each part
                # translated_text += ' ' + translate(half1) + translate(half2)

                # Divide-up sentence into list of words
                sentence_list = sentence.split(" ")

                for word in sentence_list:
                    #########################################
                    ##   ISSUE 2: Long "Wordds"           ###   
                    #########################################
                    if (len(word.encode('utf-8')) < 5000):
                        word = "<<Omitted Word longer than 5000bytes>>"
                    translated_text += ' ' + translate(word)
                
                # Re-set text container to empty
                source_text_chunk = ''

    # Translate the final chunk of input text, if there is any valid text left to translate
    if translate(source_text_chunk) != None:
        translated_text += ' ' + translate(source_text_chunk)
    
    return translated_text

def initialize_pdf_storage():
    """Initialize PDF document to write on."""
    # Use PDF Class with footer, specified at the top
    pdf = CustomPDF() 
    # Set uni code compatible font 
    pdf.set_font("Arial", size = 7)
    
    return pdf


def write_to_page(text,
                page_number,
                pdf):
    """Writes a string on a pdf page.
    
    This function uses the FDPF module to write the string on
    a pdf page of a PDF document. The encoding is "latin-1".
 
    Args:
        text: string to be saved
        pahe_number: string/int with current page nuber
        pdf: FPDF CustomPDF object
    Returns: FPDF CustomPDF object with added page
    """
    assert isinstance(pdf, CustomPDF), ("PDF needs to be FPDF CustomPDF object as created\n"
                                        "by initialize_pdf_storage().")
    # Add a page
    pdf.add_page()

    # Assign page number (uses footer class defined above)
    pdf.page_no = page_number

    pdf.multi_cell(w=0,h=5,txt= text.encode("latin-1", errors = "replace").decode("latin-1"))

    return pdf

def save_to_pdf(pdf,
                file_name,
                destination_folder = "scripts/output/"):
    """Saves pdf pages as a pdf document.
     
    Args:
        pdf: FPDF Custom_Page Object 
        file_name: name of the file
        destination_folder: location where to save the file
    Returns: Nothing
    """
    assert isinstance(pdf, CustomPDF), ("PDF needs to be FPDF CustomPDF object as created\n"
                                        "by initialize_pdf_storage().")
    pdf.output(Path(destination_folder + file_name + ".pdf"))#,'F')