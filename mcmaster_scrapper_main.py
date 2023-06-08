import xlwings as xl
import traceback


def add_image(l, sht_name, rn, row):
    try:
        xl.books.active.sheets[sht_name].pictures.add(
            image=row['png'])  #, name=f'{row["PN"]} {rn}', left=l, top=(rn*30)+2, height=27)
        print(f'Sucess {row["PN"]} link {row["png"]}')
    except Exception as e:
        print(traceback.format_exc())
        print(f'fail {row["PN"]} link {row["png"]}')

if __name__ == '__main__':
    import pandas as pd
    import xlwings as xl
    xl.books.active.sheets['Test'].delete()
    # from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium import webdriver
    import multiprocessing as mp
    import warnings,os,time,re,json
    from rich import print
    from def_cost_extractor import cost_extractor
    warnings.simplefilter(action='ignore', category=(FutureWarning, UserWarning))
    os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
    chromeOptions = webdriver.ChromeOptions()
    # caps=DesiredCapabilities.CHROME
    # caps['goog:loggingPrefs']={'performance':"ALL"}
    chromeOptions.add_argument('--blink-settings=imagesEnabled=false')
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--log-level=3')
    chromeOptions.add_argument('--log-path=nul')
    def log_entry(entry):
        response=json.loads(entry['message'])['message']
        return response
    MPN_df=xl.books.active.sheets['Sheet1'].range('A1').expand('down').options(index=False).options(pd.DataFrame,index=False).value
    home_raw = 'https://www.mcmaster.com/{}/'
    driver = webdriver.Chrome('sldr.exe',options=chromeOptions)
    raw = 'https://www.mcmaster.com/WebParts/Ordering/InLnOrdWebPart/ItmPrsnttnDynamicDat.aspx?acttxt=dynamicdat&partnbrtxt={}'
    driver.get(home_raw.format(MPN_df.iloc[0,0]))
    time.sleep(2)
    all_cookies=driver.get_cookies()
    cookies={}
    for i in all_cookies:
        cookies[i['name']]=i['value']
    driver.close()
    start=time.time()
    pool = mp.Pool(processes=10)
    results=pool.starmap(cost_extractor, [(i,raw,cookies) for i in MPN_df.iloc[:,0]])
    res_df=pd.concat([pd.DataFrame(i) for i in results],ignore_index=True)
    res_df['COST'] = res_df['$$'].str.extract('(\$\d+\.\d+)')
    res_df=res_df.sort_values(['PN','COST'],ascending=[True,False],ignore_index=True)
    res_df['TIER']=res_df['$$'].apply(lambda x:'EA' if 'Each' in x else 
                                      '{} Pack'.format(re.search('\d+$', x)[0]))
    res_df['link']=res_df['PN'].apply(lambda x:home_raw.format(x))
    res_df.loc[res_df['T'].notna(),'TIER']=res_df['T']
    res_df=res_df[['link','PN','TIER','COST','png']]
    xl.books.active.sheets.add(after='Sheet1',name='Test')
    print(res_df)
    print('processed in {} secs'.format(round(time.time()-start,2)))
    sht=xl.books.active.sheets['Test']
    sht.range('A1').options(
        index=False).value = res_df.iloc[:, 0:4]
    sht.range('E1').value='Image'
    rnge = sht.range('E1:R{}'.format(len(res_df)+2))
    sht_name=sht.name
    rnge.row_height=30
    rnge.column_width=10
    l = sht.range('E2').left+10/4
    pool.starmap(add_image,[(l,sht_name,rn+1,row) for rn,row in res_df.iterrows()])


    # def add_image(l, sht_name, rn, row):
    #     xl.books.active.sheets[sht_name].pictures.add(
    #         row['png'], name=f'{row["PN"]} {rn}', left=l, top=(rn*30)+2, height=27)

    # for rn,row in res_df.iterrows():
    #     rn+=1
    #     add_image(l,sht_name,rn,row)
    # browser_log=driver.get_log('performance')
    # events=[log_entry(entry) for entry in browser_log]
    # events=[event for event in events if 'Network.response' in event['method']]
    # for i in events:
    #     if 'params' in i.keys():
    #         if 'response' in i['params']:
    #             if 'aspx' in i['params']['response']['url']:
    #                 t = re.search(r"\/(\w+)\/",i['params']['response']['url']).group(1)
    #                 break
    # raw = f"https://www.mcmaster.com/{t}/WebParts/Ordering/InLnOrdWebPart/ItmPrsnttnDynamicDat.aspx?"+ \
    #     "acttxt=dynamicdat&partnbrtxt={}&possiblecompnbrtxt=&isinlnspec=false&"+ \
    #     "attrCompIds=&attrnm=&attrval=&cssAlias=undefined&useEs6=true"