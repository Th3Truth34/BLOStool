from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.activity import Activity
from app.models.lead import Lead
from app.schemas.activity import ActivityCreate, ActivityResponse

router = APIRouter(prefix="/leads/{lead_id}/activities", tags=["activities"])


@router.get("", response_model=list[ActivityResponse])
async def list_activities(
    lead_id: str,
    activity_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Activity).where(Activity.lead_id == lead_id)
    if activity_type:
        query = query.where(Activity.activity_type == activity_type)
    query = query.order_by(Activity.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ActivityResponse)
async def create_activity(lead_id: str, activity_data: ActivityCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Lead not found")

    activity = Activity(lead_id=lead_id, **activity_data.model_dump())
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity
