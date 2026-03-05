from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.lead import Lead
from app.models.contact import Contact
from app.models.activity import Activity
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, PipelineResponse

router = APIRouter(prefix="/leads", tags=["leads"])


def lead_to_response(lead: Lead) -> LeadResponse:
    return LeadResponse(
        id=lead.id,
        project_name=lead.project_name,
        status=lead.status,
        source=lead.source,
        priority=lead.priority,
        unit_count=lead.unit_count,
        estimated_value=lead.estimated_value,
        project_type=lead.project_type,
        construction_phase=lead.construction_phase,
        estimated_completion=lead.estimated_completion,
        address=lead.address,
        city=lead.city,
        state=lead.state,
        zip_code=lead.zip_code,
        next_action=lead.next_action,
        next_action_date=lead.next_action_date,
        loss_reason=lead.loss_reason,
        notes=lead.notes,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        contact_count=len(lead.contacts) if lead.contacts else 0,
        activity_count=len(lead.activities) if lead.activities else 0,
    )


@router.get("", response_model=list[LeadResponse])
async def list_leads(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Lead).options(selectinload(Lead.contacts), selectinload(Lead.activities))

    if status:
        query = query.where(Lead.status == status)
    if source:
        query = query.where(Lead.source == source)
    if city:
        query = query.where(Lead.city.ilike(f"%{city}%"))
    if search:
        query = query.where(Lead.project_name.ilike(f"%{search}%"))

    query = query.order_by(Lead.updated_at.desc())
    result = await db.execute(query)
    leads = result.scalars().all()
    return [lead_to_response(lead) for lead in leads]


@router.get("/pipeline", response_model=list[PipelineResponse])
async def get_pipeline(db: AsyncSession = Depends(get_db)):
    statuses = ["new", "researching", "contacted", "meeting_scheduled", "proposal_sent", "negotiating", "won", "lost"]
    pipeline = []
    for status in statuses:
        query = (
            select(Lead)
            .options(selectinload(Lead.contacts), selectinload(Lead.activities))
            .where(Lead.status == status)
            .order_by(Lead.priority.desc(), Lead.updated_at.desc())
        )
        result = await db.execute(query)
        leads = result.scalars().all()
        pipeline.append(PipelineResponse(
            status=status,
            count=len(leads),
            leads=[lead_to_response(lead) for lead in leads],
        ))
    return pipeline


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    query = (
        select(Lead)
        .options(selectinload(Lead.contacts), selectinload(Lead.activities))
        .where(Lead.id == lead_id)
    )
    result = await db.execute(query)
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead_to_response(lead)


@router.post("", response_model=LeadResponse)
async def create_lead(lead_data: LeadCreate, db: AsyncSession = Depends(get_db)):
    lead = Lead(**lead_data.model_dump())
    db.add(lead)
    await db.commit()

    query = (
        select(Lead)
        .options(selectinload(Lead.contacts), selectinload(Lead.activities))
        .where(Lead.id == lead.id)
    )
    result = await db.execute(query)
    lead = result.scalar_one()
    return lead_to_response(lead)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: str, lead_data: LeadUpdate, db: AsyncSession = Depends(get_db)):
    query = (
        select(Lead)
        .options(selectinload(Lead.contacts), selectinload(Lead.activities))
        .where(Lead.id == lead_id)
    )
    result = await db.execute(query)
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_status = lead.status
    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow().isoformat()

    # Auto-log status change
    if "status" in update_data and update_data["status"] != old_status:
        activity = Activity(
            lead_id=lead_id,
            activity_type="status_change",
            title=f"Status changed from {old_status} to {update_data['status']}",
        )
        db.add(activity)

    await db.commit()
    await db.refresh(lead)

    query = (
        select(Lead)
        .options(selectinload(Lead.contacts), selectinload(Lead.activities))
        .where(Lead.id == lead_id)
    )
    result = await db.execute(query)
    lead = result.scalar_one()
    return lead_to_response(lead)


@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()
    return {"detail": "Lead deleted"}
