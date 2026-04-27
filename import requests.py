import requests

BASE = "https://hj3lee.mycafe24.com/wp-json/nbp/v1"
HEADERS_JSON = {"x-api-key": "NBP_SECRET_BOT_9999", "Content-Type": "application/json"}

r = requests.get(f"{BASE}/targets", timeout=60)
r.raise_for_status()
targets = r.json()

payload = [
    {"post_id": targets[0]["post_id"], "price_current": 1290000, "discount_rate": "-12", "is_soldout": False},
]
r2 = requests.post(f"{BASE}/update-prices", headers=HEADERS_JSON, json=payload, timeout=60)
r2.raise_for_status()
print(r2.json())