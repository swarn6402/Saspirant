from __future__ import annotations

from datetime import date, datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper


class UniversityScraper(BaseScraper):
    """Generic scraper for Indian university notice/notification pages."""

    DEFAULT_SELECTORS = [
        ".notification-list a[href]",
        ".notice-board a[href]",
        "#notifications a[href]",
        "a[href*='pdf']",
        "a[href*='notification']",
        "a[href*='notice']",
        "a[href*='announcement']",
    ]
    RELEVANT_KEYWORDS = {"admission", "exam", "result", "schedule", "declaration", "notice"}
    IRRELEVANT_KEYWORDS = {"holiday", "staff recruitment", "tender", "quotation", "auction"}

    def __init__(self, url: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(url, config=config)
        self.organization = self.config.get("organization_name", "University")
        self.selectors = self.config.get("selectors", self.DEFAULT_SELECTORS)
        self._seen_keys: set[str] = set()

    def parse_notification(self, html_element: Tag) -> dict[str, Any]:
        link = html_element.find("a", href=True) if html_element.name != "a" else html_element
        href = urljoin(self.url, link["href"]) if link else None
        title = self.clean_text(link.get_text(" ", strip=True)) if link else ""
        context_text = self.clean_text(html_element.get_text(" ", strip=True))
        merged_text = self.clean_text(f"{title} {context_text}")

        parsed_date = None
        for chunk in html_element.stripped_strings:
            parsed_date = self.parse_date(chunk)
            if parsed_date:
                break

        return {
            "source_url": self.url,
            "job_title": title or "Not specified",
            "organization": self.organization,
            "notification_date": parsed_date.isoformat() if parsed_date else None,
            "last_date_to_apply": None,
            "age_limit": "Not specified",
            "qualification_required": "Not specified",
            "exam_category": "University",
            "full_details": merged_text or "Not specified",
            "pdf_url": href if href and ".pdf" in href.lower() else None,
        }

    def check_if_new(
        self, item: dict[str, Any], last_scraped_time: datetime | date | str | None
    ) -> bool:
        key = item.get("pdf_url") or f"{item.get('job_title')}::{item.get('notification_date')}"
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
                return datetime.fromisoformat(notif_date_str).date() >= last_date
            except ValueError:
                return True
        return True

    def _is_relevant(self, title: str, details: str) -> bool:
        haystack = f"{title} {details}".lower()
        if any(k in haystack for k in self.IRRELEVANT_KEYWORDS):
            return False
        return any(k in haystack for k in self.RELEVANT_KEYWORDS)

    def _collect_candidates(self, soup: BeautifulSoup) -> list[Tag]:
        candidates: list[Tag] = []
        for selector in self.selectors:
            candidates.extend([a for a in soup.select(selector) if isinstance(a, Tag)])
        if not candidates:
            candidates = [a for a in soup.select("a[href]") if isinstance(a, Tag)]
        return candidates

    def scrape(self, last_scraped_time: datetime | date | str | None = None) -> list[dict[str, Any]]:
        soup = self.fetch_page(self.url)
        if not soup:
            page_source = self.fetch_with_selenium(self.url)
            if not page_source:
                return []
            soup = BeautifulSoup(page_source, "lxml")

        candidates = self._collect_candidates(soup)
        output: list[dict[str, Any]] = []

        for item_tag in candidates:
            item = self.parse_notification(item_tag)
            if not self._is_relevant(item["job_title"], item["full_details"]):
                continue

            pdf_url = item.get("pdf_url")
            if pdf_url:
                pdf_bytes = self.download_pdf(pdf_url)
                if pdf_bytes:
                    pdf_text = self.extract_text_from_pdf(pdf_bytes)
                    if not pdf_text:
                        self.logger.warning("OCR needed for scanned university PDF: %s", pdf_url)
                        continue
                    details = self.extract_job_details(pdf_text)
                    item["full_details"] = pdf_text
                    item["last_date_to_apply"] = details["last_date_to_apply"]
                    item["age_limit"] = details["age_limit"] or "Not specified"
                    item["qualification_required"] = (
                        details["qualification_required"] or "Not specified"
                    )

                    content_lower = pdf_text.lower()
                    if not self._is_relevant(item["job_title"], content_lower):
                        continue

            if self.check_if_new(item, last_scraped_time):
                output.append(item)

        return output


def test_university_scraper() -> None:
    demo_url = "https://du.ac.in/index.php?page=notices"
    scraper = UniversityScraper(demo_url, config={"organization_name": "University"})
    data = scraper.scrape()
    print(f"University notifications fetched: {len(data)}")
    if data:
        print(data[0])


if __name__ == "__main__":
    test_university_scraper()
