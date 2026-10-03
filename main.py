import json
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

ALDI_SEARCH_URL = "https://asl.api.aldi.co.uk/commerce/v3/product-search"
BRAND_FILTER = "EVERYDAY ESSENTIALS"

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def search_aldi(query, brand_filter=None):
    params = {
        "q": query,
        "serviceType": "walk-in",
        "servicePoint": "C297",
        "currency": "GBP",
        "limit": 30,
        "offset": 0,
        "sort": "relevance",
    }
    if brand_filter:
        params["brandName[]"] = brand_filter

    url = f"{ALDI_SEARCH_URL}?{urlencode(params, quote_via=quote)}"
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=10) as resp:
        status = getattr(resp, "status", resp.getcode())
        if status >= 400:
            raise RuntimeError(f"Aldi search failed with status {status}")
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("data", [])


def best_match(results):
    """Aldi's own ranking is usually close enough — just take the top hit."""
    return results[0] if results else None


def load_list(path):
    return [line.strip() for line in Path(path).expanduser().read_text().splitlines() if line.strip()]


def choose_mode():
    print("1. Search all brands")
    print("2. Everyday Essentials only")
    choice = input("Choose 1 or 2: ").strip()
    return BRAND_FILTER if choice == "2" else None


def main():
    brand_filter = choose_mode()

    items = load_list("~/Documents/Obsidian-Notes/Personal/Food/Shopping Lists/Aldi-Calc List Input.md")
    lines = []
    total = 0.0

    for item in items:
        results = search_aldi(item, brand_filter)
        match = best_match(results)

        if match:
            name = match.get("name", item)
            price_display = match["price"]["amountRelevantDisplay"]  # e.g. '£0.95'
            price = match["price"]["amount"] / 100  # amount is in pence
            lines.append(f"- {name} — {price_display}  _(searched: '{item}')_")
            total += price
        else:
            lines.append(f"- {item} — not found")

    lines.append(f"\n**Total: £{total:.2f}**")

    output = "\n".join(lines)
    print(output)
    Path("/home/pauchxk/Documents/Obsidian-Notes/Personal/Food/Shopping Lists/Aldi-Calc List Output.md").write_text(output)


if __name__ == "__main__":
    main()