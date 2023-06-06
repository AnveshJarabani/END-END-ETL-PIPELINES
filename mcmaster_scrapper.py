import pandas as pd
import xlwings as xl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import multiprocessing as mp
import warnings,os,time,re
warnings.simplefilter(action='ignore', category=(FutureWarning, UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
chromeOptions = webdriver.ChromeOptions()
# chromeOptions.add_argument('--blink-settings=imagesEnabled=false')
# chromeOptions.add_argument('--headless')
# chromeOptions.add_argument('--log-level=3')
# chromeOptions.add_argument('--log-path=nul')
start=time.time()
# driver.maximize_window()
driver = webdriver.Chrome('sldr.exe',options=chromeOptions)
MPN_df=xl.books.active.sheets(2).range('A1').expand('down').options(index=False).options(pd.DataFrame,index=False).value
lnk1 = 'https://www.mcmaster.com/mv1685653428/WebParts/Ordering/InLnOrdWebPart/ItmPrsnttnDynamicDat.aspx?acttxt=getstockstatus&partnbrtxt=92510A476&possiblecompnbrtxt=&isinlnspec=false&attrCompIds=&attrnm=&attrval=&cssAlias=undefined&useEs6=true'
driver.get(lnk1)
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
            print(f'\033[93m{x}\033[0m')
            dct = {'link': [lnk],
                   'PN': [i],
                   '$$': [x],
                   'T': None}
            return pd.DataFrame(dct)      
    except:
        m=1
        dct={'link':[],
                'PN':[],
                '$$':[],
                'T':[]}
        while driver.find_elements(By.CSS_SELECTOR,"[data-mcm-prce-lvl='{}']".format(m)):
            lst = driver.find_elements(
                By.CSS_SELECTOR, "[data-mcm-prce-lvl='{}']".format(m))
            dct['link'].append(lnk)
            dct['PN'].append(i)
            dct['$$'].append(lst[1].text)
            dct['T'].append(lst[0].text)
            m+=1
            print(f'\033[96m{lst[0].text,lst[1].text}\033[0m')
        return pd.DataFrame(dct)
if __name__ == '__main__':
    pool = mp.Pool(processes=8)
    results=pool.map(cost_extractor, MPN_df.iloc[:,0].values)
    res_df=pd.concat(results,ignore_index=True)
    res_df['COST'] = res_df['$$'].str.extract('(\$\d+\.\d+)')
    res_df=res_df.sort_values(['PN','COST'],ascending=[True,False])
    res_df['TIER']=res_df['$$'].apply(lambda x:'EA' if 'Each' in x else 
                                      '{} Pack'.format(re.search('\d+$', x)[0]))
    res_df.loc[res_df['T'].notna(),'TIER']=res_df['T']
    res_df=res_df[['link','PN','TIER','COST']]
    # xl.books.active.sheets.add()
    # xl.books.active.sheets.active.range('A1').options(index=False).value=res_df
    print(res_df)
    print('processed in {} secs'.format(round(time.time()-start,2)))




