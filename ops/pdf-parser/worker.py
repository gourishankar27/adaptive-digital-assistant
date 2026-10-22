"""No network/files/credentials: one bounded PDF on stdin, extracted pages on stdout."""
import hashlib
import io
import json
import logging
import resource
import sys

resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
resource.setrlimit(resource.RLIMIT_CPU, (6, 6))
logging.disable(logging.CRITICAL)

from pypdf import PdfReader  # noqa: E402
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject  # noqa: E402

PARSER = "pypdf-6.21.2-text-v1"
FORBIDDEN = {"/JS", "/JavaScript", "/EmbeddedFiles", "/Filespec", "/Launch", "/GoToR", "/URI", "/RichMedia", "/XFA", "/AcroForm", "/AA", "/OpenAction", "/Encrypt"}

def main():
    raw = sys.stdin.buffer.read(262145)
    if not 1 <= len(raw) <= 262144 or not raw.startswith(b"%PDF-") or not raw.rstrip().endswith(b"%%EOF"):
        raise ValueError("pdf_invalid")
    reader = PdfReader(io.BytesIO(raw), strict=True)
    if reader.is_encrypted:
        raise ValueError("pdf_encrypted")
    visited, stack, count = set(), [reader.trailer], 0
    while stack:
        value = stack.pop(); count += 1
        if count > 50000:
            raise ValueError("pdf_object_limit")
        if isinstance(value, IndirectObject):
            key = (value.idnum, value.generation)
            if key in visited: continue
            visited.add(key); stack.append(value.get_object())
        elif isinstance(value, DictionaryObject):
            if any(str(k) in FORBIDDEN for k in value) or value.get('/Subtype') == '/Link':
                raise ValueError("pdf_active_content")
            stack.extend(value.values())
        elif isinstance(value, ArrayObject): stack.extend(value)
    if not 1 <= len(reader.pages) <= 16:
        raise ValueError("pdf_page_limit")
    pages, text = [], ""
    for index, page in enumerate(reader.pages, 1):
        extracted = (page.extract_text() or "").replace("\r\n", "\n").replace("\r", "\n")
        if not extracted.strip(): raise ValueError("pdf_ocr_required")
        extracted = extracted.rstrip("\n") + "\n"
        start = len(text); text += extracted
        if len(text.encode('utf-8')) > 262144: raise ValueError("pdf_text_limit")
        pages.append({"page":index,"span_start":start,"span_end":len(text),"text_hash":hashlib.sha256(extracted.encode()).hexdigest()})
    return {"text":text,"pages":pages,"raw_hash":hashlib.sha256(raw).hexdigest(),"text_hash":hashlib.sha256(text.encode()).hexdigest(),"parser":PARSER,"normalization":"lf-page-newline-v1","warnings":["Reading order, columns, tables and hidden text require visual verification; OCR is disabled."]}

try:
    result = main()
except Exception as error:
    allowed = {"pdf_invalid","pdf_encrypted","pdf_object_limit","pdf_active_content","pdf_page_limit","pdf_ocr_required","pdf_text_limit"}
    code = str(error)
    result = {"error":code if code in allowed else "pdf_malformed"}
sys.stdout.write(json.dumps(result,ensure_ascii=True,separators=(',',':')))
