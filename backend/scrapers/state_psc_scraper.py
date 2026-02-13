from __future__ import annotations

from datetime import date, datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper


class StatePSCScraper(BaseScraper):
    """Configurable scraper template for State PSC portals (MPPSC/UPPSC/BPSC/RPSC/GPSC)."""

    DEFAULT_SELECTORS = [
        ".notice a[href]",
        ".notification a[href]",
        ".latest-news a[href]",
        "a[href*='advertisement']",
        "a[href*='notification']",
        "a[href*='pdf']",
    ]

    def __init__(self, url: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(url, config=config)
        self.organization = self.config.get("organization_name", "State PSC")
        self.selectors = self.config.get("selectors", self.DEFAULT_SELECTORS)
        self._seen_keys: set[str] = set()

    def parse_notification(self, html_element: Tag) -> dict[str, Any]:
        link = html_element.find("a", href=True) if html_element.name != "a" else html_element
        href = urljoin(self.url, link["href"]) if link else None
        title = self.clean_text(link.get_text(" ", strip=True)) if link else ""
        context = self.clean_text(html_element.get_text(" ", strip=True))

        parsed_date = None
        for value in html_element.stripped_strings:
            parsed_date = self.parse_date(value)
            if parsed_date:
                break

        details = self.extract_job_details(context)
        return {
            "source_url": self.url,
            "job_title": title or details["job_title"] or "Not specified",
            "organization": self.organization,
            "notification_date": parsed_date.isoformat() if parsed_date else None,
            "last_date_to_apply": details["last_date_to_apply"],
            "age_limit": details["age_limit"] or "Not specified",
            "qualification_required": details["qualification_required"] or "Not specified",
            "exam_category": "State PSC",
            "full_details": context or "Not specified",
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

        last_date = last_scraped_time.date() if isinstance(last_scraped_time, datetime) else last_scraped_time
        notif_date_str = item.get("notification_date")
        if notif_date_str:
            try:
                return datetime.fromisoformat(notif_date_str).date() >= last_date
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

        anchors: list[Tag] = []
        for selector in self.selectors:
            anchors.extend([tag for tag in soup.select(selector) if isinstance(tag, Tag)])
        if not anchors:
            anchors = [a for a in soup.select("a[href]") if isinstance(a, Tag)]

        data: list[dict[str, Any]] = []
        for anchor in anchors:
            item = self.parse_notification(anchor)

            title_lc = item["job_title"].lower()
            if not any(k in title_lc for k in ["exam", "notification", "recruitment", "advertisement", "vacancy"]):
                continue

            pdf_url = item.get("pdf_url")
            if pdf_url:
                pdf_bytes = self.download_pdf(pdf_url)
                if pdf_bytes:
                    pdf_text = self.extract_text_from_pdf(pdf_bytes)
                    if not pdf_text:
                        self.logger.warning("OCR needed for scanned State PSC PDF: %s", pdf_url)
                        continue
                    extracted = self.extract_job_details(pdf_text)
                    item["full_details"] = pdf_text
                    item["age_limit"] = extracted["age_limit"] or item["age_limit"]
                    item["qualification_required"] = (
                        extracted["qualification_required"] or item["qualification_required"]
                    )
                    item["last_date_to_apply"] = (
                        extracted["last_date_to_apply"] or item["last_date_to_apply"]
                    )

            if self.check_if_new(item, last_scraped_time):
                data.append(item)

        return data


def test_state_psc_scraper() -> None:
    scraper = StatePSCScraper("https://www.mppsc.mp.gov.in/", config={"organization_name": "MPPSC"})
    data = scraper.scrape()
    print(f"State PSC notifications fetched: {len(data)}")
    if data:
        print(data[0])


if __name__ == "__main__":
    test_state_psc_scraper()
