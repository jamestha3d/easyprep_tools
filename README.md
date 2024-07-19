# PDF Text Extractor and Parser (AI-Generated README)

This Python script extracts questions and answer options from a formatted PDF document, likely a question sheet.

**Project Description:**

This project automates the extraction of questions and answer options from a PDF document. It utilizes regular expressions to identify text patterns commonly found in question sheets and then groups related questions based on their proximity in the document. 

**Key Functionalities:**

* **Question and Option Extraction:** Employs regular expressions to identify question text and corresponding answer options within the PDF content.
* **Question Grouping:** Groups related questions based on their proximity in the document, ensuring a logical structure for the extracted data.
* **Formatting Flexibility:** Handles variations in question numbering formats (e.g., "Question 1", "Phrase 1:") to ensure broader compatibility.
* **Text Cleaning:** Removes unnecessary characters and formatting from the extracted text, resulting in a cleaner and more usable data format.
* **JSON Output:** Saves the extracted data in a JSON file (`tef_textes.json`) for easy integration and further processing.

**Requirements:**

* Python 3 (tested with version 3.x)
* pdfplumber library (install using `pip install pdfplumber`)

**Usage:**

1. **Save the Script:** Save the script as a Python file (e.g., `pdf_extractor.py`).
2. **Set File Path:** Modify the file path in the `Pdf.__init__()` function to point to your target PDF document.
3. **Run the Script:** Execute the script using the command `python pdf_extractor.py` in your terminal.

**Outputs:**

* **Console Output:** The script displays the extracted questions and answer options on the console for immediate review.
* **JSON File:** The script generates a JSON file (`tef_textes.json`) containing the extracted questions and options in a structured format.

**Considerations:**

* **Basic Implementation:** This script serves as a foundational tool and might require adjustments based on the specific structure and formatting variations present in your PDF documents. 
* **Customization Potential:** The script can be further customized to handle additional question numbering formats, answer key extraction, or integration with different data processing workflows.

**AI-Generated Disclaimer:**

This README file was AI-generated. 
