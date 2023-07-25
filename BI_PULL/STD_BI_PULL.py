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
    EC.presence_of_element_located((By.ID, "__tile0-__container1-2")))
# CLICK ON MMC REPORT FAV TILE
lst = find(css, "div[id*='Favourite']").find_elements(tag, "bdi")
[i for i in lst if "STD_BI_PULL" in i.text][0].click()
WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((css, "[id*='promptsList']"))
)
STD=pd.DataFrame(columns=['PART_NUMBER','STD_COST'])
for i in PLANTS:
    # CLICK ON REFRESH BUTTON
    if i != PLANTS[0]:
        find(css, "[title='Refresh']").click()
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((css, "[id*='promptsList']")))
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
    WebDriverWait(driver, 10000).until(EC.element_to_be_clickable((css, "[title='Last page']")))
    # GO TO EXPORT TAB
    find(css, "[title='Export']").click()
    time.sleep(1)
    # DOWNLOAD TXT
    find(css, "[data-customclass*='TXTExportEntry']").click()
    find(css, "[id*='ConfirmExportButton']").click()
    while not os.path.exists("../../STD_BI_PULL.txt"): time.sleep(1) # WAIT TILL THE FILE IS DOWNLOADED
    INCOMING_DF=pd.read_csv("../../STD_BI_PULL.txt",delimiter='\t')
    INCOMING_DF.select_dtypes(include=[float]).astype(np.float16)
    INCOMING_DF.select_dtypes(include=[int]).astype(np.int16)
    INCOMING_DF = INCOMING_DF.pivot_table(
        index=["PART_NUMBER"], values=["STD_COST"], aggfunc=max
    )
    INCOMING_DF.reset_index(inplace=True)
    STD=pd.concat([STD, INCOMING_DF],ignore_index=True)
    print(len(STD),len(INCOMING_DF))
    os.remove("../../STD_BI_PULL.txt")
STD = STD[STD["PART_NUMBER"].str.endswith("-UCT") == False]
STD.columns = ["MATERIAL", "STD COST"]
STD.drop_duplicates(subset=["MATERIAL"], inplace=True, ignore_index=True)
STD["STD COST"] /= 1.106
STD.reset_index(inplace=True)
STD["STD COST"] = STD["STD COST"].round(2)
with pd.HDFStore("../H5/ST_BM_BR.H5", mode="r+") as store:
    store.put("STD", STD)
print("ST_BM_BR.H5 STD COMPLETE")