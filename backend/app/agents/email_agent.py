from app.agents.base_agent import call_ollama


def generate_rfp_email(
    distributor_name: str,
    restaurant_name: str,
    location: str,
    ingredients: list[dict],
    current_date: str,
    response_deadline: str,
) -> str:
    ingredient_lines = "\n".join(
        f"- {item.get('name', '')}: {item.get('quantity', '')}" for item in ingredients
    )
    prompt = (
        "Write a professional RFQ email to a food distributor. Include restaurant intro, "
        "ingredient list with quantities, request for quote, and polite closing.\n"
        f"Use the following date in the email: {current_date}\n"
        f"Use the following response deadline in the email: {response_deadline}\n"
        "Do NOT generate your own date. Always use the provided date.\n\n"
        "Do NOT include placeholders, bracketed text, notes, or instructions in output.\n"
        f"Restaurant: {restaurant_name}\n"
        f"Location: {location}\n"
        f"Distributor: {distributor_name}\n"
        f"Ingredients:\n{ingredient_lines}\n"
    )

    try:
        body = call_ollama(prompt)
        cleaned_lines: list[str] = []
        for line in body.splitlines():
            stripped = line.strip()
            if "[" in stripped or "]" in stripped:
                continue
            if not stripped:
                cleaned_lines.append("")
                continue
            cleaned_lines.append(line)
        cleaned_body = "\n".join(cleaned_lines).strip()
        return cleaned_body.replace("[", "").replace("]", "")
    except Exception:
        return (
            f"Date: {current_date}\n\n"
            f"Dear {distributor_name},\n\n"
            f"We are {restaurant_name} located in {location}.\n"
            "We are requesting a quote for the following ingredients:\n"
            f"{ingredient_lines}\n\n"
            f"Please share pricing and availability by {response_deadline}.\n\n"
            "Best regards,\nRestaurant Procurement Team"
        )
