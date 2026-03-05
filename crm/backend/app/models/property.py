import enum
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PropertyType(str, enum.Enum):
    GARDEN = "garden"
    MIDRISE = "midrise"
    HIGHRISE = "highrise"
    TOWNHOME = "townhome"
    MIXED_USE = "mixed_use"
    SENIOR_LIVING = "senior_living"
    STUDENT_HOUSING = "student_housing"
    AFFORDABLE = "affordable"


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), unique=True)
    property_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    total_units: Mapped[Optional[int]] = mapped_column(nullable=True)
    total_buildings: Mapped[Optional[int]] = mapped_column(nullable=True)
    total_sqft: Mapped[Optional[int]] = mapped_column(nullable=True)
    stories: Mapped[Optional[int]] = mapped_column(nullable=True)
    parking_spaces: Mapped[Optional[int]] = mapped_column(nullable=True)
    permit_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    permit_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    zoning: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    amenities: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)

    lead: Mapped["Lead"] = relationship(back_populates="property")


from app.models.lead import Lead
