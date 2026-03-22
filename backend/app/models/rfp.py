import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RFP(Base):
    __tablename__ = "rfps"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    restaurant_id: Mapped[str] = mapped_column(ForeignKey("restaurants.id"), nullable=False)
    menu_id: Mapped[str] = mapped_column(ForeignKey("menus.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String, nullable=False)

    ingredients: Mapped[list["RFPIngredient"]] = relationship(
        "RFPIngredient",
        back_populates="rfp",
        cascade="all, delete-orphan",
    )
