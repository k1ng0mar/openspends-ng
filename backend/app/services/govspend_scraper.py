"""
OpenSpends NG — GovSpend Playwright Scraper

Uses Playwright to render the GovSpend SPA and extract payment data.
"""

import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

CHROMIUM_PATH = "/snap/bin/chromium"
GOVSPEND_URL = "https://www.govspend.ng/explore"

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def parse_govspend_date(date_str: str) -> str:
    """Parse GovSpend date format '31, Mar 2026' to ISO '2026-03-31'."""
    try:
        parts = date_str.replace(",", "").split()
        day = int(parts[0])
        month_str = parts[1].strip().lower()[:3]
        year = int(parts[2])
        month = MONTH_MAP.get(month_str, 1)
        return f"{year:04d}-{month:02d}-{day:02d}"
    except Exception:
        return date_str


def parse_naira(amount_str: str) -> float:
    """Parse ₦134,246,912.75 to 134246912.75."""
    try:
        return float(amount_str.replace("₦", "").replace(",", "").strip())
    except Exception:
        return 0.0


class GovSpendScraperPlaywright:
    """Render GovSpend SPA with Playwright and extract payment data."""

    def scrape_page(self, url: str = GOVSPEND_URL) -> list[dict]:
        """Scrape a single page of GovSpend data."""
        from playwright.sync_api import sync_playwright

        payments = []
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=CHROMIUM_PATH,
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(8000)

            # Extract table rows via JS
            rows = page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('table tbody tr, table tr:not(:first-child)');
                    return Array.from(rows).map(row =>
                        Array.from(row.querySelectorAll('td')).map(c => c.innerText.trim())
                    );
                }
            """)

            for row in rows:
                if len(row) >= 5:
                    payments.append({
                        "date": parse_govspend_date(row[0]),
                        "mda": row[1].strip() if len(row) > 1 else "",
                        "beneficiary": row[2].strip() if len(row) > 2 else "",
                        "amount": parse_naira(row[3]) if len(row) > 3 else 0,
                        "description": row[4].strip() if len(row) > 4 else "",
                        "payment_ref": row[5].strip() if len(row) > 5 else "",
                        "payer_code": row[6].strip() if len(row) > 6 else "",
                        "source": "govspend",
                    })

            browser.close()
        return payments

    def scrape_all(self, max_pages: int = 1) -> list[dict]:
        """Scrape multiple pages of GovSpend (clicks pagination)."""
        from playwright.sync_api import sync_playwright

        all_payments = []
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=CHROMIUM_PATH,
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            page = browser.new_page()
            page.goto(GOVSPEND_URL, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(8000)

            for page_num in range(1, max_pages + 1):
                if page_num > 1:
                    # Try clicking next page
                    try:
                        next_btn = page.query_selector("button[aria-label='Next page'], a[rel='next']")
                        if not next_btn:
                            # Try pagination links
                            pagination = page.query_selector_all("[class*='pagination'] a, [class*='page'] a")
                            for link in pagination:
                                if str(page_num) in (link.inner_text() or ""):
                                    link.click()
                                    page.wait_for_timeout(3000)
                                    break
                            else:
                                break
                        else:
                            next_btn.click()
                            page.wait_for_timeout(3000)
                    except Exception:
                        break

                rows = page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('table tbody tr, tr:not(:first-child)');
                        return Array.from(rows).map(row =>
                            Array.from(row.querySelectorAll('td')).map(c => c.innerText.trim())
                        );
                    }
                """)

                page_payments = []
                for row in rows:
                    if len(row) >= 5:
                        page_payments.append({
                            "date": parse_govspend_date(row[0]),
                            "mda": row[1].strip(),
                            "beneficiary": row[2].strip(),
                            "amount": parse_naira(row[3]),
                            "description": row[4].strip(),
                            "payment_ref": row[5].strip() if len(row) > 5 else "",
                            "payer_code": row[6].strip() if len(row) > 6 else "",
                            "source": "govspend",
                            "scraped_at": datetime.utcnow().isoformat(),
                        })

                all_payments.extend(page_payments)
                logger.info(f"Page {page_num}: {len(page_payments)} payments")

                if len(page_payments) < 10:  # No more data
                    break

            browser.close()

        return all_payments


def scrape_govspend(max_pages: int = 1) -> list[dict]:
    """Convenience: scrape GovSpend payments."""
    scraper = GovSpendScraperPlaywright()
    return scraper.scrape_all(max_pages=max_pages)
