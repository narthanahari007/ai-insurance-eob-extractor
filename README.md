AI Insurance EOB Extraction & Chatbot

An OCR-based Python project that extracts structured information from scanned insurance Explanation of Benefits (EOB) documents, validates the extracted records, generates Excel reports, and answers questions using a rule-based chatbot.

Project Overview

Insurance EOB documents contain important patient, procedure, and financial information. Manually extracting this information from scanned documents can be time-consuming.

This project automates much of that process using Optical Character Recognition (OCR), Python-based extraction, validation, structured data storage, and Excel reporting.

Key Features
Converts PDF pages into images for OCR processing.
Extracts text and word positions from scanned documents.
Detects EOB sections using document-layout heuristics.
Extracts structured information using Python and pattern-based processing.
Supports multiple service lines.
Applies validation and correction steps.
Stores processed records in JSON format.
Generates Excel reports with data, review, validation summary, and source traceability sheets.
Provides a rule-based chatbot for querying extracted information.
Technologies Used
Python
PyMuPDF
Tesseract OCR
pytesseract
Pillow
Regular expressions
JSON
Pandas
Excel reporting
Rule-based chatbot development
System Architecture
Scanned Insurance PDF
        |
        v
PDF-to-Image Conversion
        |
        v
Tesseract OCR
        |
        v
EOB Section Detection
        |
        v
Field Extraction
        |
        v
Validation and Corrections
        |
        v
Structured JSON Records
       / \
      v   v
   Excel  Rule-Based
   Report Chatbot
Project Results

The current development dataset contains 241 service-line records extracted from an 82-page scanned document.

The generated Excel workbook includes:

EOB Data
Review
Validation Summary
Source Traceability

These results describe the current processed dataset and do not guarantee that every OCR-extracted field is error-free.

Project Structure
ai-insurance-eob-extractor/
├── backend/
│   ├── pdf_to_images.py
│   ├── eob_detector.py
│   ├── eob_extractor.py
│   ├── extract_all.py
│   ├── apply_corrections.py
│   ├── final_validation.py
│   ├── create_excel.py
│   ├── build_final_dataset.py
│   └── chatbot.py
├── .gitignore
├── README.md
└── requirements.txt

The exact files and folder structure may vary as development continues.

Installation
Prerequisites
Python 3.10 or later
Tesseract OCR
pip
1. Clone the repository
git clone YOUR_REPOSITORY_URL
cd ai-insurance-eob-extractor

Replace YOUR_REPOSITORY_URL with your actual GitHub repository URL.

2. Create a virtual environment
python -m venv venv

Activate it on Windows:

.\venv\Scripts\Activate.ps1
3. Install Python dependencies
python -m pip install -r requirements.txt
4. Install Tesseract OCR

Install Tesseract OCR separately and ensure its executable is available to your system or configured in your Python application.

Usage

Run the relevant scripts in the intended pipeline order:

Convert PDF pages into images.
Perform OCR and detect EOB sections.
Extract fields and service-line records.
Apply corrections and validation.
Build the final structured dataset.
Generate the Excel workbook.
Run the chatbot to query the processed records.

Exact commands depend on the final script configuration and input-file paths.

Privacy and Security

Insurance documents can contain sensitive personal and financial information.

Do not commit original insurance PDFs.
Do not publish patient names, insurance identifiers, or extracted personal records.
Do not upload generated spreadsheets or private datasets.
Keep API keys and credentials out of source control.
Use synthetic or properly anonymized sample data for demonstrations.
Limitations
OCR accuracy depends on document image quality.
Blurry scans and complex layouts can cause extraction errors.
Layout-based detection may need adjustment for other document formats.
Extracted records require validation.
The current chatbot uses predefined Python rules rather than a large language model.
Future Enhancements
Build a web interface for document upload and querying.
Add confidence-based extraction and manual review.
Improve document-layout detection.
Support additional insurance document formats.
Add natural-language query interpretation.
Introduce secure authentication and access controls.
Author

Narthana Hari S.V.

B.Tech – Artificial Intelligence and Data Science

Project: AI Insurance EOB Extraction & Chatbot