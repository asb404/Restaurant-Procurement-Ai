import re


LINE_PATTERN = re.compile(
    r"(?P<name>[A-Za-z ]{2,})\s*[-:]\s*\$?(?P<price>\d+(?:\.\d+)?)\s*/\s*(?P<unit>[A-Za-z]+)",
    re.IGNORECASE,
)


def parse_quote_email(body: str) -> list[dict]:
    quotes: list[dict] = []
    for line in body.splitlines():
        match = LINE_PATTERN.search(line.strip())
        if not match:
            continue
        quotes.append(
            {
                "ingredient_name": match.group("name").strip().lower(),
                "price": float(match.group("price")),
                "unit": match.group("unit").lower(),
            }
        )
    return quotes
