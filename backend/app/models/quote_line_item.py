import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class QuoteLineItem(Base):
    __tablename__ = "quote_line_items"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id"), nullable=False)
    ingredient_id: Mapped[str] = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)

    quote: Mapped["Quote"] = relationship("Quote", back_populates="line_items")
