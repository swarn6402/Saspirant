from __future__ import annotations

from datetime import date, datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper


class UPSCScraper(BaseScraper):
    """Scraper for UPSC active examinations and recruitment notifications."""

    DEFAULT_URL = "https://upsc.gov.in/examinations/active"

    def __init__(self, url: str | None = None, config: dict[str, Any] | None = None) -> None:
        super().__init__(url or self.DEFAULT_URL, config=config)
        self._seen_keys: set[str] = set()

    def parse_notification(self, html_element: Tag) -> dict[str, Any]:
        text = self.clean_text(html_element.get_text(" ", strip=True))
        link = html_element.find("a", href=True)
        href = urljoin(self.url, link["href"]) if link else None

        parsed_date = None
        for candidate in html_element.stripped_strings:
            parsed_date = self.parse_date(candidate)
            if parsed_date:
                break

        details = self.extract_job_details(text)
        return {
            "source_url": self.url,
            "job_title": link.get_text(strip=True) if link else (details["job_title"] or "Not specified"),
            "organization": "UPSC",
            "notification_date": parsed_date.isoformat() if parsed_date else None,
            "last_date_to_apply": details["last_date_to_apply"],
            "age_limit": details["age_limit"] or "Not specified",
            "qualification_required": details["qualification_required"] or "Not specified",
            "exam_category": "UPSC",
            "full_details": text or "Not specified",
            "pdf_url": href if href and href.lower().endswith(".pdf") else None,
        }

    def check_if_new(
        self, item: dict[str, Any], last_scraped_time: datetime | date | str | None
    ) -> bool:
        key = item.get("pdf_url") or f"{item.get('job_title','')}::{item.get('notification_date','')}"
        if key in self._seen_keys:
            return False
        self._seen_keys.add(key)

        if not last_scraped_time:
            return True

        if isinstance(last_scraped_time, str):
            try:
                last_scraped_time = datetime.fromisoformat(last_scraped_time)
            except ValueError:
                return True
        if isinstance(last_scraped_time, datetime):
            last_date = last_scraped_time.date()
        else:
            last_date = last_scraped_time

        notif_date_str = item.get("notification_date")
        if notif_date_str:
            try:
                notif_date = datetime.fromisoformat(notif_date_str).date()
                return notif_date >= last_date
            except ValueError:
                return True
        return True

    def scrape(self, last_scraped_time: datetime | date | str | None = None) -> list[dict[str, Any]]:
        soup = self.fetch_page(self.url)
        if not soup:
            page_source = self.fetch_with_selenium(self.url)
            if not page_source:
                return []
            soup = BeautifulSoup(page_source, "lxml")

        rows = soup.select("table tr")
        if not rows:
            rows = [row for row in soup.select("tr") if row.find("a", href=True)]

        results: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, Tag):
                continue
            item = self.parse_notification(row)
            if not item.get("job_title"):
                continue

            pdf_url = item.get("pdf_url")
            if pdf_url:
                pdf_bytes = self.download_pdf(pdf_url)
                if pdf_bytes:
                    pdf_text = self.extract_text_from_pdf(pdf_bytes)
                    if not pdf_text:
                        self.logger.warning("OCR needed for scanned UPSC PDF: %s", pdf_url)
                        continue
                    pdf_details = self.extract_job_details(pdf_text)
                    item["full_details"] = pdf_text
                    item["age_limit"] = pdf_details["age_limit"] or item["age_limit"]
                    item["qualification_required"] = (
                        pdf_details["qualification_required"] or item["qualification_required"]
                    )
                    item["last_date_to_apply"] = (
                        pdf_details["last_date_to_apply"] or item["last_date_to_apply"]
                    )

            for field in ["job_title", "age_limit", "qualification_required", "full_details"]:
                if not item.get(field):
                    item[field] = "Not specified"

            if self.check_if_new(item, last_scraped_time):
                results.append(item)

        return results


def test_upsc_scraper() -> None:
    scraper = UPSCScraper()
    data = scraper.scrape()
    print(f"UPSC notifications fetched: {len(data)}")
    if data:
        print(data[0])


if __name__ == "__main__":
    test_upsc_scraper()

