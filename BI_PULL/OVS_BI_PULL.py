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
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((By.ID, "__tile0-__container1-2"))
)

# CLICK ON OVS REPORT FAV TILE
lst = find(css, "div[id*='Favourite']").find_elements(tag, "bdi")
[i for i in lst if "OVS Purchase Order" in i.text][0].click()
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']"))
)
find(css, "[title*='Reset prompts values to default']").click()  # CLICK RESET
prompts_list = find(css, 'div[class*="PromptsSummaryList"]')
prompts = prompts_list.find_elements(tag, "span")
[i for i in prompts if "Plant" in i.text][0].click()  # CLICK PLANT PROMT
time.sleep(0.5)
find(css, "[title*='Show the settings page']").click()  # SELECT SETTINGS
time.sleep(1)
find(css, "[class*='SettingsSearchByKeys']").click()  # TURN ON KEY SEARCH
find(css, "[class*='SettingsShowKeys']").click()  # TURN ON KEY SEARCH
find(css, "[id*='search-I']").send_keys("3322")
find(css, "[title*='Add']").click()  # CLICK PLUS
find(
    css, "[title*='Refresh the document using the prompts values']"
).click()  # CLICK Run
WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((css, "[title*='Zoom']")))
# ----RUN THE REPORT WITH CSV
find(css, "[title*='Export']").click()  # CLICK EXPORT
time.sleep(1)
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
    df = pd.read_csv(zf.open("OVS Purchase Order Report.csv"))
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int16)
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.to_pickle("../PKL/OVS_RAW.PKL")
print("OVS_RAW.PKL COMPLETE")
os.remove(crNew)
from BI_TO_DB import load_to_db

load_to_db("../PKL/OVS_RAW.PKL")
# BUILD H5 ETL FILE
exec(open("../DATA ETLS/OVS CALC.py").read())
