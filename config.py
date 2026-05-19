import urllib3

UOB_URL = "https://www.uob.com.my/wsm/stayinformed.do?path=gia"
CIMB_URL = "https://www.cimb.com.my/en/personal/wealth-management/investments/investment-products/e-gold-investment-account-egia.html"
MAY_URL = "https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page"
PBE_URL = "https://www.pbebank.com/en/invest/gold-egold-investment-account/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
    "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/"
}

CACHE_TTL = 900  # 15 minutes in seconds

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)