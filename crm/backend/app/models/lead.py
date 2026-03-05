import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    RESEARCHING = "researching"
    CONTACTED = "contacted"
    MEETING_SCHEDULED = "meeting_scheduled"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    WON = "won"
    LOST = "lost"


class LeadSource(str, enum.Enum):
    SCRAPED_PERMIT = "scraped_permit"
    SCRAPED_NEWS = "scraped_news"
    SCRAPED_PLANNING = "scraped_planning"
    MANUAL = "manual"
    REFERRAL = "referral"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default=LeadStatus.NEW.value)
    source: Mapped[str] = mapped_column(String(30), default=LeadSource.MANUAL.value)
    priority: Mapped[int] = mapped_column(default=3)

    # Project details
    unit_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    estimated_value: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    project_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    construction_phase: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_completion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Location
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Tracking
    next_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    next_action_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    loss_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())
    updated_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())

    # Relationships
    contacts: Mapped[list["Contact"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    property: Mapped[Optional["Property"]] = relationship(back_populates="lead", uselist=False, cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    scraped_data: Mapped[list["ScrapedData"]] = relationship(back_populates="lead")


from app.models.contact import Contact
from app.models.property import Property
from app.models.activity import Activity
from app.models.scraped_data import ScrapedData
