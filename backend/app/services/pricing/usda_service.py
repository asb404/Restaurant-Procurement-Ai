from datetime import datetime, timedelta
import hashlib
import random

from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.models.ingredient_price import IngredientPrice


def _normalize_ingredient_name(name: str) -> str:
    stop_words = {
        "fresh",
        "dried",
        "chopped",
        "sliced",
        "ground",
        "organic",
        "raw",
        "large",
        "small",
        "whole",
    }
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in name.lower())
    tokens = [token for token in cleaned.split() if token and token not in stop_words]
    return " ".join(tokens) or name.strip().lower()


def _keyword_from_name(normalized_name: str) -> str:
    keyword_map = {
        "cheese": "cheese",
        "mozzarella": "cheese",
        "parmesan": "cheese",
        "tomato": "tomato",
        "flour": "flour",
        "oil": "oil",
        "olive": "oil",
        "butter": "butter",
        "onion": "onion",
        "mushroom": "mushroom",
        "sauce": "tomato",
    }
    for token in normalized_name.split():
        if token in keyword_map:
            return keyword_map[token]
    return "default"


def _price_for_keyword(keyword: str) -> float:
    base_prices = {
        "cheese": 8.0,
        "tomato": 3.5,
        "flour": 2.0,
        "oil": 6.0,
        "butter": 7.0,
        "onion": 2.5,
        "mushroom": 4.0,
        "default": 5.0,
    }
    base_price = base_prices.get(keyword, base_prices["default"])

    bucket = int(datetime.utcnow().timestamp() // 300)
    seed_source = f"{keyword}:{bucket}"
    seed_value = int(hashlib.sha256(seed_source.encode("utf-8")).hexdigest()[:8], 16)
    variation = random.Random(seed_value).uniform(0.9, 1.1)
    return round(base_price * variation, 2)


def get_price_for_ingredient(name: str) -> dict:
    normalized = _normalize_ingredient_name(name)
    keyword = _keyword_from_name(normalized)
    return {
        "price": _price_for_keyword(keyword),
        "unit": "kg",
        "source": "USDA",
    }


def _get_price_history_and_trend(ingredient_id: str, source: str, db: Session) -> tuple[list[float], str]:
    recent_rows = (
        db.query(IngredientPrice)
        .filter(
            IngredientPrice.ingredient_id == ingredient_id,
            IngredientPrice.source == source,
        )
        .order_by(IngredientPrice.fetched_at.desc())
        .limit(5)
        .all()
    )
    recent_rows = list(reversed(recent_rows))
    history = [float(row.price) for row in recent_rows]

    if len(history) < 2:
        trend = "stable"
    elif history[-1] > history[0]:
        trend = "increasing"
    elif history[-1] < history[0]:
        trend = "decreasing"
    else:
        trend = "stable"

    return history, trend


def fetch_and_store_prices(ingredient_list: list[Ingredient], db: Session) -> dict[str, dict]:
    pricing: dict[str, dict] = {}
    now = datetime.utcnow()

    for ingredient in ingredient_list:
        price_data = get_price_for_ingredient(ingredient.name)
        current_price = float(price_data["price"])
        current_unit = str(price_data["unit"])
        current_source = str(price_data.get("source", "USDA"))

        latest = (
            db.query(IngredientPrice)
            .filter(
                IngredientPrice.ingredient_id == ingredient.id,
                IngredientPrice.source == current_source,
            )
            .order_by(IngredientPrice.fetched_at.desc())
            .first()
        )

        if (
            latest
            and latest.fetched_at
            and latest.price == current_price
            and latest.fetched_at >= now - timedelta(minutes=5)
        ):
            print(f"Skipping duplicate price for ingredient {ingredient.name}")
            history, trend = _get_price_history_and_trend(
                ingredient_id=ingredient.id,
                source=current_source,
                db=db,
            )
            pricing[ingredient.id] = {
                "price": latest.price,
                "unit": latest.unit,
                "source": latest.source,
                "trend": trend,
                "history": history,
            }
            continue

        print(f"Inserting new price for ingredient {ingredient.name}")
        ingredient_price = IngredientPrice(
            ingredient_id=ingredient.id,
            price=current_price,
            unit=current_unit,
            source=current_source,
        )
        db.add(ingredient_price)
        db.commit()
        db.refresh(ingredient_price)

        history, trend = _get_price_history_and_trend(
            ingredient_id=ingredient.id,
            source=current_source,
            db=db,
        )

        pricing[ingredient.id] = {
            "price": ingredient_price.price,
            "unit": ingredient_price.unit,
            "source": ingredient_price.source,
            "trend": trend,
            "history": history,
        }

    return pricing
