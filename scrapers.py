import time
import re
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from config import UOB_URL, CIMB_URL, MAY_URL, PBE_URL, RHB_URL, HSBC_URL,HEADERS


def clean_time(t):
    if not t:
        return "N/A"
    return re.sub(r'<[^>]+>', '', str(t)).strip()


def safe_request(session, url):
    try:
        return session.get(url, headers=HEADERS, timeout=8)
    except Exception as e:
        print(f"[ERROR] Request failed for {url}: {e}")
        return None


def safe_request_proxy(url, max_retries=3):
    api_key = os.environ.get("SCRAPER_API_KEY")
    if not api_key:
        print("[ERROR] SCRAPER_API_KEY is not set")
        return None

    proxy_url = "http://{}:@proxy.scrape.do:8080".format(api_key)
    proxies = {"http": proxy_url, "https": proxy_url}

    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] Fetching Maybank (Attempt {attempt + 1}/{max_retries})...")
            response = requests.get(url, headers=HEADERS, proxies=proxies, verify=False, timeout=40)

            if response.status_code == 200:
                # Validate the response actually has a table
                soup = BeautifulSoup(response.text, "html.parser")
                tables = soup.find_all("table")
                if len(tables) > 0:
                    print(f"[DEBUG] Maybank valid response with {len(tables)} tables")
                    return response
                else:
                    print(f"[WARNING] Maybank returned 200 but no tables found, retrying...")
            else:
                print(f"[WARNING] Maybank returned status {response.status_code}")

        except requests.exceptions.ReadTimeout:
            print(f"[WARNING] Maybank attempt {attempt + 1} timed out.")
        except Exception as e:
            print(f"[ERROR] Maybank attempt {attempt + 1} failed: {e}")

        if attempt < max_retries - 1:
            time.sleep(2)

    print("[ERROR] All Maybank proxy attempts failed. Serving 'N/A' for now.")
    return None


def scrape_cimb(session):
    result = {"selling": None, "buying": None, "time": "N/A"}
    try:
        res = safe_request(session, CIMB_URL)
        if res:
            soup = BeautifulSoup(res.text, "html.parser")
            time_cimb = soup.find(string=lambda t: t and "Last Updated" in t)
            for table in soup.find_all("table"):
                for row in table.find_all("tr"):
                    cols = [c.text.strip() for c in row.find_all(["td", "th"])]
                    if len(cols) == 3 and cols[0] == "CIMB Clicks":
                        result["selling"] = float(cols[1])
                        result["buying"] = float(cols[2])
            if time_cimb:
                result["time"] = time_cimb.strip().replace("Last Updated:", "Effetive On").strip()
    except Exception as e:
        print("[ERROR] CIMB parsing failed:", e)
    return result


def scrape_uob(session):
    result = {"selling": None, "buying": None, "time": "N/A"}
    try:
        res = safe_request(session, UOB_URL)
        if res:
            for line in res.text.split("\n"):
                cols = line.split(",")
                if cols[0] == "GOLD SAVINGS ACCOUNT":
                    result["selling"] = float(cols[2])
                    result["buying"] = float(cols[3])
                    result["time"] = "Effective On " + cols[5].strip()
    except Exception as e:
        print("[ERROR] UOB parsing failed:", e)
    return result


def scrape_maybank():
    result = {"selling": None, "buying": None, "time": "N/A"}
    try:
        res = safe_request_proxy(MAY_URL)
        if res:
            print("[DEBUG] Maybank status:", res.status_code)
            soup = BeautifulSoup(res.text, "html.parser")
            time_may = soup.find(string=lambda t: t and "Effective on" in t)
            tables = soup.find_all("table")
            print(f"[DEBUG] Maybank tables found: {len(tables)}")
            if tables:
                td = tables[0].find_all("td")
                print(f"[DEBUG] Maybank td count: {len(td)}")
                print(f"[DEBUG] Maybank td values: {[t.text.strip() for t in td[:5]]}")
                if len(td) >= 3:
                    result["selling"] = float(td[1].text.strip())
                    result["buying"] = float(td[2].text.strip())
            if time_may:
                result["time"] = clean_time(str(time_may))
    except Exception as e:
        print("[ERROR] Maybank parsing failed:", e)
    return result


