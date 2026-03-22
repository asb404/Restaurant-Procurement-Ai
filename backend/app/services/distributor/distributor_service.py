from sqlalchemy.orm import Session

from app.models.distributor import Distributor
from app.models.distributor_ingredient import DistributorIngredient
from app.models.ingredient import Ingredient


def find_distributors_for_ingredients(
    ingredients: list[Ingredient],
    restaurant_location: str,
    db: Session,
) -> dict[str, list[dict]]:
    if "bloomington" in restaurant_location.lower():
        distributor_names = [
            "Bloomington Fresh Produce",
            "Indiana Food Supply Co.",
            "Midwest Restaurant Distributors",
        ]
    else:
        distributor_names = [
            "Global Food Distributors",
            "Fresh Farms Supply",
        ]

    distributors: list[Distributor] = []
    for name in distributor_names:
        distributor = db.query(Distributor).filter(Distributor.name == name).first()
        if not distributor:
            email_name = name.lower().replace(" ", ".")
            distributor = Distributor(
                name=name,
                location=restaurant_location,
                contact_email=f"contact@{email_name}.com",
            )
            db.add(distributor)
            db.commit()
            db.refresh(distributor)
        distributors.append(distributor)

    matches: dict[str, list[dict]] = {}
    count = len(distributors)

    for index, ingredient in enumerate(ingredients):
        assigned = [distributors[index % count]]
        if count > 1:
            assigned.append(distributors[(index + 1) % count])

        unique_assigned = {d.id: d for d in assigned}.values()
        matches[ingredient.id] = []

        for distributor in unique_assigned:
            existing = (
                db.query(DistributorIngredient)
                .filter(
                    DistributorIngredient.distributor_id == distributor.id,
                    DistributorIngredient.ingredient_id == ingredient.id,
                )
                .first()
            )
            if not existing:
                mapping = DistributorIngredient(
                    distributor_id=distributor.id,
                    ingredient_id=ingredient.id,
                )
                db.add(mapping)
                db.commit()

            matches[ingredient.id].append(
                {
                    "id": distributor.id,
                    "name": distributor.name,
                    "location": distributor.location,
                    "contact_email": distributor.contact_email,
                }
            )

    return matches
