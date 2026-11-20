import os
import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from datetime import datetime
import time
import pyautogui as pg
import pytesseract
import pygetwindow as gw
from dotenv import load_dotenv

load_dotenv()

# CONFIG
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
message_thread_id = os.getenv("MESSAGE_THREAD")

NBC_URL = "https://www.nbc.gov.kh/english/economic_research/exchange_rate.php"

# REQUEST SESSION
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[408, 429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
)
session.mount("https://", HTTPAdapter(max_retries=retries))
HEADERS = {"User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        )}

# ZSCALER CHECK + DISABLE
def check_server_connection():
    try:
        r = requests.get("https://www.google.com/generate_204", timeout=5)
        return r.status_code == 204
    except requests.RequestException:
        return False

# FETCH NBC RATE
def fetch_usd_khr_rate():
    resp = session.get(NBC_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    html = resp.text

    m = re.search(
        r"Official\s*Exchange\s*Rate\s*:\s*<font[^>]*>\s*([^<]+?)\s*</font>",
        html,
        re.IGNORECASE
    )

    if not m:
        raise RuntimeError("Could not find exchange rate.")

    return m.group(1).strip()


# TELEGRAM SEND
def send_telegram_text(message: str, thread_id=message_thread_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    if thread_id is not None:
        payload["message_thread_id"] = int(thread_id)

    r = session.post(url, json=payload, timeout=20)
    print("HTTP:", r.status_code)
    print("Resp:", r.text)
    r.raise_for_status()


# MAIN
if __name__ == "__main__":

    rate = fetch_usd_khr_rate()
    rate = int(rate)
    formatted_rate = f"{rate:,}"

    DATE = datetime.now().strftime("%d-%m-%y")
    CURRENCY = "USD"

    MESSAGE = f"""📅 <b>DATE:</b> {DATE}

💵 <b>Currency:</b> {CURRENCY}

💲 <b>Rate:</b> {formatted_rate} ៛
"""

    print("Extracted rate:", formatted_rate)

    # STEP 4: Send Telegram
    send_telegram_text(MESSAGE)

    print("✅ Done")