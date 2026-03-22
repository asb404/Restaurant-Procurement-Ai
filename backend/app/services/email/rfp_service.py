from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.agents.email_agent import generate_rfp_email
from app.models.menu import Menu
from app.models.rfp import RFP
from app.models.rfp_ingredient import RFPIngredient
from app.services.email.email_sender import send_email


def normalize_ingredient_name(name: str) -> str:
    cleaned = name.strip().lower()
    replacements = {
        "egg wash": "eggs",
    }
    for source, target in replacements.items():
        if source in cleaned:
            return target
    return cleaned


def normalize_quantity(ingredient_name: str, original_quantity: str) -> str:
    name = normalize_ingredient_name(ingredient_name)

    liquid_keywords = [
        "oil",
        "sauce",
        "vinegar",
        "milk",
        "water",
        "broth",
        "stock",
        "juice",
        "cream",
    ]
    if any(keyword in name for keyword in liquid_keywords):
        return "1 L"

    solid_overrides = {
        "flour": "1 kg",
        "cheese": "500 g",
        "tomato": "1 kg",
        "onion": "1 kg",
        "potato": "1 kg",
        "carrot": "1 kg",
    }
    for keyword, value in solid_overrides.items():
        if keyword in name:
            return value

    return "1 kg"


def create_and_send_rfp(restaurant, ingredients: list[dict], distributors: dict[str, list[dict]], db: Session) -> dict:
    menu = (
        db.query(Menu)
        .filter(Menu.restaurant_id == restaurant.id)
        .order_by(Menu.created_at.desc())
        .first()
    )
    if not menu:
        return {"rfp_id": None, "distributors_contacted": []}

    rfp = RFP(restaurant_id=restaurant.id, menu_id=menu.id, status="SENT")
    db.add(rfp)
    db.commit()
    db.refresh(rfp)

    seen_ingredient_ids: set[str] = set()
    for item in ingredients:
        ingredient_id = item.get("id")
        if not ingredient_id or ingredient_id in seen_ingredient_ids:
            continue
        seen_ingredient_ids.add(ingredient_id)
        normalized_quantity = normalize_quantity(
            ingredient_name=str(item.get("name", "")),
            original_quantity=str(item.get("quantity", "")),
        )
        normalized_name = normalize_ingredient_name(str(item.get("name", "")))

        rfp_item = RFPIngredient(
            rfp_id=rfp.id,
            ingredient_id=ingredient_id,
            quantity=normalized_quantity,
        )
        db.add(rfp_item)
    db.commit()

    ingredients_by_distributor: dict[str, dict] = {}
    for item in ingredients:
        ingredient_id = item.get("id")
        if not ingredient_id:
            continue
        for distributor in distributors.get(ingredient_id, []):
            distributor_id = distributor["id"]
            entry = ingredients_by_distributor.setdefault(
                distributor_id,
                {
                    "name": distributor["name"],
                    "contact_email": distributor["contact_email"],
                    "ingredients": [],
                },
            )
            if not any(existing.get("id") == ingredient_id for existing in entry["ingredients"]):
                entry["ingredients"].append(
                    {
                        "id": ingredient_id,
                        "name": normalize_ingredient_name(str(item.get("name", ""))),
                        "quantity": normalize_quantity(
                            ingredient_name=str(item.get("name", "")),
                            original_quantity=str(item.get("quantity", "")),
                        ),
                    }
                )

    distributors_contacted: list[dict] = []
    now = datetime.now()
    current_date = now.strftime("%B %d, %Y")
    response_deadline = (now + timedelta(days=7)).strftime("%B %d, %Y")
    for distributor_id, data in ingredients_by_distributor.items():
        body = generate_rfp_email(
            distributor_name=data["name"],
            restaurant_name=restaurant.name,
            location=restaurant.location,
            ingredients=data["ingredients"],
            current_date=current_date,
            response_deadline=response_deadline,
        )
        send_email(
            to_email=data["contact_email"],
            subject=f"RFP Request from {restaurant.name}",
            body=body,
        )
        distributors_contacted.append(
            {
                "id": distributor_id,
                "name": data["name"],
                "contact_email": data["contact_email"],
            }
        )

    return {"rfp_id": rfp.id, "distributors_contacted": distributors_contacted}
