import os
from curl_cffi import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message: str) -> bool:
    """Telegram Bot API üzerinden anlık bildirim gönderir."""
    if not TELEGRAM_BOT_TOKEN or "buraya_" in TELEGRAM_BOT_TOKEN:
        print(f"[UYARI - TELEGRAM AYARLI DEĞİL] Mesaj:\n{message}")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM HATA] {e}")
        return False
