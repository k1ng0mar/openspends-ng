"""
OpenSpends NG — PDF Budget Parser

Parses Nigerian budget PDFs (BOF Appropriation Bills, Quarterly Implementation Reports)
into structured records ready for DB ingestion.

Supports:
- tabula-py (Java-based, good for structured tables)
- camelot (Python-native, better for bordered tables)
- pymupdf (fallback, text extraction + OCR coordination)

Strategy:
1. Try camelot first (most accurate for bordered tables)
2. Fall back to tabula if camelot fails
3. Use pymupdf for metadata + text-only pages
"""

import logging
from pathlib import Path
from typing import Optional
import tempfile

import camelot
import tabula
import fitz  # pymupdf
import pandas as pd

logger = logging.getLogger(__name__)


class BudgetPDFParser:
    """Parse Nigerian budget PDFs into structured DataFrames."""

    # Expected column patterns in BOF budget tables
    COLUMN_PATTERNS = {
        "appropriation": [
            "MDA", "MINISTRY", "DEPARTMENT", "AGENCY",
            "PERSONNEL", "OVERHEAD", "CAPITAL", "TOTAL",
            "PERSONNEL COST", "OVERHEAD COST", "CAPITAL EXPENDITURE",
        ],
        "implementation": [
            "MDA", "APPROVED BUDGET", "ACTUAL RELEASE",
            "ACTUAL EXPENDITURE", "IMPLEMENTATION", "%",
        ],
    }

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        self._doc = None

    @property
    def doc(self):
        if self._doc is None:
            self._doc = fitz.open(str(self.pdf_path))
        return self._doc

    # ── Metadata ──

    def get_metadata(self) -> dict:
        """Extract PDF metadata (title, page count, etc.)."""
        meta = self.doc.metadata
        return {
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "page_count": len(self.doc),
            "file_name": self.pdf_path.name,
            "file_size_kb": round(self.pdf_path.stat().st_size / 1024, 1),
        }

    def get_page_text(self, page_num: int) -> str:
        """Extract raw text from a single page (0-indexed)."""
        if page_num >= len(self.doc):
            raise ValueError(f"Page {page_num} out of range ({len(self.doc)} pages)")
        return self.doc[page_num].get_text()

    # ── Table Extraction ──

    def extract_tables_camelot(
        self,
        pages: str = "all",
        flavor: str = "lattice",  # "lattice" for bordered, "stream" for whitespace-delimited
    ) -> list[pd.DataFrame]:
        """
        Extract tables using camelot.
        Best for: bordered tables in BOF Appropriation Bills.
        """
        try:
            tables = camelot.read_pdf(
                str(self.pdf_path),
                pages=pages,
                flavor=flavor,
                suppress_stdout=True,
            )
            logger.info(f"camelot: extracted {len(tables)} tables")
            return [t.df for t in tables]
        except Exception as e:
            logger.warning(f"camelot extraction failed: {e}")
            return []

    def extract_tables_tabula(
        self,
        pages: str = "all",
        multiple_tables: bool = True,
    ) -> list[pd.DataFrame]:
        """
        Extract tables using tabula-py.
        Best for: whitespace-separated tables, multi-column layouts.
        """
        try:
            tables = tabula.read_pdf(
                str(self.pdf_path),
                pages=pages,
                multiple_tables=multiple_tables,
                pandas_options={"header": 0},
                silent=True,
            )
            tables = [t for t in tables if not t.empty]
            logger.info(f"tabula: extracted {len(tables)} tables")
            return tables
        except Exception as e:
            logger.warning(f"tabula extraction failed: {e}")
            return []

    def extract_tables(self, pages: str = "all") -> list[pd.DataFrame]:
        """
        Best-effort table extraction.
        Tries camelot first, then tabula, merges results.
        """
        tables = self.extract_tables_camelot(pages=pages)

        if not tables:
            logger.info("camelot found no tables, trying tabula")
            tables = self.extract_tables_tabula(pages=pages)

        if not tables:
            # Try camelot stream mode (for borderless tables)
            tables = self.extract_tables_camelot(pages=pages, flavor="stream")

        return tables

    # ── Nigerian Budget Specific Parsing ──

    def classify_page(self, page_num: int) -> str:
        """
        Classify a budget PDF page by content type.
        Returns: "appropriation" | "implementation" | "summary" | "other"
        """
        text = self.get_page_text(page_num).lower()

        if any(kw in text for kw in ["appropriation", "approved budget", "total appropriation"]):
            if any(kw in text for kw in ["personnel", "overhead", "capital"]):
                return "appropriation"
        if any(kw in text for kw in ["implementation", "actual release", "actual expenditure"]):
            return "implementation"
        if any(kw in text for kw in ["summary", "total", "grand total"]):
            return "summary"

        return "other"

    def parse_appropriation_table(self, df: pd.DataFrame) -> list[dict]:
        """
        Parse a raw appropriation table DataFrame into clean records.
        Handles common BOF column naming variations.
        """
        # Normalize column names
        df.columns = [str(c).strip().upper() for c in df.columns]

        # Map common column name variations
        column_map = {}
        for col in df.columns:
            if any(kw in col for kw in ["MDA", "MINISTRY", "DEPARTMENT", "AGENCY", "ORGANIZATION"]):
                column_map[col] = "mda_name"
            elif any(kw in col for kw in ["PERSONNEL", "SALARY", "SALARIES"]):
                column_map[col] = "personnel_cost"
            elif any(kw in col for kw in ["OVERHEAD", "RECURRENT"]):
                column_map[col] = "overhead_cost"
            elif any(kw in col for kw in ["CAPITAL", "FIXED ASSET"]):
                column_map[col] = "capital_expenditure"
            elif any(kw in col for kw in ["TOTAL", "AGGREGATE", "SUM"]):
                column_map[col] = "total"

        df = df.rename(columns=column_map)

        # Keep only mapped columns
        keep_cols = ["mda_name", "personnel_cost", "overhead_cost", "capital_expenditure", "total"]
        existing = [c for c in keep_cols if c in df.columns]

        if "mda_name" not in existing:
            logger.warning("Could not identify MDA name column, skipping table")
            return []

        df = df[existing]

        # Clean numeric columns
        for col in ["personnel_cost", "overhead_cost", "capital_expenditure", "total"]:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("₦", "", regex=False)
                    .str.replace("N", "", regex=False)
                    .str.strip()
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Drop rows where mda_name is empty or looks like a header
        df = df.dropna(subset=["mda_name"])
        df = df[~df["mda_name"].str.contains("TOTAL|SUB-TOTAL|GRAND", case=False, na=False)]

        return df.to_dict(orient="records")

    def parse_full_budget(self) -> dict:
        """
        Full pipeline: extract + classify + parse all tables in the PDF.
        Returns structured dict with metadata and parsed records.
        """
        meta = self.get_metadata()
        logger.info(f"Parsing {meta['file_name']} ({meta['page_count']} pages)")

        all_tables = self.extract_tables()
        appropriation_records = []
        implementation_records = []
        raw_tables = []

        for i, df in enumerate(all_tables):
            raw_tables.append({"index": i, "columns": list(df.columns), "rows": len(df)})

            # Try to parse as appropriation
            records = self.parse_appropriation_table(df)
            if records:
                appropriation_records.extend(records)
            else:
                # Store raw for manual review
                raw_tables[-1]["sample"] = df.head(3).to_dict()

        logger.info(
            f"Parsed {len(appropriation_records)} appropriation records, "
            f"{len(raw_tables)} total tables found"
        )

        return {
            "metadata": meta,
            "appropriation_records": appropriation_records,
            "implementation_records": implementation_records,
            "raw_tables": raw_tables,
        }

    # ── Cleanup ──

    def close(self):
        if self._doc:
            self.close_doc()

    def close_doc(self):
        if self._doc:
            self._doc.close()
            self._doc = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ── Convenience Functions ──

def parse_budget_pdf(pdf_path: str) -> dict:
    """One-shot parse a budget PDF."""
    with BudgetPDFParser(pdf_path) as parser:
        return parser.parse_full_budget()


def parse_from_url(url: str) -> dict:
    """Download and parse a budget PDF from a URL."""
    import httpx

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        response = httpx.get(url, timeout=60, follow_redirects=True)
        response.raise_for_status()
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        return parse_budget_pdf(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
