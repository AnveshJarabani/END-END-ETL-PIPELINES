import pandas as pd
import xlwings as xl
import multiprocessing as mp
import warnings,os,time,re
import requests,json
from requests_html import HTMLSession
from selenium import webdriver
from bs4 import BeautifulSoup as bs
warnings.simplefilter(action='ignore', category=(FutureWarning, UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
MPN_df=xl.books.active.sheets(2).range('A1').expand('down').options(index=False).options(pd.DataFrame,index=False).value
start=time.time()
chromeOptions = webdriver.ChromeOptions()
driver = webdriver.Chrome('sldr.exe', options=chromeOptions)
raw = "https://www.mcmaster.com/mv1685653428/WebParts/Ordering/InLnOrdWebPart/ItmPrsnttnDynamicDat.aspx?" + \
    "acttxt=getstockstatus&partnbrtxt={}&possiblecompnbrtxt=&isinlnspec=false&" + \
    "attrCompIds=&attrnm=&attrval=&cssAlias=undefined&useEs6=true"
home_raw = 'https://www.mcmaster.com/{}/'
driver.get(home_raw.format(MPN_df.iloc[0,0]))
all_cookies=driver.get_cookies()
dct={}
for ck in all_cookies:
    dct[ck['name']]=ck['value']
# cookies={}
# for cookie in full_cookies:
#     cookies.update(cookie.__dict__)
# cookies={x:str(y) if y is not None else None for x,y in cookies.items()}
for i in MPN_df.iloc[:, 0]:
# def cost_extractor(i):
    # global raw,home_raw,cookies
    lnk = raw.format(i)
    response=requests.get(url=lnk,cookies=dct)
    jsn_string = response.text
    dict = json.loads(jsn_string)
    if not dict['PrceTiers']:
        print(dict['PrceTxt'])
        data = {'PN': [i],
                '$$': [dict['PrceTxt']],
                'T': None}
    else:
        data = {'PN': [],
                '$$': [],
                'T': []}
        for y in dict['PrceTiers']:
            print(y['PrceTierQtyTxt'], y['PrceTierPrceTxt'])
            data['PN'].append(i)
            data['$$'].append(y['PrceTierPrceTxt'])
            data['T'].append(y['PrceTierQtyTxt'])
    # return pd.DataFrame(data)
# if __name__ == '__main__':
#     pool = mp.Pool(processes=8)
#     results=pool.map(cost_extractor, MPN_df.iloc[:,0])
#     res_df=pd.concat(results,ignore_index=True)
#     res_df['COST'] = res_df['$$'].str.extract('(\$\d+\.\d+)')
#     res_df=res_df.sort_values(['PN','COST'],ascending=[True,False])
#     res_df['TIER']=res_df['$$'].apply(lambda x:'EA' if 'Each' in x else 
#                                         '{} Pack'.format(re.search('\d+$', x)[0]))
#     res_df['link']=res_df['PN'].apply(lambda x:home_raw.format(x))
#     res_df.loc[res_df['T'].notna(),'TIER']=res_df['T']
#     res_df=res_df[['link','PN','TIER','COST']]
#     print(res_df)
#     # xl.books.active.sheets.add()
#     # xl.books.active.sheets.active.range('A1').options(index=False).value=res_df
#     print('processed in {} secs'.format(round(time.time()-start,2)))




# def cost_extractor(i):
#     lnk = """https://www.mcmaster.com/
#             mv1685653428/WebParts/Ordering/InLnOrdWebPart/ItmPrsnttnDynamicDat.aspx?acttxt=
#             getstockstatus&partnbrtxt={}&possiblecompnbrtxt=&isinlnspec=false&attrCompIds=&
#             attrnm=&attrval=&cssAlias=undefined&useEs6=true""".format(i)
#     response = session.get(lnk)
#     response.html.render()
#     while cls1 not in response.html.html and cls2 not in response.html.html:
#         # try:
#         response.html.render(sleep=0.5)
#         if cls1 in response.html.html:
#             soup = bs(response.html.html, 'html.parser')
#             print(soup.find_all('div', class_='PrceTxt')[0].text)
#         elif cls2 in response.html.html:
#             soup=bs(response.html.html,'html.parser')
#             table=soup.find_all('table',class_='PrceTierTbl')[0]
#             for row in table.find_all('tr'):
#                 cells=row.find_all('td')
#                 print([i.text for i in cells])
#         # except:
#         #     break
# if __name__ == '__main__':
#     pool = mp.Pool(processes=8)
#     results=pool.map(cost_extractor, MPN_df.iloc[:,0].values)
    # res_df=pd.concat(results,ignore_index=True)
    # res_df['COST'] = res_df['$$'].str.extract('(\$\d+\.\d+)')
    # res_df=res_df.sort_values(['PN','COST'],ascending=[True,False])
    # res_df['TIER']=res_df['$$'].apply(lambda x:'EA' if 'Each' in x else 
    #                                   '{} Pack'.format(re.search('\d+$', x)[0]))
    # res_df.loc[res_df['T'].notna(),'TIER']=res_df['T']
    # res_df=res_df[['link','PN','TIER','COST']]
    # xl.books.active.sheets.add()
    # xl.books.active.sheets.active.range('A1').options(index=False).value=res_df
    # print('processed in {} secs'.format(round(time.time()-start,2)))
# driver.maximize_window()
# driver = webdriver.Chrome('sldr.exe',options=chromeOptions)
# def cost_extractor(i):
#     lnk='https://www.mcmaster.com/{}/'.format(i)
#     driver.get(lnk)
#     WebDriverWait(driver, 20).until(EC.any_of(
#         EC.text_to_be_present_in_element(
#         (By.CSS_SELECTOR, "[class*='PrceTxt']"),'$'),
#         EC.text_to_be_present_in_element(
#             (By.CSS_SELECTOR, "[data-mcm-prce-lvl]"),)
#         ))
#     source=driver.page_source
#     soup=bs(source,'html.parser')
#     element=soup.find('div', class_='PrceTxt')
#     if element:
#         x=element.text
#         print(x)
#         dct = {'link': [lnk],
#                 'PN': [i],
#                 '$$': [x],
#                 'T': None}
#         return pd.DataFrame(dct)
        
#     else:
#         m=1
#         dct={'link':[],
#                 'PN':[],
#                 '$$':[],
#                 'T':[]}
#         while soup.find_all("[data-mcm-prce-lvl='{}']".format(m)):
#             lst = soup.find_all("[data-mcm-prce-lvl='{}']".format(m))
#             dct['link'].append(lnk)
#             dct['PN'].append(i)
#             dct['$$'].append(lst[1].text)
#             dct['T'].append(lst[0].text)
#             m+=1
#             print(lst[0].text,lst[1].text)
#         return pd.DataFrame(dct)




