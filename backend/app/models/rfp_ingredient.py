import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RFPIngredient(Base):
    __tablename__ = "rfp_ingredients"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rfp_id: Mapped[str] = mapped_column(ForeignKey("rfps.id"), nullable=False)
    ingredient_id: Mapped[str] = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    quantity: Mapped[str] = mapped_column(String, nullable=False)

    rfp: Mapped["RFP"] = relationship("RFP", back_populates="ingredients")
