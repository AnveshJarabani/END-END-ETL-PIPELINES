from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import zipfile
import time
import glob
import os, json

chromeOptions = webdriver.ChromeOptions()
today = datetime.today().strftime("%m/%d/%y")
START_DATE = (datetime.today() + delt.relativedelta(months=-18)).strftime("%m/%d/%y")
driver = webdriver.Chrome()
driver.maximize_window()
find = driver.find_element
finds = driver.find_elements
css = By.CSS_SELECTOR
tag = By.TAG_NAME
located = EC.presence_of_element_located
clickable = EC.element_to_be_clickable
driver.get("http://alinbop.uct.local/BOE/BI")
driver.switch_to.frame(find(By.TAG_NAME, "iframe"))
WebDriverWait(driver, 25).until(located((By.ID, "__label0-bdi")))
username = find(By.ID, "__input3-inner")
password = find(By.ID, "__input4-inner")
keys = json.load(open("../PRIVATE/encrypt.json", "r"))
username.send_keys(keys["BI_USER"])
password.send_keys(keys["BI_PASS"])
find(By.ID, "__button1-inner").click()
WebDriverWait(driver, 25).until(located((By.ID, "__vbox5")))
# CLICK ON NOTIFICATION ANALYSIS FAV TILE
lst = find(css, "div[id*='Favourite']").find_elements(tag, "bdi")
[i for i in lst if "Notification Analysis" in i.text][0].click()
WebDriverWait(driver, 25).until(located((css, "[id*='promptsList']")))
prompts_list = find(css, 'div[class*="PromptsSummaryList"]')
prompts = prompts_list.find_elements(tag, "span")
# CLICK PLANT PROMT
[i for i in prompts if "Plant" in i.text][0].click()
#  ------------------------- ADD PLANTS TO PROMPT LIST -------------------------
find(css, "[title*='Reset prompts']").click()  # CLICK RESET
find(css, "[id*='search-I']").send_keys("3322")
find(css, "[title*='Add']").click()  # CLICK PLUS
find(css, "[id*='search-I']").send_keys("3321")
find(css, "[title='Add']").click()  # CLICK PLUS
time.sleep(1)
# FOR DATES ENTRY ----- DAY INTERVAL PROMPT
[i for i in prompts if "Day Interval" in i.text][0].click()
WebDriverWait(driver, 25).until(located((css, "[id*='rangeInputLow-inner']")))
find(css, "[id*='rangeInputLow-inner']").send_keys(START_DATE)  # START DATE
find(css, "[id*='rangeInputHigh-inner']").send_keys(today)  # CURRENT DATE
find(css, "[title*='Refresh the document']").click()  # CLICK RUN
WebDriverWait(driver, 10000).until(clickable((css, "[title*='Zoom']")))
# GO TO EXPORT TAB
find(css, "[title='Export']").click()
time.sleep(3)
# DOWNLOAD CSV BY DATA ONLY.
find(css, "[data-customclass*='CSVExportEntry']").click()
find(css, "[id*='ConfirmExportButton']").click()
# WAIT TILL THE FILE IS DOWNLOADED
while not os.path.exists("../../QN_BI_PULL.txt"): time.sleep(1)
df=pd.read_csv("../../QN_BI_PULL.txt",delimiter='\t')
df = df.loc[df.iloc[:, 0].notna()]
df.replace(",", "", regex=True, inplace=True)
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int8)
df["Required Start Date"] = pd.to_datetime(df["Required Start Date"])
df.to_pickle("../PKL/QN M-18.pkl")
os.remove("../../QN_BI_PULL.txt")
print("QN M-18.PKL COMPLETE")
