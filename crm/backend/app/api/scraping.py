from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.scraped_data import ScrapedData
from app.models.lead import Lead

router = APIRouter(prefix="/scraping", tags=["scraping"])


class ScrapedDataResponse(BaseModel):
    id: str
    lead_id: Optional[str] = None
    source_type: str
    source_url: str
    source_name: str
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    unit_count: Optional[int] = None
    scraped_at: str
    is_matched: bool
    is_dismissed: bool
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True


class LinkToLeadRequest(BaseModel):
    lead_id: str


class TriggerScrapeResponse(BaseModel):
    message: str
    results_count: int


@router.get("", response_model=list[ScrapedDataResponse])
async def list_scraped_data(
    is_matched: Optional[bool] = Query(None),
    is_dismissed: Optional[bool] = Query(None),
    source_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(ScrapedData)
    if is_matched is not None:
        query = query.where(ScrapedData.is_matched == is_matched)
    if is_dismissed is not None:
        query = query.where(ScrapedData.is_dismissed == is_dismissed)
    if source_type:
        query = query.where(ScrapedData.source_type == source_type)
    query = query.order_by(ScrapedData.scraped_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{scraped_id}/link", response_model=ScrapedDataResponse)
async def link_to_lead(scraped_id: str, body: LinkToLeadRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScrapedData).where(ScrapedData.id == scraped_id))
    scraped = result.scalar_one_or_none()
    if not scraped:
        raise HTTPException(status_code=404, detail="Scraped data not found")

    result = await db.execute(select(Lead).where(Lead.id == body.lead_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Lead not found")

    scraped.lead_id = body.lead_id
    scraped.is_matched = True
    await db.commit()
    await db.refresh(scraped)
    return scraped


@router.post("/{scraped_id}/dismiss", response_model=ScrapedDataResponse)
async def dismiss_scraped(scraped_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScrapedData).where(ScrapedData.id == scraped_id))
    scraped = result.scalar_one_or_none()
    if not scraped:
        raise HTTPException(status_code=404, detail="Scraped data not found")

    scraped.is_dismissed = True
    await db.commit()
    await db.refresh(scraped)
    return scraped


@router.post("/{scraped_id}/create-lead", response_model=dict)
async def create_lead_from_scraped(scraped_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScrapedData).where(ScrapedData.id == scraped_id))
    scraped = result.scalar_one_or_none()
    if not scraped:
        raise HTTPException(status_code=404, detail="Scraped data not found")

    lead = Lead(
        project_name=scraped.title or "Untitled Project",
        source=f"scraped_{scraped.source_type}" if scraped.source_type in ("permit", "news", "planning") else "manual",
        city=scraped.location,
        unit_count=scraped.unit_count,
    )
    db.add(lead)
    await db.flush()

    scraped.lead_id = lead.id
    scraped.is_matched = True

    await db.commit()
    return {"lead_id": lead.id, "detail": "Lead created from scraped data"}


@router.post("/trigger", response_model=TriggerScrapeResponse)
async def trigger_scrape(db: AsyncSession = Depends(get_db)):
    from app.services.scraping.scheduler import run_all_scrapers
    count = await run_all_scrapers(db)
    return TriggerScrapeResponse(message="Scraping completed", results_count=count)
