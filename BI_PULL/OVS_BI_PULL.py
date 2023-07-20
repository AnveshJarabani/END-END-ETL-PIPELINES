from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import time,os,json
chromeOptions = webdriver.ChromeOptions()
today = datetime.today().strftime("%m/%d/%y")
START_DATE = (datetime.today() + delt.relativedelta(months=-18)).strftime("%m/%d/%y")
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("http://alinbop.uct.local/BOE/BI")
find = driver.find_element
finds = driver.find_elements
tag = By.TAG_NAME
css = By.CSS_SELECTOR
driver.switch_to.frame(find(By.TAG_NAME, "iframe"))
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__label0-bdi")))
username = find(By.ID, "__input3-inner")
password = find(By.ID, "__input4-inner")
keys = json.load(open("../PRIVATE/encrypt.json", "r"))
username.send_keys(keys["BI_USER"])
password.send_keys(keys["BI_PASS"])
find(By.ID, "__button1-inner").click()
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__tile0-__container1-2")))
# CLICK ON OVS REPORT FAV TILE
lst = find(css, "div[id*='Favourite']").find_elements(tag, "bdi")
[i for i in lst if "OVS_BI_PULL" in i.text][0].click()  
WebDriverWait(driver, 25).until(EC.presence_of_element_located((css, "[id*='promptsList']")))
find(css, "[title*='Refresh the document using the prompts values']").click()  # CLICK Run
WebDriverWait(driver, 10000).until(EC.presence_of_element_located((tag, "table")))
# WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((css, "[title*='Zoom']")))
find(css, "[title*='Export']").click()  # CLICK EXPORT
time.sleep(1)
# DOWNLOAD TXT BY DATA ONLY.
find(css, "[data-customclass*='TXTExportEntry']").click()
find(css, "[id*='ConfirmExportButton']").click()
while not os.path.exists("../../OVS_BI_PULL.txt"): time.sleep(1)
df=pd.read_csv("../../OVS_BI_PULL.txt",delimiter="\t")
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int16)
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.to_pickle("../PKL/OVS_RAW.PKL")
print("OVS_RAW.PKL COMPLETE")
os.remove("../../OVS_BI_PULL.txt")
# BUILD H5 ETL FILE
exec(open("../DATA ETLS/OVS CALC.py").read())