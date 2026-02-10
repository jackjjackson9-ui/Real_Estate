import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from twilio.rest import Client

SEARCH_ZIP = "08742"
SEARCH_URL = f"https://www.realtor.com/realestateandhomes-search/{SEARCH_ZIP}"
STATE_FILE = Path("seen_listings.json")


@dataclass
class Listing:
    listing_id: str
    address: str
    url: str


def fetch_listings(zip_code: str = SEARCH_ZIP) -> List[Listing]:
    url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    next_data = soup.find("script", {"id": "__NEXT_DATA__"})
    if not next_data or not next_data.string:
        raise RuntimeError("Could not find listing JSON in page")

    payload = json.loads(next_data.string)

    # Realtor page shape can vary; this finds any list under key 'properties'.
    raw_properties = _find_first_properties_array(payload)
    if not raw_properties:
        return []

    listings: List[Listing] = []
    for p in raw_properties:
        listing_id = str(
            p.get("property_id")
            or p.get("listing_id")
            or p.get("permalink")
            or ""
        )
        if not listing_id:
            continue

        line = p.get("location", {}).get("address", {}).get("line") or p.get("address", {}).get("line")
        city = p.get("location", {}).get("address", {}).get("city") or p.get("address", {}).get("city")
        state_code = p.get("location", {}).get("address", {}).get("state_code") or p.get("address", {}).get("state_code")
        postal = p.get("location", {}).get("address", {}).get("postal_code") or p.get("address", {}).get("postal_code")

        parts = [x for x in [line, city, state_code, postal] if x]
        address = ", ".join(parts) if parts else "Address unavailable"

        listing_url = p.get("href") or p.get("permalink") or ""
        if listing_url and not listing_url.startswith("http"):
            listing_url = f"https://www.realtor.com{listing_url}"

        if not listing_url:
            listing_url = SEARCH_URL

        listings.append(Listing(listing_id=listing_id, address=address, url=listing_url))

    return listings


def _find_first_properties_array(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "properties" and isinstance(v, list):
                return v
            found = _find_first_properties_array(v)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for i in obj:
            found = _find_first_properties_array(i)
            if found is not None:
                return found
    return None


def load_seen_ids() -> set:
    if not STATE_FILE.exists():
        return set()
    data = json.loads(STATE_FILE.read_text())
    return set(data.get("seen_ids", []))


def save_seen_ids(ids: set) -> None:
    STATE_FILE.write_text(json.dumps({"seen_ids": sorted(ids)}, indent=2))


def build_message(new_listings: List[Listing]) -> str:
    if not new_listings:
        return "No new 08742 listings today."

    lines = ["New 08742 listings:"]
    for item in new_listings:
        lines.append(f"- {item.address} | {item.url}")

    message = "\n".join(lines)
    if len(message) > 1550:
        # SMS safety margin.
        message = message[:1540] + "\n..."
    return message


def send_sms(body: str) -> None:
    load_dotenv()

    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_FROM_NUMBER")
    to_phone = os.getenv("TO_PHONE", "+17326109003")

    missing = [
        name
        for name, value in {
            "TWILIO_ACCOUNT_SID": sid,
            "TWILIO_AUTH_TOKEN": token,
            "TWILIO_FROM_NUMBER": from_phone,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

    client = Client(sid, token)
    client.messages.create(body=body, from_=from_phone, to=to_phone)


def run_once() -> Dict[str, int]:
    listings = fetch_listings(SEARCH_ZIP)
    seen = load_seen_ids()

    new_listings = [l for l in listings if l.listing_id not in seen]

    for l in listings:
        seen.add(l.listing_id)
    save_seen_ids(seen)

    body = build_message(new_listings)
    send_sms(body)

    return {
        "total_found": len(listings),
        "new_found": len(new_listings),
        "sent_at": int(datetime.utcnow().timestamp()),
    }


if __name__ == "__main__":
    result = run_once()
    print(json.dumps(result, indent=2))
