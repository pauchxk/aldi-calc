import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ALDI_SEARCH_URL = "https://asl.api.aldi.co.uk/commerce/v3/product-search-suggestion"

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def search_aldi(query):
    """Query Aldi's search-suggestion endpoint and return the list of product dicts."""
    params = {
        "q": query,
        "serviceType": "walk-in",
        "servicePoint": "C297",  # any store code — catalogue prices are national, not per-store
    }
    url = f"{ALDI_SEARCH_URL}?{urlencode(params)}"
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=10) as resp:
        status = getattr(resp, "status", resp.getcode())
        if status >= 400:
            raise RuntimeError(f"Aldi search failed with status {status}")
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("data", {}).get("products", [])


def best_match(results):
    """Aldi's own ranking is usually close enough — just take the top hit."""
    return results[0] if results else None


def load_list(path):
    return [line.strip() for line in Path(path).expanduser().read_text().splitlines() if line.strip()]


def main():
    items = load_list("~/Documents/Obsidian-Notes/Personal/Food/Shopping Lists/Aldi-Calc List Input.md")
    lines = []
    total = 0.0

    for item in items:
        results = search_aldi(item)
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
    Path("groceries_priced.md").write_text(output)


if __name__ == "__main__":
    main()