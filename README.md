# Translate long PDF-Reports in Python.
![Style](https://img.shields.io/badge/Style-Flake8-brightgreen.svg)
[![Continuous Integration](https://github.com/pcschreiber1/PDF_Extraction-Translation/actions/workflows/CI.yml/badge.svg)](https://github.com/pcschreiber1/PDF_Extraction-Translation/actions/workflows/CI.yml)
[![codecov](https://codecov.io/gh/pcschreiber1/PDF_Extraction-Translation/branch/main/graph/badge.svg?token=R2T8WEHXL8)](https://codecov.io/gh/pcschreiber1/PDF_Extraction-Translation)

Translate many large PDF Reports for free using Python. You can find the corresponding *Towards Data Science* article [here](https://towardsdatascience.com/translate-long-pdf-reports-in-python-eab3be08ceb4) or follow the Jupyter Notebook `Article_PDF-Translation` - the Central Bank Report is stored in `src/examples`.

This repo stores the pipeline developed for work, where a large number of official reports from different OECD countries had to be translated. To translate free of charge, the `GoogleTranslate` API is used. The main python packages are: `pdfplumber`, `deep_translator`, and `pyfpdf2`.
