import pandas as pd
import xlwings as xl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from selenium import webdriver
chromeOptions = webdriver.ChromeOptions()
driver = webdriver.Chrome('sldr.exe')
driver.maximize_window()
MPN_df=xl.books.active.sheets(2).range('A1').expand('down').options(index=False).options(pd.DataFrame,index=False).value
MPN_df['link'] = 'https://www.mcmaster.com/'+MPN_df['PN']+'/'
for i in MPN_df['link']:
    driver.get(i)
    try:
        WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "[class*='PrceTxt']"),'$'))
        element=driver.find_element(By.CSS_SELECTOR, "[class*='PrceTxt']")
        if element:
            x=element.text
            MPN_df.loc[MPN_df['link']==i,'COST']=x
            MPN_df.loc[MPN_df['link']==i,'TIER']='STD'
            print(x)
    except:
        m=1
        while driver.find_elements(By.CSS_SELECTOR,"[data-mcm-prce-lvl='{}']".format(m)):
            lst = driver.find_elements(
                By.CSS_SELECTOR, "[data-mcm-prce-lvl='{}']".format(m))
            if m==1:
                MPN_df.loc[MPN_df['link']==i,'TIER']=lst[0].text
                MPN_df.loc[MPN_df['link']==i,'COST']=lst[1].text
            else:
                MPN_df.loc[len(MPN_df)]={'link':i,
                                         'PN': MPN_df.loc[MPN_df['link'] == i, 'PN'].reset_index().loc[0, 'PN'],
                                         'COST':lst[1].text,
                                         'TIER':lst[0].text}
            m+=1
            print(lst[0].text,lst[1].text)
MPN_df['$$']=MPN_df['COST'].str.extract('\$(\d+\.\d+)')
MPN_df=MPN_df.sort_values('PN')
xl.books.active.sheets.active.range('N1').options(index=False).value=MPN_df

    




