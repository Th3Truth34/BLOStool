"""
Scraping scheduler — runs all configured scrapers.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.scraping.permit_scraper import PermitScraper
from app.services.scraping.news_scraper import NewsScraper


async def run_all_scrapers(db: AsyncSession) -> int:
    """Run all scrapers and return total number of new results."""
    total = 0

    scrapers = [
        PermitScraper(),
        NewsScraper(),
    ]

    for scraper in scrapers:
        try:
            results = await scraper.run(db)
            total += len(results)
            print(f"[Scraper] {scraper.source_name}: {len(results)} new results")
        except Exception as e:
            print(f"[Scraper] {scraper.source_name} failed: {e}")

    return total
