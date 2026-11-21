# -*- coding: utf-8 -*-
"""Document I/O: .docx / .md / .markdown / .txt behind one block-and-write interface.

Cross-platform and independent of Microsoft Word: PDF export prefers LibreOffice (present on
Windows, macOS and Linux) and only falls back to Word COM on Windows. Plain text and Markdown
are read and written directly, with no external program involved.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import docx

TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".mdown"}
SUPPORTED_SUFFIXES = TEXT_SUFFIXES | {".docx"}

SKIP_STYLE_PREFIXES = ("Heading", "Title", "Subtitle", "TOC", "Caption", "Bibliography")
SKIP_PATTERNS = [
    r"^图\s*\d", r"^表\s*\d", r"^Figure\s*\d", r"^Table\s*\d",
    r"^\[\d+\]", r"^\d+\.\s*\S{0,40}$",
    r"^(参考文献|References|Bibliography|致谢|Acknowledg)", r"^(Key ?words|关键词|摘要|Abstract)",
]
CODE_FONT_HINTS = ("Consolas", "Courier", "Mono")

MD_SKIP_PREFIXES = (
    "#", "```", "~~~", ">", "|", "---", "***", "![", "[!", "<",
    "    ", "\t",
)


def text_units(text: str) -> int:
    """Language-neutral length: CJK characters plus English word tokens."""
    return len(re.findall(r"[\u4e00-\u9fff]", text)) + len(re.findall(r"[A-Za-z][A-Za-z'-]*", text))


FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _fenced_lines(lines: List[str]) -> List[bool]:
    """Flag every line that sits inside a code fence, including the fence lines themselves."""
    flags, inside = [], False
    for line in lines:
        if FENCE_RE.match(line):
            flags.append(True)
            inside = not inside
            continue
        flags.append(inside)
    return flags


def _md_reason(block: str, fenced: bool) -> Optional[str]:
    first = block.split(chr(10), 1)[0]
    if fenced:
        return "code-fence"
    if first.startswith("#"):
        return "md:heading"
    if first.startswith("|"):
        return "md:table"
    if re.match(r"^\[[^\]]+]\: \s", first):
        return "md:link-def"
    for prefix in (">", "---", "***", "![", "[!", "<", "    ", chr(9)):
        if first.startswith(prefix):
            return f"md:{prefix.strip()}"
    return None


class DocxDocument:
    """Backed by python-docx. Paragraph styles survive; runs inside a paragraph are merged."""

    kind = "docx"

    def __init__(self, path: str):
        self.path = path
        self.doc = docx.Document(path)

    def units(self, min_words: int) -> Tuple[List[Dict], List[Dict]]:
        targets, skipped = [], []
        for idx, p in enumerate(self.doc.paragraphs):
            reason = self._skip_reason(p)
            text = p.text.strip()
            if reason:
                if text:
                    skipped.append({"idx": idx, "reason": reason, "text": text[:60]})
                continue
            if text_units(text) < min_words:
                skipped.append({"idx": idx, "reason": "below-min-words", "text": text[:60]})
                continue
            targets.append({"idx": idx, "text": text, "word_count": text_units(text)})
        return targets, skipped

    def _skip_reason(self, p) -> Optional[str]:
        style = (p.style.name if p.style is not None else "") or ""
        if style.startswith(SKIP_STYLE_PREFIXES):
            return f"style:{style}"
        text = p.text.strip()
        if not text:
            return "empty"
        if text_units(text) < 5:
            return "too-short"
        for pat in SKIP_PATTERNS:
            if re.search(pat, text, flags=re.I):
                return f"pattern:{pat}"
        for run in p.runs[:4]:
            name = (run.font.name if run.font is not None else "") or ""
            if any(hint in name for hint in CODE_FONT_HINTS):
                return "code-font"
        return None

    def set_text(self, idx: int, text: str) -> None:
        p = self.doc.paragraphs[idx]
        if p.runs:
            p.runs[0].text = text
            for run in p.runs[1:]:
                run.text = ""
        else:
            p.text = text

    def save(self, out_path: str) -> None:
        self.doc.save(out_path)
        if out_path.lower().endswith(".docx"):
            scrub_docx_metadata(out_path)


class PlainDocument:
    """Plain text and Markdown: blocks split on blank lines, replaced as a whole."""

    def __init__(self, path: str):
        self.path = path
        self.is_markdown = Path(path).suffix.lower() in {".md", ".markdown", ".mdown"}
        with open(path, "r", encoding="utf-8-sig") as fh:
            self.lines = fh.read().split("\n")
        self.blocks: List[Tuple[int, int]] = []
        self._split_blocks()

    @property
    def kind(self) -> str:
        return "markdown" if self.is_markdown else "text"

    def _split_blocks(self) -> None:
        start = None
        for i, line in enumerate(self.lines):
            if line.strip():
                if start is None:
                    start = i
            elif start is not None:
                self.blocks.append((start, i))
                start = None
        if start is not None:
            self.blocks.append((start, len(self.lines)))

    def _block_text(self, bidx: int) -> str:
        start, end = self.blocks[bidx]
        return "\n".join(self.lines[start:end]).strip()

    def units(self, min_words: int) -> Tuple[List[Dict], List[Dict]]:
        targets, skipped = [], []
        fenced = _fenced_lines(self.lines) if self.is_markdown else [False] * len(self.lines)
        for bidx, (start, end) in enumerate(self.blocks):
            text = self._block_text(bidx)
            reason = _md_reason(text, any(fenced[start:end])) if self.is_markdown else None
            if reason:
                skipped.append({"idx": bidx, "reason": reason, "text": text[:60]})
                continue
            if text_units(text) < min_words:
                skipped.append({"idx": bidx, "reason": "below-min-words", "text": text[:60]})
                continue
            targets.append({"idx": bidx, "text": text, "word_count": text_units(text)})
        return targets, skipped

    def set_text(self, idx: int, text: str) -> None:
        start, end = self.blocks[idx]
        new_lines = text.split("\n")
        self.lines[start:end] = new_lines
        # The block length changed, so recompute the offsets that follow.
        self.blocks = []
        self._split_blocks()

    def save(self, out_path: str) -> None:
        with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(self.lines))


def load_document(path: str):
    suffix = Path(path).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(
            f"Unsupported format {suffix or '(no extension)'}; supported: "
            + ", ".join(sorted(SUPPORTED_SUFFIXES))
            + ". Re-save legacy .doc as .docx first.")
    if suffix == ".docx":
        return DocxDocument(path)
    return PlainDocument(path)


def scrub_docx_metadata(docx_path: str, title: str = "", subject: str = "") -> None:
    tmp = docx_path + ".clean.tmp"
    clean_core = (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f"<dc:title>{title}</dc:title><dc:subject>{subject}</dc:subject>"
        "<dc:creator/><cp:keywords/><dc:description/><cp:lastModifiedBy/>"
        "<cp:revision>1</cp:revision></cp:coreProperties>"
    )
    with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = clean_core.encode("utf-8") if item.filename == "docProps/core.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    os.replace(tmp, docx_path)


def _find_soffice() -> Optional[str]:
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
    ]
    return next((c for c in candidates if os.path.exists(c)), None)


def _export_pdf_word(docx_path: str, pdf_path: str) -> None:
    docx_abs = str(Path(docx_path).resolve())
    pdf_abs = str(Path(pdf_path).resolve())
    ps = (
        "$w = New-Object -ComObject Word.Application; $w.Visible = $false; $w.DisplayAlerts = 0; "
        f"try {{ $d = $w.Documents.Open('{docx_abs}', $false, $true); "
        f"$d.ExportAsFixedFormat('{pdf_abs}', 17, $false, 0, 0, 1, 1, 0, $false, $true, 1, $true, $true, $false); "
        "$d.Close($false) } finally { $w.Quit() }"
    )
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                   check=True, timeout=300)


def export_pdf(src_path: str, pdf_path: str) -> str:
    """docx -> pdf. LibreOffice first, Word on Windows second. Returns the engine used."""
    if not src_path.lower().endswith(".docx"):
        raise RuntimeError("Only .docx can be exported to PDF; use the rewritten text or Markdown as-is, or convert it with pandoc.")

    soffice = _find_soffice()
    if soffice:
        outdir = tempfile.mkdtemp(prefix="deai-pdf-")
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, src_path],
                       check=True, timeout=600,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        produced = Path(outdir) / (Path(src_path).stem + ".pdf")
        if not produced.exists():
            raise RuntimeError(f"LibreOffice produced no PDF in {outdir}")
        shutil.move(str(produced), pdf_path)
        shutil.rmtree(outdir, ignore_errors=True)
        engine = "libreoffice"
    elif sys.platform == "win32":
        _export_pdf_word(src_path, pdf_path)
        engine = "word"
    else:
        raise RuntimeError(
            "No PDF converter found. Install LibreOffice (cross-platform) and retry; "
            "an installed Microsoft Word also works on Windows.")

    try:
        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({"/Title": "", "/Subject": "", "/Author": "", "/Keywords": "",
                             "/Creator": "de-ai", "/Producer": ""})
        tmp = pdf_path + ".tmp"
        with open(tmp, "wb") as fh:
            writer.write(fh)
        os.replace(tmp, pdf_path)
    except Exception as exc:
        raise RuntimeError(f"PDF written but metadata scrubbing failed: {exc}") from exc
    return engine
