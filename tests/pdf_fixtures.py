"""Small synthetic PDFs; no private files or third-party documents."""


def text_pdf(
    pages=("Public orbit launch is Monday.",),
    catalog_extra=b"",
    compressed=False,
    unicode_map=False,
    content_streams=None,
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
        if content_streams is not None:
            stream = content_streams[len(children) - 1]
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


def public_pdf_profiles():
    """Reproducible developer-generated layouts; no private/third-party files."""

    def positioned(pages, compressed=False):
        streams = []
        for page in pages:
            parts = []
            for x, y, text in page:
                escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                parts.append(f"BT /F1 10 Tf 1 0 0 1 {x} {y} Tm ({escaped}) Tj ET\n")
            streams.append("".join(parts).encode("ascii"))
        return text_pdf(tuple("" for _ in pages), compressed=compressed, content_streams=streams)

    dense = [
        [(72, 760, "Public planning report")]
        + [
            (
                72,
                740 - row * 12,
                f"Line {row:02}: selected facts remain imported and need owner review.",
            )
            for row in range(50)
        ]
        for _ in range(16)
    ]
    table = [
        [
            (72, 760, "Public inventory"),
            (72, 730, "Item"),
            (300, 730, "Count"),
            (72, 710, name),
            (300, 710, count),
        ]
        for name, count in (("Mars", "3"), ("Venus", "5"))
    ]
    return [
        {
            "key": "single-page",
            "raw": text_pdf(),
            "pages": 1,
            "fragments": ["Public orbit launch is Monday."],
        },
        {
            "key": "columns",
            "raw": positioned(
                [
                    [
                        (72, 740, "Public report"),
                        (72, 710, "Left alpha"),
                        (300, 710, "Right beta"),
                        (72, 690, "Left gamma"),
                        (300, 690, "Right delta"),
                    ]
                ]
            ),
            "pages": 1,
            "fragments": ["Left alpha", "Right beta", "Left gamma", "Right delta"],
        },
        {
            "key": "table-repeated-header",
            "raw": positioned(table),
            "pages": 2,
            "fragments": ["Public inventory", "Mars", "Venus", "3", "5"],
        },
        {
            "key": "unicode-map",
            "raw": text_pdf(("Public \xa0 \xa1",), unicode_map=True),
            "pages": 1,
            "fragments": ["😀", "e\u0301"],
        },
        {
            "key": "dense-16-pages",
            "raw": positioned(dense),
            "pages": 16,
            "fragments": ["Line 00:", "Line 49:"],
        },
        {
            "key": "compressed-16-pages",
            "raw": positioned(dense, compressed=True),
            "pages": 16,
            "fragments": ["Line 00:", "Line 49:"],
        },
    ]
