from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import dateutil.relativedelta as delt
import pandas as pd
import numpy as np
import zipfile,time,glob,os
dict={1:'01',2:'01',3:'01',
      4:'02',5:'02',6:'02',
      7:'03',8:'03',9:'03',
      10:'04',11:'04',12:'04'}
QS=[]
dt=datetime.now()
QS.append(dict[dt.month]+str(dt.year))
start_time=time.time()
chromeOptions = webdriver.ChromeOptions()
today=datetime.today().strftime('%m/%d/%y')
START_DATE=(datetime.today()+delt.relativedelta(months=-18)).strftime('%m/%d/%y')
driver=webdriver.Chrome('sldr.exe')
driver.maximize_window()
driver.get('http://alinbop.uct.local/BOE/BI') 
driver.switch_to.frame(driver.find_element(By.TAG_NAME,'iframe'))
WebDriverWait(driver,25).until(EC.presence_of_element_located((By.ID, '__label0-bdi')))
driver.find_element(By.CSS_SELECTOR,"[placeholder='User Name']").send_keys("ajarabani")
driver.find_element(By.CSS_SELECTOR,"[placeholder='Password']").send_keys("Zintak1!")
driver.find_element(By.CSS_SELECTOR,"[class*='LoginButton']").click()
WebDriverWait(driver,25).until(EC.presence_of_element_located((By.ID, '__tile0-__container1-2')))
driver.find_element(By.ID,"__tile0-__container1-3").click() # CLICK ON PURCHASE HIST REPORT FAV TILE
WebDriverWait(driver,25).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[id*='promptsList']")))
for i in QS:
    if i!=QS[0]:
        driver.find_element(By.CSS_SELECTOR,"[title='Refresh']").click() # CLICK REFRESH
        WebDriverWait(driver,25).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[id*='promptsList']")))
    # FOR PLANT SELECTION - CHANDLER FAB & INTEGRATION , SELECTING KEYS
    if i==QS[0]:    
        driver.find_element(By.CSS_SELECTOR,"[title*='Reset prompts']").click() # CLICK RESET
        driver.find_element(By.CSS_SELECTOR,"[id*='promptsList-5']").click() # CLICK PLANT PROMT
        driver.find_element(By.CSS_SELECTOR,"[title*='Show the settings page']").click() # SELECT SETTINGS
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR,"[class*='SettingsSearchByKeys']").click() # TURN ON KEY SEARCH
        driver.find_element(By.CSS_SELECTOR,"[class*='SettingsShowKeys']").click() # TURN ON KEY SEARCH
        driver.find_element(By.CSS_SELECTOR,"[id*='search-I']").send_keys('3322')
        driver.find_element(By.CSS_SELECTOR,"[title*='Add']").click() # CLICK PLUS
        driver.find_element(By.CSS_SELECTOR,"[id*='search-I']").send_keys('3321')
        driver.find_element(By.CSS_SELECTOR,"[title='Add']").click() # CLICK PLUS
    driver.find_element(By.CSS_SELECTOR,"[id*='promptsList-3']").click() # FISCAL QUARTER PROMPT
    driver.find_element(By.CSS_SELECTOR,"[title*='Reset prompt values']").click() # CLICK RESET
    driver.find_element(By.CSS_SELECTOR,"[id*='search-I']").send_keys(i) 
    time.sleep(.5)
    driver.find_element(By.CSS_SELECTOR,"[title='Add']").click() # CLICK PLUS
    time.sleep(.5)
    driver.find_element(By.CSS_SELECTOR,"[title*='Refresh the document']").click() # CLICK RUN
    WebDriverWait(driver,10000).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[title*='Zoom']")))
    # GO TO EXPORT TAB
    driver.find_element(By.CSS_SELECTOR,"[title*='Export']").click() # CLICK EXPORT
    time.sleep(3)
    #SELECT SUMMARY AND DETAILS AND CLICK EXPORT
    driver.find_element(By.CSS_SELECTOR,"[data-customclass*='CSVExportEntry']").click()    
    driver.find_element(By.CSS_SELECTOR,"[placeholder='Search']").send_keys('Summary')
    driver.find_element(By.CSS_SELECTOR,"[class='sapMTableTH sapMListTblSelCol']").click() # CLICK ALL
    # DOWNLOAD CSV 
    driver.find_element(By.CSS_SELECTOR,"[title='Reset']").click()
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
#SIMPLIFY THE CSV FILE AND SAVE IT AS A HD5 FILE.
time.sleep(3)
zf=zipfile.ZipFile(crNew_path)
df=pd.read_csv(zf.open('Purchase History Report Summary.csv'))
df.select_dtypes(include=[float]).astype(np.float16)
df.select_dtypes(include=[int]).astype(np.int16)
df.to_hdf('PH_RAW.H5',key=QS[0],mode='a')
print('PH.H5 Q COMPLETE')
ven=pd.read_csv(zf.open('Purchase History Report Detaile.csv'))
ven=ven[['Material - Key','Vendor - Text']]
ven.select_dtypes(include=[float]).astype(np.float16)
ven.select_dtypes(include=[int]).astype(np.int16)
ven.to_hdf('PH_RAW.H5',key=QS[0]+'_VEN',mode='a')
print('PH_RAW Q_VEN COMPLETE')
zf.close()
os.remove(crNew)
# BUILD FOLLOWUP PICKLE FILES
exec(open('PH CALC.py').read())                             