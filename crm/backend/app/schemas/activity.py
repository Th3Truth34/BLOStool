from typing import Optional
from pydantic import BaseModel


class ActivityCreate(BaseModel):
    activity_type: str
    title: str
    description: Optional[str] = None


class ActivityResponse(BaseModel):
    id: str
    lead_id: str
    activity_type: str
    title: str
    description: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
