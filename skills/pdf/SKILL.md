---
name: pdf
description: Read, create, merge, and extract data from PDF files
---

# PDF Skill

Work with PDF files: read text, create documents, merge/split, extract tables, and convert formats.

## Available Tools

### Python Libraries

Install as needed:
```bash
pip install PyPDF2 pdfplumber reportlab fpdf2
```

| Library | Use Case |
|---------|----------|
| `pdfplumber` | Extract text, tables from existing PDFs |
| `PyPDF2` | Merge, split, rotate, encrypt PDFs |
| `reportlab` | Create PDFs from scratch (advanced) |
| `fpdf2` | Create simple PDFs quickly |

## Common Operations

### 1. Extract Text from PDF

```python
import pdfplumber

def extract_text(pdf_path: str, pages: list[int] | None = None) -> str:
    """Extract text from PDF. pages=None means all pages."""
    with pdfplumber.open(pdf_path) as pdf:
        if pages:
            texts = [pdf.pages[p].extract_text() or "" for p in pages]
        else:
            texts = [page.extract_text() or "" for page in pdf.pages]
    return "\n\n--- Page Break ---\n\n".join(texts)
```

### 2. Extract Tables from PDF

```python
import pdfplumber
import json

def extract_tables(pdf_path: str, page_num: int = 0) -> list[list[list[str]]]:
    """Extract all tables from a specific page."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        tables = page.extract_tables()
    return tables

def tables_to_csv(pdf_path: str, output_dir: str = "."):
    """Export all tables from all pages to CSV files."""
    import csv
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            for j, table in enumerate(page.extract_tables()):
                if table:
                    path = f"{output_dir}/table_p{i+1}_{j+1}.csv"
                    with open(path, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(table)
                    print(f"Wrote {path}")
```

### 3. Merge PDFs

```python
from PyPDF2 import PdfMerger

def merge_pdfs(pdf_paths: list[str], output: str):
    """Merge multiple PDFs into one."""
    merger = PdfMerger()
    for path in pdf_paths:
        merger.append(path)
    merger.write(output)
    merger.close()
    print(f"Merged {len(pdf_paths)} PDFs → {output}")
```

### 4. Split PDF

```python
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(pdf_path: str, page_ranges: dict[str, tuple[int, int]]):
    """Split PDF into multiple files.
    
    page_ranges: {"part1.pdf": (0, 5), "part2.pdf": (5, 10)}
    Pages are 0-indexed, end is exclusive.
    """
    reader = PdfReader(pdf_path)
    for output_path, (start, end) in page_ranges.items():
        writer = PdfWriter()
        for i in range(start, min(end, len(reader.pages))):
            writer.add_page(reader.pages[i])
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"Wrote {output_path} (pages {start+1}-{end})")
```

### 5. Create PDF with fpdf2

```python
from fpdf import FPDF

def create_pdf(text: str, output: str, title: str = "Document"):
    """Create a simple PDF from text content."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, text)
    pdf.output(output)
    print(f"Created {output}")
```

### 6. Get PDF Metadata

```python
from PyPDF2 import PdfReader

def get_metadata(pdf_path: str) -> dict:
    """Extract PDF metadata."""
    reader = PdfReader(pdf_path)
    info = reader.metadata
    return {
        "pages": len(reader.pages),
        "title": info.title if info else None,
        "author": info.author if info else None,
        "creator": info.creator if info else None,
    }
```

## Workflow: Analyze a PDF

When user asks to analyze a PDF:

1. **Read metadata** — get page count, title
2. **Extract text** — read content with pdfplumber
3. **Extract tables** — if tables exist, export to CSV
4. **Summarize** — use extracted text to answer questions

```bash
# Quick one-liner approach
python3 -c "
import pdfplumber
with pdfplumber.open('input.pdf') as pdf:
    for i, page in enumerate(pdf.pages):
        print(f'--- Page {i+1} ---')
        print(page.extract_text()[:500])
"
```

## Workflow: Create Report PDF

When user asks to create a PDF report:

1. Gather content (text, data, tables)
2. Use `fpdf2` for simple docs, `reportlab` for complex layouts
3. Include headers, page numbers, and proper formatting

## Error Handling

- Always check if file exists before processing
- Handle encrypted PDFs (try with password)
- Handle scanned PDFs (no extractable text → suggest OCR)
- Large PDFs: process page by page, don't load all into memory

```python
# Handle encrypted PDF
reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("password")
```

## Tips

- For scanned PDFs (images), text extraction won't work — use `pytesseract` OCR
- pdfplumber is better than PyPDF2 for text/table extraction
- PyPDF2 is better for manipulation (merge, split, rotate)
- Always close file handles properly (use `with` statements)
