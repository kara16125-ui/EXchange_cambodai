import os
import sys
import re
import html as html_lib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import time
import pyautogui as pg
import pygetwindow as gw

NBC_URL = "https://www.nbc.gov.kh/english/economic_research/exchange_rate.php"

# ==============================
# REQUESTS SESSION (retries)
# ==============================
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

# ==============================
# ZSCALER CHECK + DISABLE
# ==============================
def check_server_connection():
    try:
        r = requests.get("https://www.google.com/generate_204", timeout=5)
        return r.status_code == 204
    except requests.RequestException:
        return False

# FETCH RATE

def fetch_usd_khr_rate_or_exit():
    resp = session.get(NBC_URL, headers=HEADERS, timeout=30, allow_redirects=True)
    resp.raise_for_status()

    page = html_lib.unescape(resp.text)
    page = page.replace("&nbsp;", " ").replace("\xa0", " ")

    m = re.search(
        r"Official.*?Exchange.*?Rate\s*:\s*([0-9,]{1,10})\s*KHR\s*/\s*USD",
        page,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not m:
        m = re.search(
            r"Official\s*Exchange\s*Rate\s*:\s*<font[^>]*>\s*([0-9,]{1,10})\s*</font>\s*KHR\s*/\s*USD",
            page,
            flags=re.IGNORECASE | re.DOTALL
        )

    if not m:
        print("NBC rate not found. Exit.")
        sys.exit(0)

    rate_str = m.group(1).replace(",", "").strip()

    if rate_str in ("0000", "0", ""):
        print("NBC shows 0000. Exit.")
        sys.exit(0)

    return int(rate_str)
# MAIN
if __name__ == "__main__":

    now = datetime.now()

    # ====== FETCH RATE ======
    official_rate = fetch_usd_khr_rate_or_exit()
    formatted_rate = f"{official_rate:,}"
    print("NBC official USD/KHR rate:", formatted_rate)

    # TXT OUTPUT
    
    year = now.strftime("%Y")
    month_folder = now.strftime("%m. %B")

    base_folder = os.path.dirname(os.path.abspath(__file__))
    destination_txt_folder = os.path.join(base_folder,"txt", year, month_folder)
    os.makedirs(destination_txt_folder, exist_ok=True)

    txt_file_name = now.strftime("%m-%d-%y") + ".txt"
    txt_file_path = os.path.join(destination_txt_folder, txt_file_name)

    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write(formatted_rate)

    print("File created:", txt_file_path)

    # PDF DOWNLOAD
    
    DATE = now.strftime("%d-%m-%Y")
    pdf_url = f"https://nbc.gov.kh/files/exchange-rate/official-exchange-rate/oer_{DATE}.pdf"
    print(pdf_url) #TODO
    base_pdf_folder = os.path.dirname(os.path.abspath(__file__))
    destination_pdf_folder = os.path.join(base_pdf_folder, year, month_folder)
    os.makedirs(destination_pdf_folder, exist_ok=True)

    pdf_file_name = now.strftime("%d-%m-%y") + ".pdf"
    pdf_file_path = os.path.join(destination_pdf_folder, pdf_file_name)

    response = session.get(pdf_url, headers=HEADERS, timeout=30, allow_redirects=True)

    if response.status_code == 200:
        with open(pdf_file_path, "wb") as f:
            f.write(response.content)
        print("PDF downloaded:", pdf_file_path)
    else:
        print("PDF failed")

        if os.path.exists(txt_file_path):
            os.remove(txt_file_path)
            print("TXT removed due to PDF failure")

        sys.exit(0)