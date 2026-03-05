from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.lead import Lead
from app.models.activity import Activity
from app.models.scraped_data import ScrapedData
from app.schemas.activity import ActivityResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    total_leads: int
    active_leads: int
    won_leads: int
    lost_leads: int
    total_units: int
    pipeline_counts: dict[str, int]
    recent_activities: list[ActivityResponse]
    unmatched_scraped: int


@router.get("", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    # Total leads
    result = await db.execute(select(func.count(Lead.id)))
    total_leads = result.scalar() or 0

    # Pipeline counts
    result = await db.execute(
        select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    )
    pipeline_counts = {row[0]: row[1] for row in result.all()}

    # Active leads (not won/lost)
    active_leads = sum(v for k, v in pipeline_counts.items() if k not in ("won", "lost"))
    won_leads = pipeline_counts.get("won", 0)
    lost_leads = pipeline_counts.get("lost", 0)

    # Total units across all active leads
    result = await db.execute(
        select(func.coalesce(func.sum(Lead.unit_count), 0)).where(
            Lead.status.notin_(["won", "lost"])
        )
    )
    total_units = result.scalar() or 0

    # Recent activities
    result = await db.execute(
        select(Activity).order_by(Activity.created_at.desc()).limit(10)
    )
    recent_activities = result.scalars().all()

    # Unmatched scraped data
    result = await db.execute(
        select(func.count(ScrapedData.id)).where(
            ScrapedData.is_matched == False,
            ScrapedData.is_dismissed == False,
        )
    )
    unmatched_scraped = result.scalar() or 0

    return DashboardStats(
        total_leads=total_leads,
        active_leads=active_leads,
        won_leads=won_leads,
        lost_leads=lost_leads,
        total_units=total_units,
        pipeline_counts=pipeline_counts,
        recent_activities=recent_activities,
        unmatched_scraped=unmatched_scraped,
    )
