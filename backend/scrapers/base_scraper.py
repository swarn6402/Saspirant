from __future__ import annotations

import io
import logging
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import pdfplumber
import requests
from bs4 import BeautifulSoup, Tag
from requests import Response
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class BaseScraper(ABC):
    """Reusable base class for scraping exam/job notifications."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    def __init__(self, url: str, config: dict[str, Any] | None = None) -> None:
        """
        Initialize the scraper with URL and optional config.

        Args:
            url: Primary source URL for the scraper.
            config: Optional scraper configuration overrides.
        """
        self.url = url
        self.config = config or {}
        self.timeout = int(self.config.get("timeout", 20))
        self.max_retries = int(self.config.get("max_retries", 3))
        self.retry_delay_seconds = int(self.config.get("retry_delay_seconds", 2))
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_page(self, url: str) -> BeautifulSoup | None:
        """
        Fetch an HTML page and return a BeautifulSoup object.

        Args:
            url: URL to request.

        Returns:
            BeautifulSoup object when successful, otherwise None.
        """
        response = self._request_with_retry(url)
        if not response:
            return None
        return BeautifulSoup(response.text, "lxml")

    def fetch_with_selenium(self, url: str) -> str | None:
        """
        Fetch dynamic content using headless Chrome and return page source.

        Args:
            url: URL to load in browser.

        Returns:
            Page source HTML string when successful, otherwise None.
        """
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={self.DEFAULT_HEADERS['User-Agent']}")

        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(self.timeout)
            driver.get(url)
            WebDriverWait(driver, self.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return driver.page_source
        except (WebDriverException, TimeoutException) as exc:
            self.logger.error("Selenium fetch failed for %s: %s", url, exc)
            return None
        finally:
            if driver is not None:
                driver.quit()

    def download_pdf(self, pdf_url: str) -> bytes | None:
        """
        Download PDF bytes from a URL.

        Args:
            pdf_url: Direct or redirected PDF URL.

        Returns:
            PDF bytes when successful, otherwise None.
        """
        response = self._request_with_retry(pdf_url, stream=True)
        if not response:
            return None
        return response.content

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes with pdfplumber.

        Args:
            pdf_bytes: Raw PDF bytes.

        Returns:
            Cleaned text extracted from all pages, or empty string on failure.
        """
        if not pdf_bytes:
            return ""

        try:
            text_parts: list[str] = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    if page_text:
                        text_parts.append(page_text)
            return self.clean_text("\n".join(text_parts))
        except Exception as exc:
            self.logger.error("PDF text extraction failed: %s", exc)
            return ""

    @abstractmethod
    def parse_notification(self, html_element: Tag) -> dict[str, Any]:
        """
        Parse one notification HTML element into a structured dictionary.

        Must be implemented by child scrapers.
        """
        raise NotImplementedError

    def extract_job_details(self, text: str) -> dict[str, Any]:
        """
        Extract job attributes using regex and keyword-based parsing.

        Args:
            text: Raw notification text.

        Returns:
            Dictionary with common extracted fields.
        """
        cleaned = self.clean_text(text)
        lower = cleaned.lower()

        title_match = re.search(
            r"(recruitment|notification|advertisement)\s*(for)?\s*([A-Za-z0-9 /-]{5,120})",
            cleaned,
            flags=re.IGNORECASE,
        )
        post_count_match = re.search(
            r"(vacanc(?:y|ies)|posts?)\s*[:\-]?\s*(\d{1,6})",
            cleaned,
            flags=re.IGNORECASE,
        )
        date_match = re.search(
            r"(last\s+date(?:\s+to\s+apply)?|apply\s+before)\s*[:\-]?\s*([^\n,;]+)",
            cleaned,
            flags=re.IGNORECASE,
        )

        qualification = ""
        qualification_pattern = re.search(
            r"(qualification|eligible|eligibility)\s*[:\-]?\s*([^\n]{5,200})",
            cleaned,
            flags=re.IGNORECASE,
        )
        if qualification_pattern:
            qualification = self.clean_text(qualification_pattern.group(2))
        elif any(k in lower for k in ["graduate", "12th", "10th", "diploma", "degree"]):
            qualification = "Mentioned in notification"

        parsed_last_date = None
        if date_match:
            parsed_last_date = self.parse_date(date_match.group(2))

        return {
            "job_title": self.clean_text(title_match.group(3)) if title_match else "",
            "age_limit": self.extract_age_limit(cleaned),
            "qualification_required": qualification,
            "last_date_to_apply": parsed_last_date.isoformat() if parsed_last_date else None,
            "vacancy_count": int(post_count_match.group(2)) if post_count_match else None,
        }

    def clean_text(self, text: str) -> str:
        """
        Normalize whitespace and line breaks from text.

        Args:
            text: Input text.

        Returns:
            Cleaned text.
        """
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def parse_date(self, date_string: str) -> datetime.date | None:
        """
        Parse date strings in multiple common formats.

        Supported examples:
            - 15/02/2025
            - 15-02-2025
            - 15-Feb-2025
            - 15 February 2025
            - 2025-02-15
        """
        if not date_string:
            return None

        candidate = self.clean_text(date_string)
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d-%b-%Y",
            "%d-%B-%Y",
            "%d %b %Y",
            "%d %B %Y",
            "%Y-%m-%d",
        ]

        for date_format in formats:
            try:
                return datetime.strptime(candidate, date_format).date()
            except ValueError:
                continue

        embedded = re.search(
            r"(\d{1,2}[/-][A-Za-z0-9]{1,3}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})",
            candidate,
        )
        if embedded:
            return self.parse_date(embedded.group(1))
        return None

    def extract_age_limit(self, text: str) -> str:
        """
        Extract age-limit phrases from notification text.

        Examples:
            - 21-35 years
            - Below 30 years
            - Maximum 27 years
        """
        if not text:
            return ""

        patterns = [
            r"\b(\d{1,2}\s*[-to]+\s*\d{1,2}\s*years?)\b",
            r"\b(below\s*\d{1,2}\s*years?)\b",
            r"\b(upper\s*age\s*limit\s*[:\-]?\s*\d{1,2}\s*years?)\b",
            r"\b(max(?:imum)?\s*\d{1,2}\s*years?)\b",
            r"\b(min(?:imum)?\s*\d{1,2}\s*years?)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return self.clean_text(match.group(1))
        return ""

    def safe_parse_notifications(self, elements: list[Tag]) -> list[dict[str, Any]]:
        """
        Parse notification elements safely.

        Returns an empty list on total failure and skips invalid items instead
        of raising unhandled exceptions.
        """
        if not elements:
            return []

        parsed: list[dict[str, Any]] = []
        for element in elements:
            try:
                data = self.parse_notification(element)
                if data:
                    parsed.append(data)
            except Exception as exc:
                self.logger.warning("Failed to parse one notification element: %s", exc)
        return parsed

    def _request_with_retry(
        self, url: str, stream: bool = False, method: str = "GET"
    ) -> Response | None:
        """
        Make an HTTP request with retry logic for transient failures.

        Args:
            url: URL to request.
            stream: Whether response should be streamed.
            method: HTTP method, defaults to GET.

        Returns:
            `requests.Response` when successful, otherwise None.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.DEFAULT_HEADERS,
                    timeout=self.timeout,
                    allow_redirects=True,
                    stream=stream,
                )
                response.raise_for_status()
                return response
            except RequestException as exc:
                self.logger.warning(
                    "Request attempt %s/%s failed for %s: %s",
                    attempt,
                    self.max_retries,
                    url,
                    exc,
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay_seconds)
                else:
                    self.logger.error("All retries exhausted for %s", url)
        return None

