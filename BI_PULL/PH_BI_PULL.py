from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import  time, os, json
dict = {1: "01",2: "01",3: "01",4: "02",
        5: "02",6: "02",7: "03",8: "03",
        9: "03",10: "04",11: "04",12: "04",}
QS = []
for i in range(0, 6):
    dt = datetime.now() + delt.relativedelta(months=-3 * i)
    QS.append(dict[dt.month] + str(dt.year))
dt = datetime.now()
QS.append(dict[dt.month] + str(dt.year))
start_time = time.time()
chromeOptions = webdriver.ChromeOptions()
today = datetime.today().strftime("%m/%d/%y")
START_DATE = (datetime.today() + delt.relativedelta(months=-18)).strftime("%m/%d/%y")
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("http://alinbop.uct.local/BOE/BI")
find = driver.find_element
finds = driver.find_elements
css = By.CSS_SELECTOR
tag = By.TAG_NAME
driver.switch_to.frame(find(By.TAG_NAME, "iframe"))
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__label0-bdi")))
keys = json.load(open("../PRIVATE/encrypt.json", "r"))
find(css, "[placeholder='User Name']").send_keys(keys["BI_USER"])
find(css, "[placeholder='Password']").send_keys(keys["BI_PASS"])
find(css, "[class*='LoginButton']").click()
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__tile0-__container1-2")))
# CLICK ON PURCHASE HIST REPORT FAV TILE
lst = find(css, "div[id*='Favourite']").find_elements(tag, "bdi")
[i for i in lst if "PH_BI_PULL" in i.text][0].click()
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']")))
prompts_list = find(css, 'div[class*="PromptsSummaryList"]')
prompts = prompts_list.find_elements(tag, "span")
[i for i in prompts if "Fiscal Quarter" in i.text][0].click()  # FISCAL QUARTER PROMPT
find(css, "[title*='Reset prompt values']").click()  # CLICK RESET
for i in QS:
    find(css, "[id*='search-I']").send_keys(i)
    time.sleep(0.5)
    find(css, "[title*='Add']").click()  # CLICK PLUS
find(css, "[title*='Refresh the document']").click()  # CLICK RUN
WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((css, "[title*='Zoom']")))
# GO TO EXPORT TAB
find(css, "[title*='Export']").click()  # CLICK EXPORT
time.sleep(3)
# SELECT SUMMARY AND DETAILS AND CLICK EXPORT
find(css, "[data-customclass*='TXTExportEntry']").click()
# DOWNLOAD CSV
find(css, "[id*='ConfirmExportButton']").click()
# WAIT TILL THE FILE IS DOWNLOADED
wait = True
while not os.path.exists("../../PH_BI_PULL.txt"): time.sleep(1)
df=pd.read_csv("../../PH_BI_PULL.txt",delimiter="\t")
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int16)
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.to_pickle("../PKL/PH.PKL")
print("PH.H5 Q COMPLETE")
os.remove('../../PH_BI_PULL.txt')
# BUILD FOLLOWUP PICKLE FILES
import subprocess
subprocess.run(["python", "../DATA ETLS/PH CALC.py"])

