import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rfp_id: Mapped[str] = mapped_column(ForeignKey("rfps.id"), nullable=False)
    distributor_id: Mapped[str] = mapped_column(ForeignKey("distributors.id"), nullable=False)
    from_email: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    message_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    raw_body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    line_items: Mapped[list["QuoteLineItem"]] = relationship(
        "QuoteLineItem",
        back_populates="quote",
        cascade="all, delete-orphan",
    )
