"""Small synthetic PDFs; no private files or third-party documents."""

def text_pdf(pages=("Public orbit launch is Monday.",)):
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b""]
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    children = []
    for text in pages:
        number = len(objects) + 1
        children.append(f"{number} 0 R")
        objects.append((f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {number+1} 0 R >>").encode())
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin1")
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode()+stream+b"\nendstream")
    objects[1] = f"<< /Type /Pages /Count {len(children)} /Kids [{' '.join(children)}] >>".encode()
    raw = b"%PDF-1.4\n"; offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(raw)); raw += f"{i} 0 obj\n".encode()+obj+b"\nendobj\n"
    start = len(raw)
    raw += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
    raw += b"".join(f"{x:010} 00000 n \n".encode() for x in offsets[1:])
    raw += f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode()
    return raw
