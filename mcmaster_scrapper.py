import pandas as pd
import xlwings as xl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import multiprocessing as mp
import warnings,os,time
warnings.simplefilter(action='ignore', category=(FutureWarning, UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('--blink-settings=imagesEnabled=false')
start=time.time()
# driver.maximize_window()
driver = webdriver.Chrome('sldr.exe',options=chromeOptions)
MPN_df=xl.books.active.sheets(2).range('A1').expand('down').options(index=False).options(pd.DataFrame,index=False).value
def cost_extractor(i):
    lnk='https://www.mcmaster.com/{}/'.format(i)
    driver.get(lnk)
    WebDriverWait(driver, 20).until(EC.any_of(
        EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, "[class*='PrceTxt']"),'$'),
        EC.presence_of_element_located(
        (By.CSS_SELECTOR,"[data-mcm-prce-lvl]"))
        ))
    try:
        element=driver.find_element(By.CSS_SELECTOR, "[class*='PrceTxt']")
        if element:
            x=element.text
            print(x)
            dct = {'link': [lnk],
                   'PN': [i],
                   'COST': [x],
                   'TIER': ['STD']}
            return pd.DataFrame(dct)
            
    except:
        m=1
        while driver.find_elements(By.CSS_SELECTOR,"[data-mcm-prce-lvl='{}']".format(m)):
            lst = driver.find_elements(
                By.CSS_SELECTOR, "[data-mcm-prce-lvl='{}']".format(m))
            if m==1:
                dct = {'link': [lnk],
                       'PN': [i],
                       'COST': [lst[1].text],
                       'TIER': [lst[0].text]}
                
            else:
                dct['link'].append(lnk)
                dct['PN'].append(i)
                dct['COST'].append(lst[1].text)
                dct['TIER'].append(lst[0].text)
            m+=1
            print(lst[0].text,lst[1].text)
        return pd.DataFrame(dct)
if __name__ == '__main__':
    pool = mp.Pool(processes=mp.cpu_count())
    results=pool.map(cost_extractor, MPN_df.iloc[:,0].values)
    res_df=pd.concat(results)
    res_df['$$'] = res_df['COST'].str.extract('(\$\d+\.\d+)')
    res_df=res_df.sort_values(['PN','$$'])
    xl.books.active.sheets(3).range('N1').options(index=False).value=res_df
    print('processed in {} secs'.format(round(time.time()-start,2)))




