import pandas as pd
import xlwings as xl
import multiprocessing as mp
import warnings,os,time,re
import scrapy
from scrapy_playwright.page import PageMethod


warnings.simplefilter(action='ignore', category=(FutureWarning, UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
MPN_df=xl.books.active.sheets(2).range('A1').expand('down').options(index=False).options(pd.DataFrame,index=False).value
start=time.time()
lnk='https://www.mcmaster.com/{}/'.format(MPN_df.iloc[0,0])


class MySpider(scrapy.Spider):
    name = 'my_spider'

    def start_requests(self):
        lnk = 'https://www.mcmaster.com/{}/'.format(MPN_df.iloc[0,0])
        yield scrapy.Request(url=lnk,
                             meta=dict(
                                playwright=True,
                                playwright_include_page=True,
                                playwright_page_methods=[PageMethod(
                                    'waitForSelector','div#PrceTxt')]
                             ), callback=self.parse)

    def parse(self, response):
        yield {
            'text':response.text
        }


for r in MySpider().start_requests():
    print(r)

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
# if __name__ == '__main__':
#     pool = mp.Pool(processes=8)
#     results=pool.map(cost_extractor, MPN_df.iloc[:,0].values)
#     res_df=pd.concat(results,ignore_index=True)
#     res_df['COST'] = res_df['$$'].str.extract('(\$\d+\.\d+)')
#     res_df=res_df.sort_values(['PN','COST'],ascending=[True,False])
#     res_df['TIER']=res_df['$$'].apply(lambda x:'EA' if 'Each' in x else 
#                                       '{} Pack'.format(re.search('\d+$', x)[0]))
#     res_df.loc[res_df['T'].notna(),'TIER']=res_df['T']
#     res_df=res_df[['link','PN','TIER','COST']]
#     xl.books.active.sheets.add()
#     xl.books.active.sheets.active.range('A1').options(index=False).value=res_df
#     print('processed in {} secs'.format(round(time.time()-start,2)))




