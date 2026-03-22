import json
from urllib import request


def call_ollama(prompt: str, model: str = "gemma3:4b") -> str:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")

    req = request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(req) as response:
        body = response.read().decode("utf-8")

    data = json.loads(body)
    return str(data.get("response", "")).strip()
