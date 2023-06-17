from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import zipfile
import time
import glob
import os
chromeOptions = webdriver.ChromeOptions()
today = datetime.today().strftime('%m/%d/%y')
START_DATE = (datetime.today()+delt.relativedelta(months=-18)
              ).strftime('%m/%d/%y')
driver = webdriver.Chrome('sldr.exe')
driver.maximize_window()
find = driver.find_element
finds = driver.find_elements
css = By.CSS_SELECTOR
located = EC.presence_of_element_located
clickable = EC.element_to_be_clickable
driver.get('http://alinbop.uct.local/BOE/BI')
driver.switch_to.frame(find(By.TAG_NAME, 'iframe'))
WebDriverWait(driver, 25).until(located((By.ID, '__label0-bdi')))
username = find(By.ID, "__input3-inner")
password = find(By.ID, "__input4-inner")
username.send_keys("ajarabani")
password.send_keys("Xuiqil9`")
find(By.ID, "__button1-inner").click()
WebDriverWait(driver, 25).until(located((By.ID, '__vbox5')))
# CLICK ON NOTIFICATION ANALYSIS FAV TILE
find(By.ID, "__tile0-__container1-3").click()
WebDriverWait(driver, 25).until(located((css, "[id*='promptsList']")))
elm = find(css, "ul[id*='promptsList']")
promts_lst = elm.find_elements(By.TAG_NAME, 'li')
#  ------------------------- ADD PLANTS TO PROMPT LIST -------------------------
for i in promts_lst:
    if 'Plant' in i.text:
        i.click()
        break
find(css, "[title*='Reset prompts']").click()  # CLICK RESET
find(css, "[id*='search-I']").send_keys('3322')
find(css, "[title*='Add']").click()  # CLICK PLUS
find(css, "[id*='search-I']").send_keys('3321')
find(css, "[title='Add']").click()  # CLICK PLUS
time.sleep(1)
# FOR DATES ENTRY ----- DAY INTERVAL PROMPT
for i in promts_lst:
    if 'Day Interval' in i.text:
        i.click()
        break
WebDriverWait(driver, 25).until(located((css, "[id*='rangeInputLow-inner']")))
find(css, "[id*='rangeInputLow-inner']").send_keys(START_DATE)  # START DATE
find(css, "[id*='rangeInputHigh-inner']").send_keys(today)  # CURRENT DATE
find(css, "[title*='Refresh the document']").click()  # CLICK RUN
WebDriverWait(driver, 10000).until(clickable((css, "[title*='Zoom']")))
# GO TO EXPORT TAB
find(css, "[title='Export']").click()
time.sleep(3)
# DOWNLOAD CSV BY DATA ONLY.
find(css, "[data-customclass*='CSVExportEntry']").click()
find(css, "[id*='ConfirmExportButton']").click()
# WAIT TILL THE FILE IS DOWNLOADED
wait = True
DLOADS_PATH = r"C:\Users\ajarabani\Downloads/*zip"
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
zf = zipfile.ZipFile(crNew)
df = pd.read_csv(zf.open('Notification (Defect) Analysis .csv'))
df = df.loc[df.iloc[:, 0].notna()]
df.replace(',', '', regex=True, inplace=True)
df.rename(columns={'Total QN  Quantity': 'Total QN Quantity'}, inplace=True)
df['Total QN Quantity'] = df['Total QN Quantity'].astype(float)
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int8)
df = df[['Plant', 'Calendar Year/Week', 'Required Start Date', 'Notification PS Text - Long Text',
         'CAUSEDBY', 'Defect Type', 'Defect Group', 'Vendor-Key',
         'Vendor Desc', 'Material group', 'Material - Key', 'Material - Medium Text',
         'Standard Price', 'Rejected Amount', 'Total QN Quantity']]
for col in ['Rejected Amount', 'Standard Price']:
    df[col] = pd.to_numeric(df[col].str.replace('$', ''))
df['Required Start Date']=pd.to_datetime(df['Required Start Date'])
df.to_pickle('QN M-18.pkl')
os.remove(crNew)
print('QN M-18.PKL COMPLETE')