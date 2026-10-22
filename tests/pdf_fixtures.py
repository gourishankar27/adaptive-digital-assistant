"""Small synthetic PDFs; no private files or third-party documents."""


def text_pdf(
    pages=("Public orbit launch is Monday.",),
    catalog_extra=b"",
    compressed=False,
    unicode_map=False,
):
    objects = [b"<< /Type /Catalog /Pages 2 0 R " + catalog_extra + b" >>", b""]
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    children = []
    for text in pages:
        number = len(objects) + 1
        children.append(f"{number} 0 R")
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {number + 1} 0 R >>"
            ).encode()
        )
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin1")
        if compressed:
            import zlib

            stream = zlib.compress(stream)
        objects.append(
            f"<< /Length {len(stream)} {'/Filter /FlateDecode' if compressed else ''} >>\nstream\n".encode()
            + stream
            + b"\nendstream"
        )
    if unicode_map:
        mapping = b"/CIDInit /ProcSet findresource begin 12 dict begin begincmap /CIDSystemInfo << /Registry (Public) /Ordering (Unicode) /Supplement 0 >> def /CMapName /PublicUnicode def /CMapType 2 def 1 begincodespacerange <00> <FF> endcodespacerange 2 beginbfchar <A0> <D83DDE00> <A1> <00650301> endbfchar endcmap CMapName currentdict /CMap defineresource pop end end"
        objects[2] = (
            f"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /ToUnicode {len(objects) + 1} 0 R >>".encode()
        )
        objects.append(
            f"<< /Length {len(mapping)} >>\nstream\n".encode() + mapping + b"\nendstream"
        )
    objects[1] = f"<< /Type /Pages /Count {len(children)} /Kids [{' '.join(children)}] >>".encode()
    raw = b"%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(raw))
        raw += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    start = len(raw)
    raw += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
    raw += b"".join(f"{x:010} 00000 n \n".encode() for x in offsets[1:])
    raw += f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode()
    return raw
