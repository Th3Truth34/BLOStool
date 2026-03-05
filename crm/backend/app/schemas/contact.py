from typing import Optional
from pydantic import BaseModel


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    role: str = "other"
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_primary: bool = False
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_primary: Optional[bool] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: str
    lead_id: str
    first_name: str
    last_name: str
    role: str
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_primary: bool
    notes: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
