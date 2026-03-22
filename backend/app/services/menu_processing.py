import re

from sqlalchemy.orm import Session

from app.agents.dish_agent import extract_dishes
from app.agents.ingredient_agent import extract_ingredients
from app.models.dish import Dish
from app.models.dish_ingredient import DishIngredient
from app.models.ingredient import Ingredient
from app.models.menu import Menu
from app.models.restaurant import Restaurant
from app.services.distributor.distributor_service import find_distributors_for_ingredients
from app.services.email.rfp_service import create_and_send_rfp
from app.services.pricing.usda_service import fetch_and_store_prices


def _parse_quantity(value: object) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return 0.0
    try:
        return float(match.group())
    except ValueError:
        return 0.0


def _get_or_create_restaurant(
    db_session: Session,
    restaurant_name: str,
    location: str,
) -> Restaurant:
    restaurant = db_session.query(Restaurant).filter(Restaurant.name == restaurant_name).first()
    if restaurant:
        return restaurant

    restaurant = Restaurant(name=restaurant_name, location=location)
    db_session.add(restaurant)
    db_session.commit()
    db_session.refresh(restaurant)
    return restaurant


def process_menu_text(
    restaurant_name: str,
    location: str,
    text: str,
    db_session: Session,
) -> dict:
    restaurant = _get_or_create_restaurant(
        db_session=db_session,
        restaurant_name=restaurant_name,
        location=location,
    )
    menu = Menu(restaurant_id=restaurant.id, raw_text=text, source_type="RAW_TEXT")
    db_session.add(menu)
    db_session.commit()
    db_session.refresh(menu)

    dish_names = extract_dishes(text)
    result: list[dict] = []
    used_ingredients: dict[str, Ingredient] = {}

    for dish_name in dish_names:
        dish = Dish(menu_id=menu.id, name=dish_name)
        db_session.add(dish)
        db_session.commit()
        db_session.refresh(dish)

        ingredient_payload = extract_ingredients(dish_name)
        ingredients_data = ingredient_payload.get("ingredients", [])

        saved_ingredients: list[dict] = []
        for item in ingredients_data:
            ingredient_name = str(item.get("name", "")).strip()
            if not ingredient_name:
                continue

            ingredient = (
                db_session.query(Ingredient)
                .filter(Ingredient.name == ingredient_name)
                .first()
            )
            if not ingredient:
                ingredient = Ingredient(name=ingredient_name, standard_unit="unit")
                db_session.add(ingredient)
                db_session.commit()
                db_session.refresh(ingredient)

            used_ingredients[ingredient.id] = ingredient

            quantity = _parse_quantity(item.get("quantity"))
            mapping = DishIngredient(
                dish_id=dish.id,
                ingredient_id=ingredient.id,
                quantity=quantity,
            )
            db_session.add(mapping)
            db_session.commit()

            saved_ingredients.append(
                {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "quantity": item.get("quantity", ""),
                }
            )

        result.append({"dish": dish.name, "ingredients": saved_ingredients})

    pricing_by_ingredient_id = fetch_and_store_prices(
        list(used_ingredients.values()),
        db_session,
    )
    distributors_by_ingredient_id = find_distributors_for_ingredients(
        ingredients=list(used_ingredients.values()),
        restaurant_location=restaurant.location,
        db=db_session,
    )
    unique_ingredients_for_rfp: list[dict] = []
    seen_ingredient_ids: set[str] = set()
    for dish_entry in result:
        for ingredient_entry in dish_entry["ingredients"]:
            ingredient_id = ingredient_entry.get("id")
            if not ingredient_id or ingredient_id in seen_ingredient_ids:
                continue
            seen_ingredient_ids.add(ingredient_id)
            unique_ingredients_for_rfp.append(
                {
                    "id": ingredient_id,
                    "name": ingredient_entry.get("name", ""),
                    "quantity": ingredient_entry.get("quantity", ""),
                }
            )

    rfp_result = create_and_send_rfp(
        restaurant=restaurant,
        ingredients=unique_ingredients_for_rfp,
        distributors=distributors_by_ingredient_id,
        db=db_session,
    )

    for dish_entry in result:
        for ingredient_entry in dish_entry["ingredients"]:
            ingredient_id = ingredient_entry.pop("id", None)
            if ingredient_id and ingredient_id in pricing_by_ingredient_id:
                ingredient_entry["pricing"] = pricing_by_ingredient_id[ingredient_id]
            if ingredient_id and ingredient_id in distributors_by_ingredient_id:
                ingredient_entry["distributors"] = distributors_by_ingredient_id[ingredient_id]

    return {
        "restaurant_name": restaurant.name,
        "location": restaurant.location,
        "menu_id": menu.id,
        "dishes": result,
        "rfp_id": rfp_result.get("rfp_id"),
        "distributors_contacted": rfp_result.get("distributors_contacted", []),
    }
