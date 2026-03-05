from typing import Optional
from pydantic import BaseModel


class LeadCreate(BaseModel):
    project_name: str
    status: str = "new"
    source: str = "manual"
    priority: int = 3
    unit_count: Optional[int] = None
    estimated_value: Optional[str] = None
    project_type: Optional[str] = None
    construction_phase: Optional[str] = None
    estimated_completion: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[str] = None
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    project_name: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    priority: Optional[int] = None
    unit_count: Optional[int] = None
    estimated_value: Optional[str] = None
    project_type: Optional[str] = None
    construction_phase: Optional[str] = None
    estimated_completion: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[str] = None
    loss_reason: Optional[str] = None
    notes: Optional[str] = None


class LeadResponse(BaseModel):
    id: str
    project_name: str
    status: str
    source: str
    priority: int
    unit_count: Optional[int] = None
    estimated_value: Optional[str] = None
    project_type: Optional[str] = None
    construction_phase: Optional[str] = None
    estimated_completion: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[str] = None
    loss_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str
    contact_count: int = 0
    activity_count: int = 0

    class Config:
        from_attributes = True


class PipelineResponse(BaseModel):
    status: str
    count: int
    leads: list[LeadResponse]
