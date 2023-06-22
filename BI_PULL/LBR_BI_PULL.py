from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import zipfile, time, glob, os

chromeOptions = webdriver.ChromeOptions()
today = datetime.today().strftime("%m/%d/%y")
START_DATE = (datetime.today() + delt.relativedelta(months=-18)).strftime("%m/%d/%y")
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
find(
    By.ID, "__tile0-__container1-0"
).click()  # CLICK ON EMPLOYEE LABOR HRS REPORT FAV TILE
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']"))
)


find(css, "[id*='promptsList-4']").click()  # TICKET TYPE PROMPT
find(css, "[title*='Show the settings page']").click()  # SELECT SETTINGS
time.sleep(1)
find(css, "[title*='Show the settings page']").click()
find(css, "[class*='SettingsSearchByKeys']").click()  # TURN ON KEY SEARCH
find(css, "[class*='SettingsShowKeys']").click()  # TURN ON KEY SEARCH
find(css, "[title*='Refresh']").click()  # REFRESH
find(css, "[id*='search-I']").send_keys("L")
find(css, "[title*='Add']").click()  # CLICK PLUS
find(css, "[id*='search-I']").send_keys("S")
find(css, "[title='Add']").click()  # CLICK PLUS
find(css, "[id*='promptsList-0']").click()  # CLICK PLANT PROMT
find(css, "[title*='Reset prompts']").click()  # CLICK RESET
find(css, "[id*='search-I']").send_keys("3322")
find(css, "[title*='Add']").click()  # CLICK PLUS
find(css, "[id*='search-I']").send_keys("3321")
find(css, "[title='Add']").click()  # CLICK PLUS
time.sleep(1)
# FOR DATES ENTRY -----
find(css, "[id*='promptsList-5']").click()  # DAY INTERVAL PROMPT
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='rangeInputLow-inner']"))
)
find(css, "[id*='rangeInputLow-inner']").send_keys(START_DATE)  # START DATE
find(css, "[id*='rangeInputHigh-inner']").send_keys(today)  # CURRENT DATE
find(css, "[title*='Refresh the document']").click()  # CLICK RUN
WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((css, "[title*='Zoom']")))
# GO TO EXPORT TAB
find(css, "[title='Export']").click()
time.sleep(3)
# DOWNLOAD CSV BY DATA ONLY.
find(css, "[data-customclass*='CSVExportEntry']").click()
find(css, "[placeholder='Search']").send_keys("Labor Hours")
find(css, "[class='sapMTableTH sapMListTblSelCol']").click()  # CLICK ALL
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
        crNew_path = os.path.join(DLOADS_PATH, crNew)
        wait = False
# SIMPLIFY THE CSV FILE AND SAVE IT AS A PICIKLE FILE.
# crNew_path='C:\\Users\\ajarabani\\Downloads\\Employee Labor Hours Report_P2M018.zip'
with zipfile.ZipFile(crNew_path, "r") as zf:
    zf = zipfile.ZipFile(crNew)
    df = pd.read_csv(zf.open("Employee Labor Hours.csv"))
df = df.loc[df.iloc[:, 0].notna()]
df.replace(",", "", regex=True, inplace=True)
df["Operation Quantity"] = df["Operation Quantity"].astype(float)
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int8)
df.to_pickle("../PKL/LBR M-18.pkl")
os.remove(crNew)
print("LBR M-18.PKL COMPLETE")
# BUILD FOLLOWUP PICKLE FILES
exec(open("ACT VS PLN LBR CST.py").read())
exec(open("LBR HR WO TRENDS.py").read())
exec(open("PROCESS DAYS.py").read())
exec(open("LBR QLY COSTS.py").read())
exec(open("WC LOAD HRS.py").read())
driver.close()
