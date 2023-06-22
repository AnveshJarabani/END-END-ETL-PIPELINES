from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import time, glob, os, zipfile

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
driver.switch_to.frame(find(By.TAG_NAME, "iframe"))
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__label0-bdi")))
username = find(By.ID, "__input3-inner")
password = find(By.ID, "__input4-inner")
username.send_keys("ajarabani")
password.send_keys("Xuiqil9`")
find(By.ID, "__button1-inner").click()
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__vbox5")))
find(By.ID, "__tile0-__container1-4").click()  # CLICK ON SHIPMENT REPORT FAV TILE
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']"))
)
find(css, "[title*='Reset prompts values to default']").click()  # CLICK RESET
find(css, "[id*='promptsList-0']").click()  # CLICK PLANT PROMT
time.sleep(0.5)
# -----------SELECT PLANT
find(css, "[title*='Show the settings page']").click()  # SELECT SETTINGS
time.sleep(1)
find(css, "[class*='SettingsSearchByKeys']").click()  # TURN ON KEY SEARCH
find(css, "[class*='SettingsShowKeys']").click()  # TURN ON KEY SEARCH
find(css, "[title*='Reset prompt values']").click()  # CLICK RESET
find(css, "[id*='search-I']").send_keys("3322")
find(css, "[title*='Add']").click()  # CLICK PLUS
find(css, "[id*='search-I']").send_keys("3321")
find(css, "[title='Add']").click()  # CLICK PLUS
find(css, "[id*='promptsList-3']").click()  # FISCAL QUARTER PROMPT
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
find(css, "[aria-label='Select all rows']").click()
find(css, "[id*='ConfirmExportButton']").click()
# WAIT TILL THE FILE IS DOWNLOADED
wait = True
DLOADS_PATH = "../*zip"
files = glob.iglob(DLOADS_PATH)
cr1 = max(files, key=os.path.getmtime)
while wait:
    files = glob.iglob(DLOADS_PATH)
    crNew = max(files, key=os.path.getmtime)
    if crNew == cr1:
        time.sleep(1)
    else:
        crNew_path = os.path.join(DLOADS_PATH, crNew)
        wait = False
# SIMPLIFY THE CSV FILE AND SAVE IT AS A HD5 FILE.
time.sleep(3)
crNew_path = f"../../{os.path.basename(crNew_path)}"
with zipfile.ZipFile(crNew_path) as zf:
    df = pd.read_csv(zf.open("Shipment Report.csv"))
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int16)
df["Actual Good Issue Date"] = pd.to_datetime(df["Actual Good Issue Date"])
df["Act Shipped Qty"] = df["Act Shipped Qty"].str.replace("\$|\,", "").astype(float)
df["ASP"] = df["ASP"].str.replace("\$|\,", "").astype(float)
df.dropna()
df.to_pickle("../PKL/SHP.pkl")
print("SHP.pkl COMPLETE")
os.remove(crNew)
