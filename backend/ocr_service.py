"""
Document and Image Text Extraction (OCR) Service
Processes uploaded FIR copies, bounced cheques, agreements, notices, and screenshots.
"""

import os
import logging
from typing import Optional
from pypdf import PdfReader
from PIL import Image

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str, mime_type: str) -> str:
    """
    Extract readable text from uploaded PDFs, documents, or images.
    """
    if not os.path.exists(file_path):
        return ""

    file_ext = os.path.splitext(file_path)[1].lower()

    # 1. PDF Documents
    if file_ext == ".pdf" or "pdf" in mime_type:
        try:
            reader = PdfReader(file_path)
            extracted_pages = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(f"--- [Page {i+1}] ---\n{page_text.strip()}")
            result = "\n\n".join(extracted_pages)
            if result.strip():
                return result
            return f"[PDF uploaded: {os.path.basename(file_path)}. Scanned image document without embedded text layer.]"
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            return f"[Error extracting text from PDF: {str(e)}]"

    # 2. Image Files (PNG, JPG, JPEG, WEBP)
    elif file_ext in [".png", ".jpg", ".jpeg", ".webp"] or "image" in mime_type:
        try:
            image = Image.open(file_path)
            import pytesseract
            # Check if tesseract binary is accessible
            text = pytesseract.image_to_string(image)
            if text.strip():
                return f"--- [Extracted Image Text] ---\n{text.strip()}"
            return f"[Image uploaded: {os.path.basename(file_path)}. Dimensions: {image.width}x{image.height}. No clear text recognized.]"
        except Exception as e:
            logger.info(f"Tesseract OCR not active or failed: {e}. Returning image metadata descriptor.")
            filename = os.path.basename(file_path)
            return (
                f"[Uploaded Image: {filename}]\n"
                f"Document attached to case file. Key evidence type: {infer_document_type(filename)}"
            )

    # 3. Plain text / Markdown
    elif file_ext in [".txt", ".md", ".csv"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            return f"[Error reading text file: {e}]"

    return f"[Attached file: {os.path.basename(file_path)}]"


def infer_document_type(filename: str) -> str:
    """Infer common Pakistani legal document type from filename."""
    name_lower = filename.lower()
    if "fir" in name_lower:
        return "First Information Report (FIR) Copy"
    elif "cheque" in name_lower or "check" in name_lower:
        return "Bank Cheque / Dishonour Slip (PPC 489-F Evidence)"
    elif "notice" in name_lower:
        return "Legal Demand Notice"
    elif "agreement" in name_lower or "contract" in name_lower:
        return "Written Contract / Stamp Paper Agreement"
    elif "rent" in name_lower or "tenancy" in name_lower:
        return "Tenancy / Lease Agreement"
    elif "nikah" in name_lower or "marriage" in name_lower:
        return "Nikahnama / Marriage Certificate"
    elif "fard" in name_lower or "registry" in name_lower or "plot" in name_lower:
        return "Property Title Deed / Revenue Fard"
    elif "cnic" in name_lower:
        return "Identity Document (CNIC)"
    return "Legal Supporting Document / Screenshot"
