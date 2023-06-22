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
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((By.ID, "__tile0-__container1-2"))
)
find(By.ID, "__tile0-__container1-2").click()  # CLICK ON OVS REPORT FAV TILE
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']"))
)
find(css, "[title*='Reset prompts values to default']").click()  # CLICK RESET
find(css, "[id*='promptsList-0']").click()  # CLICK PLANT PROMT
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
        crNew_path = os.path.join(DLOADS_PATH, crNew)
        wait = False
# SIMPLIFY THE CSV FILE AND SAVE IT AS A HD5 FILE.
time.sleep(3)
crNew_path = f"../../{os.path.basename(crNew_path)}"
with zipfile.ZipFile(crNew_path) as zf:
    df = pd.read_csv(zf.open("OVS Purchase Order Report.csv"))
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int16)
df.to_pickle("../PKL/OVS_RAW.PKL")
import sqlalchemy

cn = sqlalchemy.create_engine(
    "mysql+pymysql://anveshjarabani:Zintak1!@mysql12--2.mysql.database.azure.com:3306/uct_data",
    connect_args={"ssl_ca": "DigiCertGlobalRootCA.crt.pem"},
)
df.replace([np.inf, -np.inf], np.nan, inplace=True)
cn.execute("DROP TABLE IF EXISTS OVS_RAW")
df.to_sql(name="OVS_RAW", con=cn, if_exists="replace", index=False)
print("OVS_RAW.PKL COMPLETE")
os.remove(crNew)
# BUILD H5 FILE
exec(open("OVS CALC.py").read())
