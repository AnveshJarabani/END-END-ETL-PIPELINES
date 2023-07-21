from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import time, os, json

chromeOptions = webdriver.ChromeOptions()
today = datetime.today().strftime("%m/%d/%y")
START_DATE = (datetime.today() + delt.relativedelta(months=-18)).strftime("%m/%d/%y")
mtime=os.path.getmtime("../PKL/RAW_LBR.pkl")
# START_DATE=datetime.fromtimestamp(mtime).strftime("%m/%d/%y")
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("http://alinbop.uct.local/BOE/BI")
find = driver.find_element
finds = driver.find_elements
tag=By.TAG_NAME
css = By.CSS_SELECTOR
driver.switch_to.frame(find(By.TAG_NAME, "iframe"))
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__label0-bdi")))
username = find(By.ID, "__input3-inner")
password = find(By.ID, "__input4-inner")
keys = json.load(open("../PRIVATE/encrypt.json", "r"))
username.send_keys(keys["BI_USER"])
password.send_keys(keys["BI_PASS"])
find(By.ID, "__button1-inner").click()
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__vbox5")))
 # CLICK ON EMPLOYEE LABOR HRS REPORT FAV TILE
lst = find(css, "div[id*='Favourite']").find_elements(tag, "bdi")
[i for i in lst if "LBR_BI_PULL" in i.text][0].click()
WebDriverWait(driver, 25).until(EC.presence_of_element_located((css, "[id*='promptsList']")))
time.sleep(1)
# FOR DATES ENTRY -----
find(css, "[id*='promptsList-5']").click()  # DAY INTERVAL PROMPT
WebDriverWait(driver, 25).until(EC.presence_of_element_located((css, "[id*='rangeInputLow-inner']")))
find(css, "[title*='Reset prompt values']").click()  # CLICK RESET
find(css, "[id*='rangeInputLow-inner']").send_keys(START_DATE)  # START DATE
find(css, "[id*='rangeInputHigh-inner']").send_keys(today)  # CURRENT DATE
find(css, "[title*='Refresh the document']").click()  # CLICK RUN
WebDriverWait(driver, 10000).until(EC.presence_of_element_located((tag, "table")))
# GO TO EXPORT TAB
find(css, "[title='Export']").click()
time.sleep(3)
# DOWNLOAD TXT BY DATA ONLY.
find(css, "[data-customclass*='TXTExportEntry']").click()
time.sleep(1)
find(css, "[id*='ConfirmExportButton']").click()
# WAIT TILL THE FILE IS DOWNLOADED
while not os.path.exists("../../LBR_BI_PULL.txt"): time.sleep(1)
df=pd.read_csv("../../LBR_BI_PULL.txt",delimiter='\t')
df = df.loc[df.iloc[:, 0].notna()]
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int8)
# old_df=pd.read_pickle("../PKL/RAW_LBR.PKL")
# old_df=old_df.loc[old_df['END_DATE']!=START_DATE]
# df=df[old_df.columns]
# new_df=pd.concat([old_df,df],ignore_index=True)
# new_df['END_DATE']=pd.to_datetime(new_df['END_DATE'])
df.to_pickle("../PKL/RAW_LBR.PKL")
os.remove("../../LBR_BI_PULL.txt")
print("RAW_LBR.PKL COMPLETE")
# BUILD FOLLOWUP PICKLE FILES
driver.close()
exec(open("../DATA ETLS/ACT VS PLN LBR CST.py").read())
exec(open("../DATA ETLS/LBR HR WO TRENDS.py").read())
exec(open("../DATA ETLS/PROCESS DAYS.py").read())
exec(open("../DATA ETLS/LBR QLY COSTS.py").read())
exec(open("../DATA ETLS/WC LOAD HRS.py").read())

