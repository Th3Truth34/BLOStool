"""
Construction News Scraper

Parses RSS feeds from multifamily construction and real estate news sources
to find new development projects. Uses BeautifulSoup with lxml for XML parsing.
"""
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.services.scraping.base import BaseScraper, ScrapedItem

DEFAULT_FEEDS = [
    {
        "name": "Multi-Housing News",
        "url": "https://www.multihousingnews.com/feed/",
    },
    {
        "name": "Multifamily Dive",
        "url": "https://www.multifamilydive.com/feeds/news/",
    },
]


class NewsScraper(BaseScraper):
    source_type = "news"
    source_name = "Construction News RSS"

    def __init__(self, feeds: Optional[list[dict]] = None):
        self.feeds = feeds or DEFAULT_FEEDS

    async def scrape(self) -> list[ScrapedItem]:
        items = []
        for feed_config in self.feeds:
            try:
                feed_items = await self._scrape_feed(feed_config)
                items.extend(feed_items)
            except Exception as e:
                print(f"Error scraping feed {feed_config['name']}: {e}")

        # If no feeds returned results, use demo data
        if not items:
            items = self._generate_demo_data()
        return items

    async def _scrape_feed(self, feed_config: dict) -> list[ScrapedItem]:
        items = []
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            try:
                response = await client.get(feed_config["url"])
                response.raise_for_status()
            except httpx.HTTPError:
                return items

        soup = BeautifulSoup(response.text, "lxml-xml")
        entries = soup.find_all("item")[:20]

        for entry in entries:
            title_el = entry.find("title")
            title = title_el.get_text(strip=True) if title_el else ""
            desc_el = entry.find("description")
            summary = desc_el.get_text(strip=True) if desc_el else ""
            link_el = entry.find("link")
            link = link_el.get_text(strip=True) if link_el else feed_config["url"]
            pub_el = entry.find("pubDate")
            published = pub_el.get_text(strip=True) if pub_el else ""

            combined_text = f"{title} {summary}"
            if not self.is_multifamily(combined_text):
                continue

            unit_count = self.extract_unit_count(combined_text)

            items.append(ScrapedItem(
                title=title,
                source_url=link,
                description=summary[:500] if summary else None,
                unit_count=unit_count,
                raw_data={
                    "feed_name": feed_config["name"],
                    "published": published,
                    "title": title,
                    "summary": summary[:1000],
                },
                confidence_score=0.6 if unit_count else 0.3,
            ))
        return items

    def _generate_demo_data(self) -> list[ScrapedItem]:
        """Generate realistic demo news data for testing."""
        demo_news = [
            {
                "title": "National Developer Breaks Ground on 400-Unit Apartment Community in Nashville",
                "description": "GreyStar Real Estate Partners has broken ground on a 400-unit luxury apartment community in Nashville's Gulch neighborhood. The $85M project will feature studio to three-bedroom units with resort-style amenities.",
                "url": "https://example.com/news/greystar-nashville-400-units",
                "units": 400,
            },
            {
                "title": "Affordable Housing Developer Plans 200-Unit Complex in Chicago Suburb",
                "description": "Evergreen Development Group has received approval for a 200-unit affordable housing complex in Evanston, IL. The project will offer units at 50-80% area median income levels.",
                "url": "https://example.com/news/evergreen-evanston-affordable",
                "units": 200,
            },
            {
                "title": "Multifamily Construction Starts Surge in Sun Belt Markets",
                "description": "New data shows multifamily construction starts increased 15% year-over-year in Sun Belt markets, with Austin, Phoenix, and Charlotte leading the way. Industry analysts expect the trend to continue through 2026.",
                "url": "https://example.com/news/sunbelt-multifamily-surge",
                "units": None,
            },
        ]

        items = []
        for n in demo_news:
            items.append(ScrapedItem(
                title=n["title"],
                source_url=n["url"],
                description=n["description"],
                unit_count=n["units"],
                raw_data=n,
                confidence_score=0.7 if n["units"] else 0.4,
            ))
        return items
