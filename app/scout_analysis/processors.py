import os
import re
from flask import current_app

def extract_text_from_file(filepath):
    """Extract text content from various file formats (TXT, PDF, DOCX)"""
    file_ext = filepath.split('.')[-1].lower()
    
    if file_ext == 'txt':
        # Direct text extraction for TXT files
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try different encoding if utf-8 fails
            with open(filepath, 'r', encoding='latin-1') as file:
                return file.read()
    
    elif file_ext == 'pdf':
        # Extract text from PDF files
        try:
            import PyPDF2
            text = ""
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
                return text
        except ImportError:
            current_app.logger.warning("PyPDF2 not installed. Cannot process PDF files.")
            return "ERROR: PyPDF2 package required for PDF processing"
        except Exception as e:
            current_app.logger.error(f"Error extracting text from PDF: {str(e)}")
            return f"ERROR: Failed to extract text from PDF: {str(e)}"
    
    elif file_ext == 'docx':
        # Extract text from DOCX files
        try:
            import docx
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs if para.text])
        except ImportError:
            current_app.logger.warning("python-docx not installed. Cannot process DOCX files.")
            return "ERROR: python-docx package required for DOCX processing"
        except Exception as e:
            current_app.logger.error(f"Error extracting text from DOCX: {str(e)}")
            return f"ERROR: Failed to extract text from DOCX: {str(e)}"
    
    else:
        return f"Unsupported file format: {file_ext}"

def is_scout_report(filepath):
    """Determine if a file is likely a scout report based on content analysis"""
    # First check file extension
    file_ext = filepath.split('.')[-1].lower()
    scout_extensions = current_app.config.get('SCOUT_REPORT_EXTENSIONS', ['txt', 'pdf', 'docx'])
    
    if file_ext not in scout_extensions:
        return False
    
    # Extract text content
    text_content = extract_text_from_file(filepath)
    if text_content.startswith('ERROR:'):
        current_app.logger.warning(f"Could not analyze file content: {text_content}")
        return False
    
    # Define scout report keywords in both English and Chinese
    scout_keywords = [
        'scout report', 'player analysis', 'player profile', 'talent assessment',
        'player evaluation', 'strengths', 'weaknesses', 'basketball skills',
        'draft potential', 'scouting', 'rating', 'scout', 'player development',
        'scout report', 'player analysis', 'player profile', 'technical assessment', 'advantages', 'disadvantages',
        'basketball skills', 'draft potential', 'scouting', 'rating', 'player development'
    ]
    
    # Count keyword occurrences
    keyword_count = sum(1 for keyword in scout_keywords if keyword.lower() in text_content.lower())
    
    # Check for structured report sections
    sections_patterns = [
        r'strengths[：:].+?weaknesses[：:]',
        r'advantages[：:].+?disadvantages[：:]',
        r'player info|player information',
        r'overall rating|comprehensive rating',
        r'development|development direction'
    ]
    
    section_count = 0
    for pattern in sections_patterns:
        if re.search(pattern, text_content.lower(), re.DOTALL):
            section_count += 1
    
    # Determine if it's a scout report based on keywords and structure
    is_scout = (keyword_count >= 3) or (section_count >= 2)
    
    return is_scout
