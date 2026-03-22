import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DishIngredient(Base):
    __tablename__ = "dish_ingredients"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    dish_id: Mapped[str] = mapped_column(ForeignKey("dishes.id"), nullable=False)
    ingredient_id: Mapped[str] = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)

    dish: Mapped["Dish"] = relationship("Dish", back_populates="dish_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient",
        back_populates="dish_ingredients",
    )
