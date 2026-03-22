import json

from app.agents.base_agent import call_ollama


def extract_dishes(menu_text: str) -> list[str]:
    prompt = (
        "Extract a list of dish names from the following menu text. "
        "Return as a JSON list.\n\n"
        f"{menu_text}"
    )
    response = call_ollama(prompt)

    try:
        data = json.loads(response)
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]
    except json.JSONDecodeError:
        pass

    start = response.find("[")
    end = response.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(response[start : end + 1])
            if isinstance(data, list):
                return [str(item).strip() for item in data if str(item).strip()]
        except json.JSONDecodeError:
            return []

    return []
