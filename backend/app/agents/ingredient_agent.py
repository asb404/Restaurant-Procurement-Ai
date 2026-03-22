import json

from app.agents.base_agent import call_ollama


def extract_ingredients(dish_name: str) -> dict:
    prompt = (
        "For this dish, return ingredients and quantities in JSON format exactly like:\n"
        '{"dish":"...","ingredients":[{"name":"...","quantity":"..."}]}\n\n'
        f"Dish: {dish_name}"
    )
    response = call_ollama(prompt)

    try:
        data = json.loads(response)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    start = response.find("{")
    end = response.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(response[start : end + 1])
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            return {"dish": dish_name, "ingredients": []}

    return {"dish": dish_name, "ingredients": []}
