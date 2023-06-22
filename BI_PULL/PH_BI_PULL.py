from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import zipfile, time, glob, os

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
driver.switch_to.frame(find(By.TAG_NAME, "iframe"))
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__label0-bdi")))
find(css, "[placeholder='User Name']").send_keys("ajarabani")
find(css, "[placeholder='Password']").send_keys("Xuiqil9`")
find(css, "[class*='LoginButton']").click()
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((By.ID, "__tile0-__container1-2"))
)
find(By.ID, "__tile0-__container1-3").click()  # CLICK ON PURCHASE HIST REPORT FAV TILE
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']"))
)
for i in QS:
    if i != QS[0]:
        find(css, "[title='Refresh']").click()  # CLICK REFRESH
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((css, "[id*='promptsList']"))
        )
    # FOR PLANT SELECTION - CHANDLER FAB & INTEGRATION , SELECTING KEYS
    if i == QS[0]:
        find(css, "[title*='Reset prompts']").click()  # CLICK RESET
        # find(css,"[id*='promptsList-5']").click() # CLICK PLANT PROMT
        find(css, "[title*='Show the settings page']").click()  # SELECT SETTINGS
        time.sleep(1)
        find(css, "[class*='SettingsSearchByKeys']").click()  # TURN ON KEY SEARCH
        find(css, "[class*='SettingsShowKeys']").click()  # TURN ON KEY SEARCH
        find(css, "[id*='search-I']").send_keys("3322")
        find(css, "[title*='Add']").click()  # CLICK PLUS
        find(css, "[id*='search-I']").send_keys("3321")
        find(css, "[title='Add']").click()  # CLICK PLUS
    find(css, "[id*='promptsList-3']").click()  # FISCAL QUARTER PROMPT
    find(css, "[title*='Reset prompt values']").click()  # CLICK RESET
    find(css, "[id*='search-I']").send_keys(i)
    time.sleep(0.5)
    find(css, "[title='Add']").click()  # CLICK PLUS
    time.sleep(0.5)
    find(css, "[title*='Refresh the document']").click()  # CLICK RUN
    WebDriverWait(driver, 10000).until(
        EC.element_to_be_clickable((css, "[title*='Zoom']"))
    )
    # GO TO EXPORT TAB
    find(css, "[title*='Export']").click()  # CLICK EXPORT
    time.sleep(3)
    # SELECT SUMMARY AND DETAILS AND CLICK EXPORT
    find(css, "[data-customclass*='CSVExportEntry']").click()
    find(css, "[placeholder='Search']").send_keys("Summary")
    find(css, "[class='sapMTableTH sapMListTblSelCol']").click()  # CLICK ALL
    # DOWNLOAD CSV
    find(css, "[title='Reset']").click()
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
    df = pd.read_csv(zf.open("Purchase History Report Summary.csv"))
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int16)
df.to_hdf("../H5/PH_RAW.H5", key=QS[0], mode="a")
import sqlalchemy

cn = sqlalchemy.create_engine(
    "mysql+pymysql://anveshjarabani:Zintak1!@mysql12--2.mysql.database.azure.com:3306/uct_data",
    connect_args={"ssl_ca": "DigiCertGlobalRootCA.crt.pem"},
)
df.replace([np.inf, -np.inf], np.nan, inplace=True)
cn.execute("DROP TABLE IF EXISTS PH_RAW_{QS[0]}")
df.to_sql(name="PH_RAW_{QS[0]}", con=cn, if_exists="replace", index=False)
print("PH.H5 Q COMPLETE")
ven = pd.read_csv(zf.open("Purchase History Report Detaile.csv"))
ven = ven[["Material - Key", "Vendor - Text"]]
ven.select_dtypes(include=[float]).astype(np.float16)
ven.select_dtypes(include=[int]).astype(np.int16)
ven.to_hdf("../H5/PH_RAW.H5", key=QS[0] + "_VEN", mode="a")
print("PH_RAW Q_VEN COMPLETE")
zf.close()
os.remove(crNew)
# BUILD FOLLOWUP PICKLE FILES
exec(open("PH CALC.py").read())
