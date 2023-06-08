from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import zipfile,time,glob,os
chromeOptions = webdriver.ChromeOptions()
today=datetime.today().strftime('%m/%d/%y')
START_DATE=(datetime.today()+delt.relativedelta(months=-18)).strftime('%m/%d/%y')
driver=webdriver.Chrome('sldr.exe')
driver.maximize_window()
driver.get('http://alinbop.uct.local/BOE/BI')
driver.switch_to.frame(driver.find_element(By.TAG_NAME,'iframe'))
WebDriverWait(driver,25).until(EC.presence_of_element_located((By.ID, '__label0-bdi')))
username = driver.find_element(By.ID,"__input3-inner")
password = driver.find_element(By.ID,"__input4-inner")
username.send_keys("ajarabani")
password.send_keys("Xuiqil9`")
driver.find_element(By.ID,"__button1-inner").click()
WebDriverWait(driver,25).until(EC.presence_of_element_located((By.ID, '__vbox5')))
driver.find_element(By.ID,"__tile0-__container1-0").click() # CLICK ON EMPLOYEE LABOR HRS REPORT FAV TILE
WebDriverWait(driver,25).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[id*='promptsList']")))
driver.find_element(By.CSS_SELECTOR,"[id*='promptsList-4']").click() # TICKET TYPE PROMPT
driver.find_element(By.CSS_SELECTOR,"[title*='Show the settings page']").click() # SELECT SETTINGS
time.sleep(1)
driver.find_element(By.CSS_SELECTOR,"[title*='Show the settings page']").click()
driver.find_element(By.CSS_SELECTOR,"[class*='SettingsSearchByKeys']").click() # TURN ON KEY SEARCH
driver.find_element(By.CSS_SELECTOR,"[class*='SettingsShowKeys']").click() # TURN ON KEY SEARCH
driver.find_element(By.CSS_SELECTOR,"[title*='Refresh']").click() # REFRESH
driver.find_element(By.CSS_SELECTOR,"[id*='search-I']").send_keys('L')
driver.find_element(By.CSS_SELECTOR,"[title*='Add']").click() # CLICK PLUS
driver.find_element(By.CSS_SELECTOR,"[id*='search-I']").send_keys('S')
driver.find_element(By.CSS_SELECTOR,"[title='Add']").click() # CLICK PLUS
driver.find_element(By.CSS_SELECTOR,"[id*='promptsList-0']").click() # CLICK PLANT PROMT
driver.find_element(By.CSS_SELECTOR,"[title*='Reset prompts']").click() # CLICK RESET
driver.find_element(By.CSS_SELECTOR,"[id*='search-I']").send_keys('3322')
driver.find_element(By.CSS_SELECTOR,"[title*='Add']").click() # CLICK PLUS
driver.find_element(By.CSS_SELECTOR,"[id*='search-I']").send_keys('3321')
driver.find_element(By.CSS_SELECTOR,"[title='Add']").click() # CLICK PLUS
time.sleep(1)
# FOR DATES ENTRY -----
driver.find_element(By.CSS_SELECTOR,"[id*='promptsList-5']").click() # DAY INTERVAL PROMPT
WebDriverWait(driver,25).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[id*='rangeInputLow-inner']")))
driver.find_element(By.CSS_SELECTOR,"[id*='rangeInputLow-inner']").send_keys(START_DATE) # START DATE
driver.find_element(By.CSS_SELECTOR,"[id*='rangeInputHigh-inner']").send_keys(today) # CURRENT DATE
driver.find_element(By.CSS_SELECTOR,"[title*='Refresh the document']").click() # CLICK RUN
WebDriverWait(driver,10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[title*='Zoom']")))
# GO TO EXPORT TAB
driver.find_element(By.CSS_SELECTOR,"[title='Export']").click()
time.sleep(3)
# DOWNLOAD CSV BY DATA ONLY. 
driver.find_element(By.CSS_SELECTOR,"[data-customclass*='CSVExportEntry']").click()    
driver.find_element(By.CSS_SELECTOR,"[placeholder='Search']").send_keys('Labor Hours')
driver.find_element(By.CSS_SELECTOR,"[class='sapMTableTH sapMListTblSelCol']").click() # CLICK ALL
driver.find_element(By.CSS_SELECTOR,"[id*='ConfirmExportButton']").click()
# WAIT TILL THE FILE IS DOWNLOADED
wait=True
DLOADS_PATH=r"C:\Users\ajarabani\Downloads/*zip"
files=glob.iglob(DLOADS_PATH)
cr1=max(files,key=os.path.getmtime)
while wait:
    files=glob.iglob(DLOADS_PATH)
    crNew=max(files,key=os.path.getmtime)
    if crNew==cr1:
        time.sleep(1)
    else:
        crNew_path=os.path.join(DLOADS_PATH,crNew)
        wait=False
#SIMPLIFY THE CSV FILE AND SAVE IT AS A PICIKLE FILE.
crNew_path='C:\\Users\\ajarabani\\Downloads\\Employee Labor Hours Report_P2M018.zip'
zf=zipfile.ZipFile(crNew_path)
df=pd.read_csv(zf.open('Employee Labor Hours.csv'))
df = df[(df['Order - Material (Key)'] != '#') & (df['Order'] != '#') & (df['Standard Text Key'] != '#')]
df=df.loc[df.iloc[:,0].notna()]
df.replace(',','',regex=True,inplace=True)
df['Operation Quantity']=df['Operation Quantity'].astype(float)
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int8)
df.to_pickle('LBR M-18.pkl')
os.remove(crNew)
print('LBR M-18.PKL COMPLETE')
# BUILD FOLLOWUP PICKLE FILES
exec(open('ACT VS PLN LBR CST.py').read())                
exec(open('LBR HR WO TRENDS.py').read())                
exec(open('PROCESS DAYS.py').read())                
exec(open('LBR QLY COSTS.py').read())                
exec(open('WC LOAD HRS.py').read())         
driver.close()                                                                 