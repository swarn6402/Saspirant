from __future__ import annotations

from datetime import date, datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper


class GenericScraper(BaseScraper):
    """Fallback scraper for unknown websites using generic link/pattern discovery."""

    def __init__(self, url: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(url, config=config)
        self.organization = self.config.get("organization_name", "Unknown Organization")
        self.category = self.config.get("exam_category", "General")
        self._seen_keys: set[str] = set()

    def parse_notification(self, html_element: Tag) -> dict[str, Any]:
        link = html_element.find("a", href=True) if html_element.name != "a" else html_element
        href = urljoin(self.url, link["href"]) if link else None
        title = self.clean_text(link.get_text(" ", strip=True)) if link else ""
        content = self.clean_text(html_element.get_text(" ", strip=True))
        details = self.extract_job_details(content)

        parsed_date = None
        for chunk in html_element.stripped_strings:
            parsed_date = self.parse_date(chunk)
            if parsed_date:
                break

        return {
            "source_url": self.url,
            "job_title": title or details["job_title"] or "Not specified",
            "organization": self.organization,
            "notification_date": parsed_date.isoformat() if parsed_date else None,
            "last_date_to_apply": details["last_date_to_apply"],
            "age_limit": details["age_limit"] or "Not specified",
            "qualification_required": details["qualification_required"] or "Not specified",
            "exam_category": self.category,
            "full_details": content or "Not specified",
            "pdf_url": href if href and ".pdf" in href.lower() else None,
        }

    def check_if_new(
        self, item: dict[str, Any], last_scraped_time: datetime | date | str | None
    ) -> bool:
        key = item.get("pdf_url") or f"{item.get('job_title')}::{item.get('notification_date')}"
        if key in self._seen_keys:
            return False
        self._seen_keys.add(key)
        return True

    def scrape(self, last_scraped_time: datetime | date | str | None = None) -> list[dict[str, Any]]:
        soup = self.fetch_page(self.url)
        if not soup:
            page_source = self.fetch_with_selenium(self.url)
            if not page_source:
                return []
            soup = BeautifulSoup(page_source, "lxml")

        anchors = [a for a in soup.select("a[href]") if isinstance(a, Tag)]
        out: list[dict[str, Any]] = []
        for anchor in anchors:
            title = self.clean_text(anchor.get_text(" ", strip=True)).lower()
            if not any(k in title for k in ["notification", "notice", "exam", "recruitment", "vacancy", "result"]):
                continue
            item = self.parse_notification(anchor)
            if self.check_if_new(item, last_scraped_time):
                out.append(item)
        return out


def test_generic_scraper() -> None:
    scraper = GenericScraper("https://example.com")
    data = scraper.scrape()
    print(f"Generic scraper notifications fetched: {len(data)}")
    if data:
        print(data[0])


if __name__ == "__main__":
    test_generic_scraper()
