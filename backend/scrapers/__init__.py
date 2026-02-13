from .generic_scraper import GenericScraper
from .ssc_scraper import SSCScraper
from .state_psc_scraper import StatePSCScraper
from .university_scraper import UniversityScraper
from .upsc_scraper import UPSCScraper


def get_scraper(url, scraper_type=None, config=None):
    """
    Auto-detect which scraper to use based on URL.
    """
    normalized = (url or "").lower()
    config = config or {}

    if "upsc.gov.in" in normalized:
        return UPSCScraper(url=url, config=config)
    if "ssc.gov.in" in normalized:
        return SSCScraper(url=url, config=config)
    if any(k in normalized for k in ["mppsc", "uppsc", "bpsc", "rpsc", "gpsc", "psc"]):
        return StatePSCScraper(url=url, config=config)
    if ".ac.in" in normalized or ".edu" in normalized:
        return UniversityScraper(url=url, config=config)

    # `scraper_type` can still guide future extensions, but fallback is generic now.
    _ = scraper_type
    return GenericScraper(url=url, config=config)


__all__ = [
    "UPSCScraper",
    "SSCScraper",
    "UniversityScraper",
    "StatePSCScraper",
    "GenericScraper",
    "get_scraper",
]
