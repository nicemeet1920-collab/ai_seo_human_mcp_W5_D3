import os
import requests
from dotenv import load_dotenv

load_dotenv()


def web_search(query, num_results=5):

    api_key = os.getenv("SERPER_API_KEY")

    if not api_key:
        return "SERPER_API_KEY not found."

    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "q": query,
        "num": num_results
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return f"Search failed: {response.status_code}"

    data = response.json()

    results = []

    for item in data.get("organic", []):

        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")

        results.append(
            f"""
TITLE: {title}
URL: {link}
SUMMARY: {snippet}
"""
        )

    return "\n".join(results)