import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    standard_unit: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    dish_ingredients: Mapped[list["DishIngredient"]] = relationship(
        "DishIngredient",
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )
    prices: Mapped[list["IngredientPrice"]] = relationship(
        "IngredientPrice",
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )
    distributor_ingredients: Mapped[list["DistributorIngredient"]] = relationship(
        "DistributorIngredient",
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )
