
import os
import re
import time
import requests

from io import BytesIO
from datetime import date, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pypdf import PdfReader 

# ==================================================
# CONFIGURATION
# ==================================================

START_DATE = date(2025, 1, 1)
END_DATE = date.today() - timedelta(days=1)

def get_pdf_url(target_date):

    if target_date.year == 2025:

        filename = target_date.strftime(
            "official-exchange-rate-2025-%m-%d.pdf"
        )

    else:

        filename = target_date.strftime(
            "oer_%d-%m-%Y.pdf"
        )

    return (
        "https://nbc.gov.kh/files/exchange-rate/"
        f"official-exchange-rate/{filename}"
    )

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

# ==================================================
# REQUEST SESSION WITH RETRIES
# ==================================================

session = requests.Session()

retries = Retry(
    total=5,
    connect=5,
    read=5,
    backoff_factor=0.5,
    status_forcelist=[408, 429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

session.mount(
    "https://",
    HTTPAdapter(max_retries=retries)
)

# ==================================================
# EXTRACT RATE FROM PDF
# ==================================================

def extract_rate_from_pdf(pdf_content):

    try:

        reader = PdfReader(BytesIO(pdf_content))

        pdf_text = ""

        for page in reader.pages:
            pdf_text += page.extract_text() or ""

        pdf_text = pdf_text.replace("\xa0", " ")

        patterns = [
            r"Official\s*Exchange\s*Rate\s*:?\s*"
            r"([0-9,]{1,10})\s*KHR\s*/\s*USD",

            r"Official\s*Exchange\s*Rate\s*:?\s*"
            r"([0-9,]{1,10})"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                pdf_text,
                flags=re.IGNORECASE | re.DOTALL
            )

            if match:

                rate = match.group(1).replace(",", "").strip()

                if rate not in ("0", "0000", ""):
                    return int(rate)

        return None

    except Exception as e:

        print("[PDF EXTRACTION ERROR]", e)

        return None


# ==================================================
# DOWNLOAD ONE DATE
# ==================================================


def download_exchange_rate(target_date):

    DATE = target_date.strftime("%d-%m-%Y")

    year = target_date.strftime("%Y")
    month_folder = target_date.strftime("%m. %B")

    # ----------------------------------------------
    # FOLDERS
    # ----------------------------------------------

    pdf_folder = os.path.join(
        BASE_FOLDER,
        year,
        month_folder
    )

    txt_folder = os.path.join(
        BASE_FOLDER,
        "txt",
        year,
        month_folder
    )

    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(txt_folder, exist_ok=True)

    # ----------------------------------------------
    # FILE PATHS
    # ----------------------------------------------

    pdf_file_name = target_date.strftime("%d-%m-%y") + ".pdf"
    txt_file_name = target_date.strftime("%m-%d-%y") + ".txt"

    pdf_file_path = os.path.join(pdf_folder, pdf_file_name)
    txt_file_path = os.path.join(txt_folder, txt_file_name)

    # ----------------------------------------------
    # CHECK EXISTING PDF AND TXT
    # ----------------------------------------------

    if os.path.exists(pdf_file_path) and os.path.exists(txt_file_path):

        print(f"[EXISTS - SKIP] {DATE}")

        return "EXISTS"

    # ----------------------------------------------
    # USE EXISTING PDF FIRST
    # ----------------------------------------------

    if os.path.exists(pdf_file_path):

        print(f"[PDF ALREADY EXISTS] {DATE}")

        try:
            with open(pdf_file_path, "rb") as f:
                pdf_content = f.read()

        except Exception as e:

            print(f"[PDF READ ERROR] {DATE}: {e}")

            return "ERROR"

    else:

        # ------------------------------------------
        # DOWNLOAD ONLY IF PDF DOES NOT EXIST
        # ------------------------------------------

        pdf_url = get_pdf_url(target_date)

        try:

            response = session.get(
                pdf_url,
                headers=HEADERS,
                timeout=30,
                allow_redirects=True
            )

            if response.status_code != 200:

                print(f"[NOT AVAILABLE] {DATE}")

                return "NOT_FOUND"

            if not response.content.startswith(b"%PDF-"):

                print(f"[INVALID PDF] {DATE}")

                return "INVALID"

            pdf_content = response.content

            with open(pdf_file_path, "wb") as f:
                f.write(pdf_content)

            print(f"[PDF DOWNLOADED] {DATE}")

        except Exception as e:

            print(f"[DOWNLOAD ERROR] {DATE}: {e}")

            return "ERROR"

    # ----------------------------------------------
    # EXTRACT RATE FROM EXISTING OR NEW PDF
    # ----------------------------------------------

    official_rate = extract_rate_from_pdf(pdf_content)

    if official_rate is None:

        print(f"[RATE NOT FOUND] {DATE}")

        return "RATE_ERROR"

    formatted_rate = f"{official_rate:,}"

    # ----------------------------------------------
    # CREATE TXT ONLY IF MISSING
    # ----------------------------------------------

    if not os.path.exists(txt_file_path):

        with open(txt_file_path, "w", encoding="utf-8") as f:
            f.write(formatted_rate)

        print(f"[TXT CREATED] {DATE}: {formatted_rate}")

    else:

        print(f"[TXT EXISTS] {DATE}")

    return "SUCCESS"



# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    print("=" * 60)
    print("NBC HISTORICAL EXCHANGE RATE DOWNLOADER")
    print("=" * 60)

    print("FROM:", START_DATE)
    print("TO  :", END_DATE)

    print()

    # ----------------------------------------------
    # COUNTERS
    # ----------------------------------------------

    total = 0
    success = 0
    exists = 0
    not_found = 0
    rate_errors = 0
    invalid = 0
    errors = 0

    # ----------------------------------------------
    # DOWNLOAD FORWARD FROM JANUARY 1, 2025
    # ----------------------------------------------

    current_date = START_DATE

    while current_date <= END_DATE:

        total += 1

        print()
        print("-" * 60)

        print(
            f"[{total}] Processing: "
            f"{current_date.strftime('%d-%m-%Y')}"
            f"{get_pdf_url}"
        )

        print("-" * 60)

        result = download_exchange_rate(current_date)

        if result == "SUCCESS":
            success += 1

        elif result == "EXISTS":
            exists += 1

        elif result == "NOT_FOUND":
            not_found += 1

        elif result == "RATE_ERROR":
            rate_errors += 1

        elif result == "INVALID":
            invalid += 1

        else:
            errors += 1

        current_date += timedelta(days=1)

        time.sleep(0.2)

    # ==================================================
    # FINAL SUMMARY
    # ==================================================

    print()
    print("=" * 60)
    print("NBC HISTORICAL DOWNLOAD COMPLETED")
    print("=" * 60)

    print("Total dates checked :", total)
    print("Successfully saved  :", success)
    print("Already existed     :", exists)
    print("Not available       :", not_found)
    print("Rate extraction fail:", rate_errors)
    print("Invalid PDF         :", invalid)
    print("Request errors      :", errors)

    print("=" * 60)

    print("PDF LOCATION:")
    print(BASE_FOLDER)

    print()

    print("TXT LOCATION:")
    print(os.path.join(BASE_FOLDER, "txt"))

    print("=" * 60)
