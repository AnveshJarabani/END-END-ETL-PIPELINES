if __name__ == '__main__':
    import pandas as pd
    import xlwings as xl
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium import webdriver
    import multiprocessing as mp
    import warnings,os,time,re,json
    from rich import print
    warnings.simplefilter(action='ignore', category=(FutureWarning, UserWarning))
    os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
    from def_cost_extractor import cost_extractor
    chromeOptions = webdriver.ChromeOptions()
    caps=DesiredCapabilities.CHROME
    caps['goog:loggingPrefs']={'performance':"ALL"}
    chromeOptions.add_argument('--blink-settings=imagesEnabled=false')
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--log-level=3')
    chromeOptions.add_argument('--log-path=nul')
    def log_entry(entry):
        response=json.loads(entry['message'])['message']
        return response
    MPN_df=xl.books.active.sheets(2).range('A1').expand('down').options(index=False).options(pd.DataFrame,index=False).value
    home_raw = 'https://www.mcmaster.com/{}/'
    driver = webdriver.Chrome('sldr.exe',options=chromeOptions,desired_capabilities=caps)
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
    res_df=res_df[['link','PN','TIER','COST']]
    # xl.books.active.sheets.add()
    print('processed in {} secs'.format(round(time.time()-start,2)))
    xl.books.active.sheets.active.range('N1').options(index=False).value=res_df
    print(res_df)
    
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