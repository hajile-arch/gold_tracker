from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import schedule
import time
import os


app = Flask(__name__)

uob_url = "https://www.uob.com.my/wsm/stayinformed.do?path=gia"
cimb_url = "https://www.cimb.com.my/en/personal/wealth-management/investments/investment-products/e-gold-investment-account-egia.html"
may_url = "https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page"

headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0", "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Connection": "keep-alive" }


def fetch_prices():
    try:
        session = requests.Session()

        uob_response = session.get(uob_url, timeout=5)
        cimb_response = session.get(cimb_url, timeout=5)
        may_response = session.get(may_url, headers=headers, timeout=10)

        soup_cimb = BeautifulSoup(cimb_response.text, "html.parser")
        soup_may = BeautifulSoup(may_response.text, "html.parser")

        # ---------------- CIMB ----------------
        time_cimb = soup_cimb.find(string=lambda t: t and "Last Updated" in t)
        selling_cimb = buying_cimb = None

        tables = soup_cimb.find_all("table")
        for table in tables:
            for row in table.find_all("tr"):
                cols = [c.text.strip() for c in row.find_all(["td", "th"])]
                if len(cols) == 3 and cols[0] == "CIMB Clicks":
                    selling_cimb = float(cols[1])
                    buying_cimb = float(cols[2])

        # ---------------- UOB ----------------
        selling_uob = buying_uob = None
        time_uob = None

        for line in uob_response.text.split("\n"):
            columns = line.split(",")
            
            if columns[0] == "GOLD SAVINGS ACCOUNT" :
                selling_uob = float(columns[2])
                buying_uob = float(columns[3])
                time_uob = columns[5]

        # ---------------- Maybank ----------------
        time_may = soup_may.find(string=lambda t: t and "Effective on" in t)
        selling_may = buying_may = None

        tables = soup_may.find_all("table")
        if tables:
            td_rows = tables[0].find_all("td")
            if len(td_rows) >= 3:
                selling_may = float(td_rows[1].text.strip())
                buying_may = float(td_rows[2].text.strip())

        # ---------------- STANDARDIZED OUTPUT ----------------
        gold_prices = {
            "CIMB": {
                "selling": selling_cimb,
                "buying": buying_cimb,
                "time": time_cimb
            },
            "UOB": {
                "selling": selling_uob,
                "buying": buying_uob,
                "time": time_uob
            },
            "Maybank": {
                "selling": selling_may,
                "buying": buying_may,
                "time": time_may
            }
        }

        print("\n================ GOLD PRICE DASHBOARD ================")

        for bank, data in gold_prices.items():
            print(f"\n--- {bank} ---")
            print("Last Updated:", data["time"])
            print("Selling:", data["selling"])
            print("Buying:", data["buying"])

        # ---------------- COMPARISON ----------------
        valid_data = {k: v for k, v in gold_prices.items() if v["selling"] and v["buying"]}

        if valid_data:
            best_buy = min(valid_data.items(), key=lambda x: x[1]["selling"])
            best_sell = max(valid_data.items(), key=lambda x: x[1]["buying"])

            print("\n================ ANALYSIS ================")
            print(f"Best place to BUY gold  : {best_buy[0]} (RM {best_buy[1]['selling']})")
            print(f"Best place to SELL gold : {best_sell[0]} (RM {best_sell[1]['buying']})")

        print("\n=====================================================\n")
        return gold_prices
    except Exception as e:
        print("Error:", e)
        return{} 
        # By returning an empty dict when got error doesnt crash the API


@app.route("/")
def gold():
    data=fetch_prices()
    valid = {k: v for k, v in data.items() if v["selling"] and v["buying"]}

    if valid:
        best_buy = min(valid.items(), key=lambda x: x[1]["selling"])
        best_sell = max(valid.items(), key=lambda x: x[1]["buying"])

        return jsonify({
            "prices": data,
            "analysis": {
                "best_buy": best_buy[0],
                "best_sell": best_sell[0]
            }
        })

    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
# ---------------- SCHEDULER ----------------
# schedule.every(10).minutes.do(fetch_prices)

# # Run once immediately
# fetch_prices()

# # Keep running
# while True:
#     schedule.run_pending()
#     time.sleep(1)