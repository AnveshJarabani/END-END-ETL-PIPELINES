if __name__ == '__main__':
    import pandas as pd
    import xlwings as xl
    if 'Test' in xl.books.active.sheet_names:
        xl.books.active.sheets['Test'].delete()
    from selenium import webdriver
    import multiprocessing as mp
    import warnings,os,time,re,json
    from rich import print
    from def_cost_extractor import cost_extractor
    warnings.simplefilter(action='ignore', category=(FutureWarning, UserWarning))
    os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
    pdm_df = pd.read_csv(r"C:\Users\ajarabani\Downloads\PDM File List.txt",delimiter=',',encoding='UTF-16')
    parts=pdm_df['File Name'].apply(lambda x: x.split('.')[0])
    # pdm_files=[]
    # for root, dirs, files in os.walk(r"C:\UCT-CORP-ePDM"):
    #     if any('AJARABANI'.lower()==item.lower() for item in dirs):
    #             pass
    #     print(root,dirs,files)
    #     pdm_files.extend(files)
    # pdm_parts=[i.split('.')[0] for i in pdm_files]
    chromeOptions = webdriver.ChromeOptions()
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
    res_df['PDM Y/N']=res_df['PN'].apply(lambda x: 'Yes' if any(x in part for part in parts) else 'No')
    res_df=res_df[['link','PN','TIER','COST','PDM Y/N']]
    xl.books.active.sheets.add(after='Sheet1',name='Test')
    print(res_df)
    print('processed in {} secs'.format(round(time.time()-start,2)))
    sht=xl.books.active.sheets['Test']
    sht.range('A1').options(
        index=False).value = res_df
    sht.range('F1').value='Image'
    rnge = sht.range('F1:F{}'.format(len(res_df)+2))
    sht_name=sht.name
    rnge.row_height=30
    rnge.column_width=30
    l = sht.range('F2').left+10/4
    for rn,i in enumerate(res_df['PN']):
        rn+=1
        local_path = r"C:\Users\ajarabani\Downloads\{}.png".format(i)
        xl.books.active.sheets[sht_name].pictures.add(
            image=local_path, name=f'{i} {rn}', left=l, top=(rn*30)+2, height=27)
    for i in res_df['PN'].unique():
        local_path = r"C:\Users\ajarabani\Downloads\{}.png".format(i)
        os.remove(local_path)