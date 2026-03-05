from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scraped_data import ScrapedData


@dataclass
class ScrapedItem:
    title: str
    source_url: str
    description: Optional[str] = None
    location: Optional[str] = None
    unit_count: Optional[int] = None
    raw_data: Optional[dict] = None
    confidence_score: float = 0.5


MULTIFAMILY_KEYWORDS = [
    "apartment", "multifamily", "multi-family", "residential units",
    "dwelling units", "mixed-use", "mixed use", "townhome", "condo",
    "senior living", "student housing", "affordable housing",
]

ZONING_CODES = ["R-3", "R-4", "R-5", "RM", "MF", "MU", "PUD"]


class BaseScraper(ABC):
    source_type: str
    source_name: str

    @abstractmethod
    async def scrape(self) -> list[ScrapedItem]:
        ...

    def is_multifamily(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in MULTIFAMILY_KEYWORDS)

    def extract_unit_count(self, text: str) -> Optional[int]:
        import re
        patterns = [
            r"(\d+)\s*(?:unit|apt|apartment|dwelling)",
            r"(\d+)\s*-\s*unit",
            r"(\d+)\s*units",
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                count = int(match.group(1))
                if count >= 5:
                    return count
        return None

    async def run(self, db: AsyncSession) -> list[ScrapedData]:
        items = await self.scrape()
        results = []
        for item in items:
            # Deduplicate by source_url
            existing = await db.execute(
                select(ScrapedData).where(ScrapedData.source_url == item.source_url)
            )
            if existing.scalar_one_or_none():
                continue

            scraped = ScrapedData(
                source_type=self.source_type,
                source_url=item.source_url,
                source_name=self.source_name,
                title=item.title,
                description=item.description,
                location=item.location,
                unit_count=item.unit_count,
                raw_data=item.raw_data,
                confidence_score=item.confidence_score,
            )
            db.add(scraped)
            results.append(scraped)

        if results:
            await db.commit()
        return results