def scrape_pbe():
    result = {"selling": None, "buying": None, "time": "N/A"}
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        with webdriver.Chrome(options=chrome_options) as driver:
            driver.get(PBE_URL)
            driver.implicitly_wait(10)

            selling_text = driver.find_element(By.XPATH, "//td[contains(text(), '1 gram')]/following-sibling::td[1]").get_attribute("textContent").strip()
            buying_text = driver.find_element(By.XPATH, "//td[contains(text(), '1 gram')]/following-sibling::td[2]").get_attribute("textContent").strip()
            time_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Gold Investment Account as at')]").get_attribute("textContent").strip()

            print("[DEBUG] PBe time_element raw:", repr(time_element))

            result["selling"] = float(selling_text)
            result["buying"] = float(buying_text)
            result["time"] = time_element.strip().replace("Gold Investment Account as at", "Effective On").strip()

            print("[DEBUG] PBe full result:", result)
    except Exception as e:
        print(f"[ERROR] PBe parsing failed: {e}")
    return result

def scrape_rhb(session):
    result = {"selling": None, "buying": None, "time": "N/A"}
    try:
        res = safe_request(session, RHB_URL)
        if res:
            soup = BeautifulSoup(res.text, "html.parser")
            time_rhb = soup.find(string=lambda t: t and "RATES ARE QUOTED AGAINST MALAYSIAN RINGGIT UPDATED" in t)
            for table in soup.find_all("table"):
                for row in table.find_all("tr"):
                    cols = [c.text.strip() for c in row.find_all(["td", "th"])]
                    if len(cols) == 5 and cols[0] == "GLD":
                        result["selling"] = float(cols[3])
                        result["buying"] = float(cols[4])
            if time_rhb:
                result["time"] = time_rhb.strip().replace("RATES ARE QUOTED AGAINST MALAYSIAN RINGGIT UPDATED AT", "Effective At").strip()
    except Exception as e:
        print("[ERROR] RHB parsing failed:", e)
    return result

def scrape_hsbc(session):
    result = {"selling": None, "buying": None, "time": "N/A"}
    try:
        res = safe_request(session, HSBC_URL)
        if res:
            soup = BeautifulSoup(res.text, "html.parser")
            time_hsbc = soup.find(string=lambda t: t and "Exchange Rates updated as at" in t)
            for table in soup.find_all("table"):
                for row in table.find_all("tr"):
                    cols = [c.text.strip() for c in row.find_all(["td", "th"])]
                    if len(cols) == 4 and cols[0] == "GLD":
                        original_sell = float(cols[2])
                        original_buy = float(cols[3])
                        result["selling"] = round(float(cols[2]) / 3.11035, 2)
                        result["buying"] = round(float(cols[3]) / 3.11035, 2)
                        result["original_selling"] = original_sell
                        result["original_buying"] = original_buy
                        result["unit"] = "0.10 troy oz"
            if time_hsbc:
                result["time"] = time_hsbc.strip().replace("Exchange Rates updated as at", "Effective On").strip()
    except Exception as e:
        print("[ERROR] HSBC parsing failed:", e)
    return result

def fetch_prices():
    print("[DEBUG] fetch_prices() called!")
    session = requests.Session()

    gold_prices = {
        "CIMB": scrape_cimb(session),
        "UOB": scrape_uob(session),
        "Maybank": scrape_maybank(),
        "Pbe": scrape_pbe(),
        "RHB": scrape_rhb(session),
        "HSBC": scrape_hsbc(session)
    }

    return gold_prices
