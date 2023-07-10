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
find = driver.find_element
finds = driver.find_elements
tag = By.TAG_NAME
css = By.CSS_SELECTOR
driver.maximize_window()
driver.get("http://alinbop.uct.local/BOE/BI")
driver.switch_to.frame(find(tag, "iframe"))
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "__label0-bdi")))
username = find(css, "[placeholder='User Name']")
password = find(css, "[placeholder='Password']")
keys = json.load(open("../PRIVATE/encrypt.json", "r"))
username.send_keys(keys["BI_USER"])
password.send_keys(keys["BI_PASS"])
PLANTS = ["3321", "3322"]
find(css, "[class*='LoginButton']").click()
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((By.ID, "__tile0-__container1-2"))
)
# CLICK ON MMC REPORT FAV TILE
lst = find(css, "div[id*='Favourite']").find_elements(tag, "bdi")
[i for i in lst if "Material Master Char" in i.text][0].click()
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']"))
)
for i in PLANTS:
    # CLICK ON REFRESH BUTTON
    if i != PLANTS[0]:
        find(css, "[title='Refresh']").click()
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((css, "[id*='promptsList']"))
        )
    find(css, "[title*='Reset prompts']").click()  # CLICK RESET
    # CLICK PLANT PROMT
    prompts_list = find(css, 'div[class*="PromptsSummaryList"]')
    prompts = prompts_list.find_elements(tag, "span")
    [i for i in prompts if "Plant" in i.text][0].click()
    time.sleep(0.5)
    find(css, "[id*='search-I']").send_keys(i)
    find(css, "[title='Add']").click()  # CLICK PLUS
    time.sleep(0.5)
    # ----RUN THE REPORT WITH CSV
    find(css, "[title*='Refresh the document']").click()  # CLICK RUN
    WebDriverWait(driver, 10000).until(
        EC.element_to_be_clickable((css, "[title='Last page']"))
    )
    # GO TO EXPORT TAB
    find(css, "[title='Export']").click()
    time.sleep(3)
    # DOWNLOAD CSV
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
            if i == "3321":
                cr_INT = crNew
            else:
                cr_FAB = crNew
            wait = False
# SIMPLIFY THE CSV FILE AND SAVE IT AS A HD5 FILE.
time.sleep(3)
with zipfile.ZipFile(cr_INT) as zf_INT:
    INT_STD = pd.read_csv(zf_INT.open("Material Master Characteristics.csv"))
INT_STD = INT_STD[["Material - Key", "Per Unit Price"]]
INT_STD.select_dtypes(include=[float]).astype(np.float16)
INT_STD.select_dtypes(include=[int]).astype(np.int16)
INT_STD = INT_STD.pivot_table(
    index=["Material - Key"], values=["Per Unit Price"], aggfunc=max
)
INT_STD.reset_index(inplace=True)
with zipfile.ZipFile(cr_FAB) as zf_FAB:
    FAB_STD = pd.read_csv(zf_FAB.open("Material Master Characteristics.csv"))
FAB_STD = FAB_STD[["Material - Key", "Per Unit Price"]]
FAB_STD.select_dtypes(include=[float]).astype(np.float16)
FAB_STD.select_dtypes(include=[int]).astype(np.int16)
FAB_STD = FAB_STD.pivot_table(
    index=["Material - Key"], values=["Per Unit Price"], aggfunc=max
)
FAB_STD.reset_index(inplace=True)
os.remove(cr_FAB)
os.remove(cr_INT)
# BUILD FOLLOWUP H5 FILES
STD = pd.concat([FAB_STD, INT_STD], ignore_index=True)
STD = STD[STD["Material - Key"].str.endswith("-UCT") == False]
STD.columns = ["MATERIAL", "STD COST"]
STD.drop_duplicates(subset=["MATERIAL"], inplace=True, ignore_index=True)

STD["STD COST"] = STD["STD COST"].str.replace("\$|\,|", "", regex=True).astype(float)
STD["STD COST"] /= 1.106
STD.reset_index(inplace=True)
STD["STD COST"] = STD["STD COST"].round(2)
with pd.HDFStore("../H5/ST_BM_BR.H5", mode="r+") as store:
    store.put("STD", STD)
print("ST_BM_BR.H5 STD COMPLETE")

