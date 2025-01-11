from flask import Blueprint, send_file, session
from fpdf import FPDF
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile
import os
from bs4 import BeautifulSoup

key_export = Blueprint('key_export', __name__)

@key_export.route('/export-keynotes-pdf')
def export_keynotes_pdf():
    """Exports generated keynotes as a PDF file."""
    # Retrieve keynotes from session
    keynotes_html = session.get('generated_keynotes', '')
    
    # Parse HTML to extract text
    soup = BeautifulSoup(keynotes_html, 'html.parser')
    keynotes_text = soup.get_text('\n', strip=True)
    
    # Create a PDF document
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Generated Keynotes", ln=True, align='C')
    pdf.ln(10)  # Add space after title

    # Add content line by line
    pdf.set_font("Arial", size=12)
    for line in keynotes_text.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 10, line.strip())
            pdf.ln(5)

    # Save the PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        response = send_file(
            tmp.name,
            download_name='keynotes.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )
        response._file_to_cleanup = tmp.name
        return response

@key_export.route('/export-keynotes-docx')
def export_keynotes_docx():
    """Exports generated keynotes as a DOCX file."""
    # Retrieve keynotes from session
    keynotes_html = session.get('generated_keynotes', '')
    
    # Parse HTML to extract text
    soup = BeautifulSoup(keynotes_html, 'html.parser')
    keynotes_text = soup.get_text('\n', strip=True)
    
    # Create a DOCX document
    doc = Document()
    title = doc.add_heading('Generated Keynotes', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()  # Add space after the title

    # Add content line by line
    for line in keynotes_text.split('\n'):
        if line.strip():
            paragraph = doc.add_paragraph(line.strip())
            paragraph.space_after = Pt(12)

    # Save the DOCX to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
        doc.save(tmp.name)
        response = send_file(
            tmp.name,
            download_name='keynotes.docx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response._file_to_cleanup = tmp.name
        return response

# Utility function to clean up temporary files
def cleanup_temp_file(filepath):
    """Deletes a temporary file."""
    try:    
        os.unlink(filepath)
    except Exception as e:
        print(f"Error deleting temporary file: {e}")
