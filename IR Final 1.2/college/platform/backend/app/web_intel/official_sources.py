"""
Layer 7: Web Intelligence — official sources only.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

OFFICIAL_SOURCES = {
    "kea": {
        "name": "Karnataka Examinations Authority",
        "url": "https://cetonline.karnataka.gov.in",
        "domains": ["kea.kar.nic.in", "cetonline.karnataka.gov.in"],
    },
    "vtu": {
        "name": "Visvesvaraya Technological University",
        "url": "https://vtu.ac.in",
        "domains": ["vtu.ac.in"],
    },
    "aicte": {
        "name": "AICTE",
        "url": "https://www.aicte-india.org",
        "domains": ["aicte-india.org"],
    },
    "ugc": {
        "name": "UGC",
        "url": "https://www.ugc.ac.in",
        "domains": ["ugc.ac.in"],
    },
    "scholarships": {
        "name": "National Scholarship Portal",
        "url": "https://scholarships.gov.in",
        "domains": ["scholarships.gov.in", "nsp.gov.in"],
    },
}


class WebIntelligenceLayer:
    """Fetch missing data from official sources only."""

    REJECTED_DOMAINS = {"quora.com", "reddit.com", "medium.com", "blogspot.com", "wordpress.com"}

    def is_official_source(self, url: str) -> bool:
        try:
            domain = urlparse(url).netloc.lower().replace("www.", "")
            if any(d in domain for d in self.REJECTED_DOMAINS):
                return False
            return any(
                domain.endswith(d) or d in domain
                for src in OFFICIAL_SOURCES.values()
                for d in src["domains"]
            ) or any(domain.endswith(d) for d in settings.OFFICIAL_DOMAINS)
        except Exception:
            return False

    def get_official_links(self, topic: str) -> List[Dict[str, str]]:
        topic_lower = topic.lower()
        links = []
        if any(k in topic_lower for k in ("cutoff", "counselling", "counseling", "kea", "kcet")):
            links.append({"source": "KEA", "url": OFFICIAL_SOURCES["kea"]["url"], "topic": "counselling"})
        if "scholarship" in topic_lower:
            links.append({"source": "NSP", "url": OFFICIAL_SOURCES["scholarships"]["url"], "topic": "scholarships"})
        if "vtu" in topic_lower or "affiliation" in topic_lower:
            links.append({"source": "VTU", "url": OFFICIAL_SOURCES["vtu"]["url"], "topic": "affiliation"})
        return links

    def enrich_missing_data(
        self,
        college_name: str,
        missing_fields: List[str],
    ) -> Dict[str, Any]:
        """Return official source URLs for missing data — no web scraping in v1."""
        return {
            "college": college_name,
            "missing_fields": missing_fields,
            "official_sources": self.get_official_links(" ".join(missing_fields)),
            "note": "Refer to official portals for the latest verified data.",
        }
