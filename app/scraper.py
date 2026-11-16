import json
import random
import time
from urllib.parse import urlparse
from curl_cffi import requests
from bs4 import BeautifulSoup

ALLOWED_DOMAINS = {
    "www.trendyol.com",
    "trendyol.com",
    "www.hepsiburada.com",
    "hepsiburada.com"
}

def validate_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme == "https" and parsed.netloc.lower() in ALLOWED_DOMAINS
    except Exception:
        return False

def scrape_product(url: str) -> dict:
    if not validate_url(url):
        raise ValueError("Geçersiz veya izin verilmeyen URL (SSRF Koruması).")

    time.sleep(random.uniform(1.5, 3.0))

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    response = requests.get(url, headers=headers, impersonate="chrome", timeout=15)
    if response.status_code != 200:
        return {"status": "error", "http_code": response.status_code}

    soup = BeautifulSoup(response.text, "html.parser")
    product_data = {
        "status": "success",
        "url": url,
        "title": None,
        "price": None,
        "in_stock": False
    }

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                data = data[0]
            if data.get("@type") == "Product":
                product_data["title"] = data.get("name")
                offers = data.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0]
                raw_price = offers.get("price")
                product_data["price"] = float(raw_price) if raw_price is not None else None
                product_data["in_stock"] = "InStock" in offers.get("availability", "")
                break
        except Exception:
            continue

    return product_data
