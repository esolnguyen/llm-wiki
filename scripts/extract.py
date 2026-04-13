#!/usr/bin/env python3
"""Extract text from a source file and save as markdown next to it.

Usage:
    python scripts/extract.py raw/paper.pdf
    python scripts/extract.py raw/                  # process all files in directory

For a single file, outputs <full_name>.md next to the source
(e.g. raw/paper.pdf -> raw/paper.pdf.md). Keeping the original extension
in the filename prevents collisions between e.g. paper.pdf and paper.html.
If the target .md already exists and is newer than the source, extraction is skipped.

Dispatches by file extension:
    .pdf                            -> pymupdf4llm (fast, pure Python, high quality for PDFs)
    .docx/.pptx/.xlsx/.html/.epub/  -> markitdown (broad format support)
    .jpg/.png/.etc (with OCR)
    .md/.txt                        -> skipped (already text)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Extensions that are already text — no extraction needed.
PASSTHROUGH_EXTS = {".md", ".markdown", ".txt"}

# Extensions pymupdf4llm handles best.
PDF_EXTS = {".pdf"}

# Extensions markitdown handles.
MARKITDOWN_EXTS = {
    ".docx", ".doc",
    ".pptx", ".ppt",
    ".xlsx", ".xls",
    ".html", ".htm",
    ".epub",
    ".csv",
    ".json",
    ".xml",
    ".zip",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
}


def extract_pdf(src: Path) -> str:
    """Extract a PDF to markdown using pymupdf4llm."""
    import pymupdf4llm
    return pymupdf4llm.to_markdown(str(src))


def extract_markitdown(src: Path) -> str:
    """Extract any markitdown-supported format."""
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(str(src))
    return result.text_content


def extract_one(src: Path) -> str | None:
    """Extract a single file. Returns the destination path (or None if skipped)."""
    if not src.exists() or not src.is_file():
        print(f"  [skip] not a file: {src}", file=sys.stderr)
        return None

    ext = src.suffix.lower()

    # Already-text files don't need extraction.
    if ext in PASSTHROUGH_EXTS:
        print(f"  [skip] already text: {src.name}")
        return None

    # Skip previously-extracted artifacts (e.g. paper.pdf.md).
    if src.name.endswith(".md") and src.stem.rsplit(".", 1)[-1] in {
        e.lstrip(".") for e in (PDF_EXTS | MARKITDOWN_EXTS)
    }:
        print(f"  [skip] extraction artifact: {src.name}")
        return None

    # Keep full original name, append .md (e.g. paper.pdf -> paper.pdf.md).
    dst = src.with_name(src.name + ".md")

    # Skip if target is up-to-date.
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        print(f"  [skip] up-to-date: {dst.name}")
        return str(dst)

    # Dispatch by extension.
    try:
        if ext in PDF_EXTS:
            content = extract_pdf(src)
        elif ext in MARKITDOWN_EXTS:
            content = extract_markitdown(src)
        else:
            print(f"  [skip] unsupported extension {ext}: {src.name}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"  [error] {src.name}: {e}", file=sys.stderr)
        return None

    # Write output with a header noting the extraction provenance.
    header = (
        f"<!-- Extracted from: {src.name} -->\n"
        f"<!-- Extractor: {'pymupdf4llm' if ext in PDF_EXTS else 'markitdown'} -->\n\n"
    )
    dst.write_text(header + content, encoding="utf-8")
    print(f"  [ok]   {src.name} -> {dst.name}")
    return str(dst)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1

    target = Path(sys.argv[1])

    if not target.exists():
        print(f"path not found: {target}", file=sys.stderr)
        return 1

    if target.is_file():
        print(f"Extracting: {target}")
        result = extract_one(target)
        return 0 if result is not None else 1

    if target.is_dir():
        print(f"Extracting all files in: {target}")
        files = sorted(
            p for p in target.rglob("*")
            if p.is_file()
            and p.suffix.lower() not in PASSTHROUGH_EXTS
            and not p.name.startswith(".")
            and "assets" not in p.parts  # skip the assets subfolder
        )
        if not files:
            print("  (no extractable files found)")
            return 0
        for f in files:
            extract_one(f)
        return 0

    print(f"unsupported path type: {target}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
