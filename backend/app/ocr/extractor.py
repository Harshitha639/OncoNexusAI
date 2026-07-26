"""
Medical report OCR / text extraction pipeline.

Strategy:
    * PDF   -> try PyMuPDF (`fitz`) first (fast, works for text-based PDFs).
               If it yields little/no text (e.g. scanned PDF), fall back to
               `pdfplumber`.
    * Image -> EasyOCR.

This module is intentionally dependency-light at import time: the heavy
OCR/PDF libraries are imported lazily inside each function so importing
`app.ocr.extractor` never fails just because, say, EasyOCR isn't needed
for a given request.
"""

from pathlib import Path

from app.core.logging import get_logger
from app.models.enums import ReportFileType

logger = get_logger(__name__)

_MIN_USEFUL_TEXT_LENGTH = 20


class OcrExtractionError(Exception):
    """Raised when no engine could extract usable text from a report file."""


def _extract_with_pymupdf(file_path: Path) -> str:
    import fitz  # PyMuPDF

    text_parts: list[str] = []
    with fitz.open(file_path) as document:
        for page in document:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()


def _extract_with_pdfplumber(file_path: Path) -> str:
    import pdfplumber

    text_parts: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def _extract_with_easyocr(file_path: Path) -> str:
    import easyocr

    # Lazily create (and cache) the reader — model weights are expensive to load.
    reader = _get_easyocr_reader()
    results = reader.readtext(str(file_path), detail=0, paragraph=True)
    return "\n".join(results).strip()


_easyocr_reader = None


def _get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr

        _easyocr_reader = easyocr.Reader(["en"], gpu=False)
    return _easyocr_reader


def extract_text(file_path: str, file_type: ReportFileType) -> tuple[str, str]:
    """Extract text from a report file.

    Returns `(extracted_text, engine_used)`. Raises `OcrExtractionError` if
    no engine could produce usable text.
    """
    path = Path(file_path)

    if file_type == ReportFileType.PDF:
        try:
            text = _extract_with_pymupdf(path)
            if len(text) >= _MIN_USEFUL_TEXT_LENGTH:
                return text, "pymupdf"
            logger.info("PyMuPDF yielded little text for %s; falling back to pdfplumber.", path)
        except Exception as exc:  # noqa: BLE001 — any PyMuPDF failure triggers fallback
            logger.warning("PyMuPDF failed for %s: %s", path, exc)

        try:
            text = _extract_with_pdfplumber(path)
            if len(text) >= _MIN_USEFUL_TEXT_LENGTH:
                return text, "pdfplumber"
        except Exception as exc:  # noqa: BLE001
            logger.warning("pdfplumber failed for %s: %s", path, exc)

        raise OcrExtractionError(
            "Could not extract text from this PDF using PyMuPDF or pdfplumber. "
            "It may be a scanned/image-only PDF."
        )

    # JPG / JPEG / PNG
    try:
        text = _extract_with_easyocr(path)
        if len(text) >= 1:
            return text, "easyocr"
        raise OcrExtractionError("EasyOCR did not detect any text in this image.")
    except OcrExtractionError:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error("EasyOCR failed for %s: %s", path, exc)
        raise OcrExtractionError(f"EasyOCR failed to process the image: {exc}") from exc
