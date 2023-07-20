from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import time, glob, os, zipfile, json

chromeOptions = webdriver.ChromeOptions()
dict = {
    1: "01",
    2: "01",
    3: "01",
    4: "02",
    5: "02",
    6: "02",
    7: "03",
    8: "03",
    9: "03",
    10: "04",
    11: "04",
    12: "04",
}
QS = []
for i in range(0, 6):
    dt = datetime.now() + delt.relativedelta(months=-3 * i)
    QS.append(dict[dt.month] + str(dt.year))
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("http://alinbop.uct.local/BOE/BI")
find = driver.find_element
finds = driver.find_elements
css = By.CSS_SELECTOR
tag = By.TAG_NAME
driver.switch_to.frame(find(tag, "iframe"))
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__label0-bdi")))
username = find(By.ID, "__input3-inner")
password = find(By.ID, "__input4-inner")
keys = json.load(open("../PRIVATE/encrypt.json", "r"))
username.send_keys(keys["BI_USER"])
password.send_keys(keys["BI_PASS"])
find(By.ID, "__button1-inner").click()
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__vbox5")))
# CLICK ON SHIPMENT REPORT FAV TILE
lst = find(css, "div[id*='Favourite']").find_elements(tag, "bdi")
[i for i in lst if "SHP_BI_PULL" in i.text][0].click()
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']"))
)
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
find(css, "[title='Export']").click()
time.sleep(2)
# DOWNLOAD CSV BY DATA ONLY.
find(css, "[data-customclass*='CSVExportEntry']").click()
find(css, "[id*='ConfirmExportButton']").click()
# WAIT TILL THE FILE IS DOWNLOADED
wait = True
DLOADS_PATH = "../../*zip"
files = glob.iglob(DLOADS_PATH)
cr1 = max(files, key=os.path.getmtime)
while wait:
    files = glob.iglob(DLOADS_PATH)
    crNew = max(files, key=os.path.getmtime)
    if crNew == cr1:
        time.sleep(1)
    else:
        crNew_path = crNew
        wait = False
# SIMPLIFY THE CSV FILE AND SAVE IT AS A HD5 FILE.
time.sleep(3)
with zipfile.ZipFile(crNew_path) as zf:
    df = pd.read_csv(zf.open("Shipment Report.csv"))
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int16)
df["SHIPPED_DATE"] = pd.to_datetime(df["SHIPPED_DATE"])
df["SHIPPED_QTY"] = (
    df["SHIPPED_QTY"].str.replace("\$|\,", "", regex=True).astype(float)
)
# df["ASP"] = df["ASP"].str.replace("\$|\,", "", regex=True).astype(float)
df.dropna()
df.to_pickle("../PKL/SHP.pkl")
driver.close()
print("SHP.pkl COMPLETE")
os.remove(crNew)
from BI_TO_DB import load_to_db

load_to_db("../PKL/SHP.pkl")
