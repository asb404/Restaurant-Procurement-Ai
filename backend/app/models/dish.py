import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    menu_id: Mapped[str] = mapped_column(ForeignKey("menus.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    menu: Mapped["Menu"] = relationship("Menu", back_populates="dishes")
    dish_ingredients: Mapped[list["DishIngredient"]] = relationship(
        "DishIngredient",
        back_populates="dish",
        cascade="all, delete-orphan",
    )
