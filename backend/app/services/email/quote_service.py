import hashlib

from sqlalchemy.orm import Session

from app.models.distributor import Distributor
from app.models.ingredient import Ingredient
from app.models.quote import Quote
from app.models.quote_line_item import QuoteLineItem
from app.models.rfp import RFP
from app.models.rfp_ingredient import RFPIngredient
from app.services.email.inbox_monitor import fetch_recent_quote_emails
from app.services.email.quote_parser import parse_quote_email


def _find_requested_ingredients(rfp_id: str, db: Session) -> dict[str, Ingredient]:
    requested = (
        db.query(Ingredient)
        .join(RFPIngredient, RFPIngredient.ingredient_id == Ingredient.id)
        .filter(RFPIngredient.rfp_id == rfp_id)
        .all()
    )
    return {ingredient.name.lower(): ingredient for ingredient in requested}


def ingest_quotes_for_rfp(rfp_id: str, db: Session) -> dict:
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    if not rfp:
        return {"ingested": 0, "skipped": 0, "message": "RFP not found"}

    ingredient_map = _find_requested_ingredients(rfp_id, db)
    emails = fetch_recent_quote_emails()

    ingested = 0
    skipped = 0

    for email_data in emails:
        message_id = email_data.get("message_id", "")
        if not message_id:
            skipped += 1
            continue

        existing = db.query(Quote).filter(Quote.message_id == message_id).first()
        if existing:
            skipped += 1
            continue

        from_email = str(email_data.get("from_email", "")).lower().strip()
        distributor = (
            db.query(Distributor)
            .filter(Distributor.contact_email.ilike(from_email))
            .first()
        )
        if not distributor:
            print(f"Skipping quote email: no distributor match for {from_email}")
            skipped += 1
            continue

        quote = Quote(
            rfp_id=rfp_id,
            distributor_id=distributor.id,
            from_email=from_email,
            subject=str(email_data.get("subject", "")),
            message_id=message_id,
            raw_body=str(email_data.get("body", "")),
        )
        db.add(quote)
        db.commit()
        db.refresh(quote)

        parsed_items = parse_quote_email(quote.raw_body)
        for item in parsed_items:
            ingredient_name = str(item.get("ingredient_name", "")).lower().strip()
            ingredient = None

            if ingredient_name in ingredient_map:
                ingredient = ingredient_map[ingredient_name]
            else:
                for key, value in ingredient_map.items():
                    if ingredient_name in key or key in ingredient_name:
                        ingredient = value
                        break

            if not ingredient:
                print(f"Warning: ingredient not found for parsed item '{ingredient_name}', skipping")
                continue

            line_item = QuoteLineItem(
                quote_id=quote.id,
                ingredient_id=ingredient.id,
                unit_price=float(item.get("price", 0.0)),
                unit=str(item.get("unit", "kg")),
            )
            db.add(line_item)

        db.commit()
        ingested += 1

    return {"ingested": ingested, "skipped": skipped, "emails_checked": len(emails)}


def compare_quotes(rfp_id: str, db: Session) -> dict:
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    if not rfp:
        return {"rfp_id": rfp_id, "totals": [], "recommended_distributor": None}

    quotes = db.query(Quote).filter(Quote.rfp_id == rfp_id).all()
    totals_map: dict[str, dict] = {}

    for quote in quotes:
        distributor = db.query(Distributor).filter(Distributor.id == quote.distributor_id).first()
        if not distributor:
            continue

        total_cost = sum(item.unit_price for item in quote.line_items)
        current = totals_map.setdefault(
            distributor.id,
            {
                "distributor_id": distributor.id,
                "distributor_name": distributor.name,
                "total_cost": 0.0,
            },
        )
        current["total_cost"] += float(total_cost)

    totals = sorted(totals_map.values(), key=lambda x: x["total_cost"])
    recommended = totals[0] if totals else None

    return {
        "rfp_id": rfp_id,
        "totals": totals,
        "recommended_distributor": recommended,
    }


def _base_price_for_ingredient(name: str) -> float:
    normalized = name.lower()
    mapping = {
        "cheese": 7.0,
        "tomato": 3.5,
        "flour": 2.0,
        "oil": 6.0,
        "butter": 7.0,
        "onion": 2.5,
        "mushroom": 4.0,
    }
    for key, value in mapping.items():
        if key in normalized:
            return value
    return 5.0


def generate_mock_quotes(rfp_id: str, db: Session) -> dict:
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    if not rfp:
        return {"generated": 0, "skipped": 0, "message": "RFP not found"}

    requested_ingredients = (
        db.query(Ingredient)
        .join(RFPIngredient, RFPIngredient.ingredient_id == Ingredient.id)
        .filter(RFPIngredient.rfp_id == rfp_id)
        .all()
    )
    if not requested_ingredients:
        return {"generated": 0, "skipped": 0, "message": "No ingredients found for RFP"}

    ingredient_ids = [ingredient.id for ingredient in requested_ingredients]
    distributors = (
        db.query(Distributor)
        .join(
            Distributor.distributor_ingredients,
        )
        .filter(
            Distributor.contact_email.isnot(None),
            Distributor.distributor_ingredients.any(),
        )
        .all()
    )
    if not distributors:
        distributors = db.query(Distributor).all()

    generated = 0
    skipped = 0

    for distributor_index, distributor in enumerate(distributors):
        message_id = f"<mock-{rfp_id}-{distributor.id}@demo.local>"
        existing_quote = db.query(Quote).filter(Quote.message_id == message_id).first()
        if existing_quote:
            skipped += 1
            continue

        lines: list[str] = []
        line_item_payloads: list[tuple[str, float, str]] = []

        for ingredient_index, ingredient in enumerate(requested_ingredients):
            base_price = _base_price_for_ingredient(ingredient.name)
            distributor_shift = 1.0 + ((distributor_index % 5) - 2) * 0.03
            hash_seed = f"{rfp_id}:{distributor.id}:{ingredient.id}:{ingredient_index}"
            hash_value = int(hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:8], 16)
            jitter = 0.97 + (hash_value % 7) * 0.01
            price = round(base_price * distributor_shift * jitter, 2)
            lines.append(f"{ingredient.name} - {price}/kg")
            line_item_payloads.append((ingredient.id, price, "kg"))

        quote = Quote(
            rfp_id=rfp_id,
            distributor_id=distributor.id,
            from_email=distributor.contact_email,
            subject=f"Quote for RFP {rfp_id}",
            message_id=message_id,
            raw_body="\n".join(lines),
        )
        db.add(quote)
        db.commit()
        db.refresh(quote)

        for ingredient_id, unit_price, unit in line_item_payloads:
            if ingredient_id not in ingredient_ids:
                continue
            db.add(
                QuoteLineItem(
                    quote_id=quote.id,
                    ingredient_id=ingredient_id,
                    unit_price=unit_price,
                    unit=unit,
                )
            )
        db.commit()
        generated += 1

    return {
        "generated": generated,
        "skipped": skipped,
        "distributors_considered": len(distributors),
    }
