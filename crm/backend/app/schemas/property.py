from typing import Optional
from pydantic import BaseModel


class PropertyCreate(BaseModel):
    property_type: Optional[str] = None
    total_units: Optional[int] = None
    total_buildings: Optional[int] = None
    total_sqft: Optional[int] = None
    stories: Optional[int] = None
    parking_spaces: Optional[int] = None
    permit_number: Optional[str] = None
    permit_date: Optional[str] = None
    zoning: Optional[str] = None
    amenities: Optional[str] = None


class PropertyUpdate(BaseModel):
    property_type: Optional[str] = None
    total_units: Optional[int] = None
    total_buildings: Optional[int] = None
    total_sqft: Optional[int] = None
    stories: Optional[int] = None
    parking_spaces: Optional[int] = None
    permit_number: Optional[str] = None
    permit_date: Optional[str] = None
    zoning: Optional[str] = None
    amenities: Optional[str] = None


class PropertyResponse(BaseModel):
    id: str
    lead_id: str
    property_type: Optional[str] = None
    total_units: Optional[int] = None
    total_buildings: Optional[int] = None
    total_sqft: Optional[int] = None
    stories: Optional[int] = None
    parking_spaces: Optional[int] = None
    permit_number: Optional[str] = None
    permit_date: Optional[str] = None
    zoning: Optional[str] = None
    amenities: Optional[str] = None

    class Config:
        from_attributes = True
