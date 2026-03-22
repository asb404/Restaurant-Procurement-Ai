import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DistributorIngredient(Base):
    __tablename__ = "distributor_ingredients"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    distributor_id: Mapped[str] = mapped_column(ForeignKey("distributors.id"), nullable=False)
    ingredient_id: Mapped[str] = mapped_column(ForeignKey("ingredients.id"), nullable=False)

    distributor: Mapped["Distributor"] = relationship(
        "Distributor",
        back_populates="distributor_ingredients",
    )
    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient",
        back_populates="distributor_ingredients",
    )
