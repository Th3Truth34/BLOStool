from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contact import Contact
from app.models.lead import Lead
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter(prefix="/leads/{lead_id}/contacts", tags=["contacts"])


@router.get("", response_model=list[ContactResponse])
async def list_contacts(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Contact).where(Contact.lead_id == lead_id).order_by(Contact.is_primary.desc(), Contact.created_at)
    )
    return result.scalars().all()


@router.post("", response_model=ContactResponse)
async def create_contact(lead_id: str, contact_data: ContactCreate, db: AsyncSession = Depends(get_db)):
    # Verify lead exists
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Lead not found")

    contact = Contact(lead_id=lead_id, **contact_data.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(lead_id: str, contact_id: str, contact_data: ContactUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id, Contact.lead_id == lead_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for field, value in contact_data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/{contact_id}")
async def delete_contact(lead_id: str, contact_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contact).where(Contact.id == contact_id, Contact.lead_id == lead_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    await db.delete(contact)
    await db.commit()
    return {"detail": "Contact deleted"}
