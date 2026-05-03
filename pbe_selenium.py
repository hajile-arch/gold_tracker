from selenium import webdriver
import re
from selenium.webdriver.common.by import By
import time

with webdriver.Chrome() as driver:
    driver.get("https://www.pbebank.com/en/invest/gold-egold-investment-account/")

    driver.implicitly_wait(8)
    
    sellingelem=driver.find_element(By.XPATH,"//td[contains(text(), '1 gram')]/following-sibling::td[1]").get_attribute("textContent").strip()
    buyingelem=driver.find_element(By.XPATH,"//td[contains(text(), '1 gram')]/following-sibling::td[2]").get_attribute("textContent").strip()
    
    # 2. Use "textContent" to grab the numbers even if the accordion is closed
    # We also add .strip() to remove any invisible extra spacing or line breaks
    # sell_price=sellingelem.get_attribute("textContent").strip()
    # buy_price=buyingelem.get_attribute("textContent").strip()
    
    print(sellingelem + buyingelem)
        
    
