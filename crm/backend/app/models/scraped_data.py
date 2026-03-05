import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScrapedData(Base):
    __tablename__ = "scraped_data"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("leads.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50))
    source_url: Mapped[str] = mapped_column(String(500))
    source_name: Mapped[str] = mapped_column(String(200))
    raw_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    unit_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    scraped_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.utcnow().isoformat())
    is_matched: Mapped[bool] = mapped_column(default=False)
    is_dismissed: Mapped[bool] = mapped_column(default=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)

    lead: Mapped[Optional["Lead"]] = relationship(back_populates="scraped_data")


from app.models.lead import Lead
