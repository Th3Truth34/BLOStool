"""
Permit Database Scraper

Scrapes city/county building permit databases for multifamily construction projects.
This is a configurable scraper that works with common permit portal formats.

In production, you would configure specific city URLs. This demo scraper
includes patterns for common permit portal systems (Accela, TRAKiT, etc.)
and a demo mode that generates sample data for testing.
"""
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.services.scraping.base import BaseScraper, ScrapedItem


class PermitScraper(BaseScraper):
    source_type = "permit"
    source_name = "Building Permit Database"

    def __init__(self, city_configs: Optional[list[dict]] = None):
        self.city_configs = city_configs or []

    async def scrape(self) -> list[ScrapedItem]:
        items = []
        if not self.city_configs:
            # Demo mode: return sample permit data for testing
            items = self._generate_demo_data()
        else:
            for config in self.city_configs:
                try:
                    city_items = await self._scrape_city(config)
                    items.extend(city_items)
                except Exception as e:
                    print(f"Error scraping {config.get('name', 'unknown')}: {e}")
        return items

    async def _scrape_city(self, config: dict) -> list[ScrapedItem]:
        """Scrape a specific city's permit portal."""
        items = []
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            try:
                response = await client.get(config["url"])
                response.raise_for_status()
            except httpx.HTTPError:
                return items

            soup = BeautifulSoup(response.text, "html.parser")

            # Generic table-based permit portal parsing
            rows = soup.select("table tr, .permit-row, .result-row")
            for row in rows:
                text = row.get_text(strip=True)
                if not self.is_multifamily(text):
                    continue

                title = self._extract_title(row, text)
                unit_count = self.extract_unit_count(text)
                if unit_count and unit_count < 20:
                    continue  # Skip small projects

                link = row.find("a")
                url = link["href"] if link and link.get("href") else config["url"]
                if url.startswith("/"):
                    url = config["url"].split("/")[0] + "//" + config["url"].split("/")[2] + url

                items.append(ScrapedItem(
                    title=title,
                    source_url=url,
                    description=text[:500],
                    location=config.get("city", ""),
                    unit_count=unit_count,
                    raw_data={"city": config.get("city"), "text": text[:1000]},
                    confidence_score=0.7 if unit_count else 0.4,
                ))
        return items

    def _extract_title(self, row, text: str) -> str:
        """Try to extract a meaningful title from a permit row."""
        # Look for common title elements
        for selector in ["td:first-child", ".project-name", ".description", "a"]:
            el = row.select_one(selector)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)[:200]
        return text[:100]

    def _generate_demo_data(self) -> list[ScrapedItem]:
        """Generate realistic demo permit data for testing."""
        demo_permits = [
            {
                "title": "New 250-Unit Apartment Complex - Riverside Development",
                "location": "Austin, TX",
                "units": 250,
                "description": "New construction of a 250-unit multifamily residential complex with ground-floor retail. 5 stories, structured parking. Permit #BP-2026-04521.",
                "url": "https://example.com/permits/austin/BP-2026-04521",
            },
            {
                "title": "Mixed-Use Tower - 180 Residential Units + Commercial",
                "location": "Denver, CO",
                "units": 180,
                "description": "12-story mixed-use development with 180 apartment units, 15,000 sqft ground-floor commercial space, and underground parking. Permit #2026-BLD-0892.",
                "url": "https://example.com/permits/denver/2026-BLD-0892",
            },
            {
                "title": "Greenfield Senior Living Community - 120 Units",
                "location": "Phoenix, AZ",
                "units": 120,
                "description": "New senior living community featuring 120 independent and assisted living units across 3 buildings. Amenities include dining hall, fitness center, and medical offices.",
                "url": "https://example.com/permits/phoenix/SL-2026-0334",
            },
            {
                "title": "Student Housing Development Near University Campus",
                "location": "Raleigh, NC",
                "units": 300,
                "description": "300-bed student housing development with shared amenity spaces, study rooms, and retail. 6 stories. Zoning: MF-2. Permit #STU-2026-1102.",
                "url": "https://example.com/permits/raleigh/STU-2026-1102",
            },
            {
                "title": "Affordable Housing Project - Westside Commons",
                "location": "Portland, OR",
                "units": 85,
                "description": "85-unit affordable housing development. Income-restricted at 60% AMI. 4 stories wood frame over concrete podium. Permit #AF-2026-0078.",
                "url": "https://example.com/permits/portland/AF-2026-0078",
            },
            {
                "title": "Luxury Waterfront Condominiums - Harbor View",
                "location": "Seattle, WA",
                "units": 150,
                "description": "150-unit luxury condominium tower on the waterfront. 22 stories, full-service amenities including rooftop pool, concierge, and marina access.",
                "url": "https://example.com/permits/seattle/LX-2026-0445",
            },
        ]

        items = []
        for p in demo_permits:
            items.append(ScrapedItem(
                title=p["title"],
                source_url=p["url"],
                description=p["description"],
                location=p["location"],
                unit_count=p["units"],
                raw_data=p,
                confidence_score=0.85,
            ))
        return items
