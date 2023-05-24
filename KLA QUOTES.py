import warnings,re,glob,os
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
import pandas as pd
import xlwings as xl
import sys
path = r'\\CHAFS01\ChandlerBU\Quoting\KLA_Tencor\Quoting WIP'
xlm = glob.glob(path + '/**/*xlsx',recursive=True)
xlm.sort(key=os.path.getmtime,reverse=True)
ft = pd.DataFrame(xlm)
ft.columns = ['Files']
def assign_pn(i1,x1,n1):
    dt = pd.read_excel(x1,sheet_name=n1,usecols='A:AZ')
    dt=dt.dropna(how='all',axis=0).dropna(how='all',axis=1)
    dt.reset_index(inplace=True,drop=True)
    cl=dt.columns[dt.isin(['PART#']).any()][0]
    ft.loc[i1,'PN']=dt.loc[dt.loc[dt[cl]=='PART#'].index[0]+1,cl]
for i in ft['Files'].index:
    try:
        x=ft.iloc[i,0]
        xl=pd.ExcelFile(x)
        for n in xl.sheet_names:
            if re.fullmatch(r'(?i)COSTBOM',n):
                assign_pn(i,x,n)
                break
        if not re.fullmatch(r'(?i)COSTBOM',n):
            for n in xl.sheet_names:    
                if re.fullmatch(r'(?i)Worksheet',n):
                    assign_pn(i,x,n)
                    break
            if not re.fullmatch(r'(?i)Worksheet',n):
                for n in xl.sheet_names:
                    if re.fullmatch(r'(?i)Data',n):
                        assign_pn(i,x,n)
                        break      
    except Exception as e:
        line = sys.exc_info()[-1].tb_lineno
        print(e,line,x)
        continue
ft =ft[ft['PN'].notna()]
ft.reset_index(inplace=True,drop=True)
ft.drop_duplicates(subset=['PN'],inplace=True)
cls=['TOP LEVEL', 'PART#','DESCRIPTION','VENDOR', 'QTY',
                            'COST EXT T1','COST EXT T2','COST EXT T3',
                            'COST EXT T5','COST EXT T7','COST EXT T9',
                            'COST EXT T10','COST EXT T15',
                            'COST EXT T20','COST EXT T25']
bm = pd.DataFrame(columns=cls)
def dt_scrub(df_kla):
    df_kla=df_kla.dropna(how='all',axis=0).dropna(how='all',axis=1)
    df_kla.columns=df_kla.columns.str.strip()
    df_kla = df_kla.filter(regex='(?i)^(?!QTY$|COST EA|QTY\.)',axis=1)
    df_kla.columns=df_kla[df_kla.isin(['PART#']).any(axis=1)].reset_index(drop=True).iloc[0]
    df_kla=df_kla.loc[~df_kla.isin(['PART#']).any(axis=1)]
    df_kla=df_kla.loc[:,pd.notna(df_kla.columns)]
    df_kla=df_kla.loc[:,df_kla.columns!=0]
    n=0
    for i in df_kla.columns:
        if isinstance(i,int)|isinstance(i,float):
            df_kla.columns.values[n]='COST EXT T' + str(round(i))
        n=n+1
    df_kla=df_kla.filter(regex='^.+(?!Unnamed).+$',axis=1)
    df_kla=df_kla.loc[df_kla['PART#'].notna()]
    df_kla=df_kla.filter(regex='(?i)^(?!QTY$)',axis=1)
    df_kla.rename(columns={'EXT':'QTY'},inplace=True)
    df_kla.dropna(how='all',axis=1,inplace=True)
    df_kla=df_kla.loc[:,~df_kla.columns.duplicated()]
    df_kla=df_kla.loc[df_kla['QTY']!=0,:]
    df_kla=df_kla.loc[df_kla.filter(regex='^COST EXT',axis=1).iloc[:,0]!=0,:]
    df_kla.insert(0,"TOP LEVEL",ft.loc[ft['Files']==x,'PN'].iloc[0])
    df_kla.columns=df_kla.columns.str.upper()
    df_kla=df_kla[df_kla.columns.intersection(cls)]
    return df_kla
def scrub_datatab(dtx):
    dtx=dtx.dropna(how='all',axis=0).dropna(how='all',axis=1)
    dtx.columns=dtx.columns.str.strip()
    dtx.iloc[0]=dtx.iloc[0].ffill()
    dtx = dtx.filter(regex='(?i)^(?!QTY$|Sell|UNIT/COST|QTY\.)',axis=1)
    dtx.iloc[0]=dtx.iloc[0].map(lambda x:int(re.search(r'(\d+)',x).group(1)) if bool(re.search(r'\d+',x)) else x)
    dtx.columns=dtx[dtx.isin(['PART#']).any(axis=1)].iloc[0]
    dtx=dtx.loc[~dtx.isin(['PART#']).any(axis=1)]
    dtx=dtx.loc[:,pd.notna(dtx.columns)]
    dtx=dtx.loc[:,dtx.columns!=0]
    n=0
    for i in dtx.columns:
        if isinstance(i,int)|isinstance(i,float):
            dtx.columns.values[n]='COST EXT T' + str(round(i))
        n=n+1
    dtx=dtx.filter(regex='^.+(?!Unnamed).+$',axis=1)
    dtx=dtx.loc[dtx['PART#'].notna()]
    dtx=dtx.filter(regex='^(?!QTY$)',axis=1)
    dtx.rename(columns={'UNIT':'QTY'},inplace=True)
    dtx.dropna(how='all',axis=1,inplace=True)
    dtx=dtx.loc[:,~dtx.columns.duplicated()]
    dtx=dtx.loc[dtx['QTY']!=0,:]
    dtx=dtx.loc[dtx['QTY'].notna(),:]
    dtx=dtx.loc[dtx.filter(regex='^COST EXT',axis=1).iloc[:,0]!=0,:]
    dtx.insert(0,"TOP LEVEL",ft.loc[ft['Files']==x,'PN'].iloc[0])
    dtx.columns=dtx.columns.str.upper()
    dtx=dtx[dtx.columns.intersection(cls)]
    return dtx
for x in ft['Files']:
    dt=pd.DataFrame()
    xl=pd.ExcelFile(x)
    for n in xl.sheet_names:
        if re.fullmatch(r'(?i)COSTBOM',n):
            dt = pd.read_excel(x,sheet_name=n,usecols='A:AZ')
            dt=dt_scrub(dt)
            break
    if not re.fullmatch(r'(?i)COSTBOM',n):
        for n in xl.sheet_names:    
            if re.fullmatch(r'(?i)Worksheet',n):
                dt = pd.read_excel(x,sheet_name=n,usecols='A:AZ')
                dt.columns=dt[dt.isin(['COST EA']).any(axis=1)].iloc[0]
                dt=dt_scrub(dt)
                break
        if not re.fullmatch(r'(?i)Worksheet',n):
            for n in xl.sheet_names:
                if re.fullmatch(r'(?i)Data',n):
                    dt=pd.read_excel(x,sheet_name=n,usecols='A:AZ')
                    dt=scrub_datatab(dt)
                    break
    bm = pd.concat([bm,dt],ignore_index=True)
    bm=bm[cls]
bc=['TOP LEVEL','PART#','DESCRIPTION','QTY','COST EXT T1']
BUILD_COST=pd.DataFrame(columns=bc)
for x in ft['Files']:
    CS=pd.DataFrame(columns=bc)
    xl=pd.ExcelFile(x)
    for n in xl.sheet_names:
        if re.fullmatch(r'(?i)Rollup',n):
            dt = pd.read_excel(x,sheet_name=n,usecols='A:M')
            dt = dt.dropna(how='all').dropna(how='all',axis=1)
            BUILD_HRS=dt.loc[dt.iloc[:,0].str.contains(r'(?i)hrs',na=False)].iloc[:,1].sum()
            pn=ft.loc[ft['Files']==x,'PN'].reset_index().iloc[0,1]
            CS.loc[0]=[pn,pn,'LABOR COST',1,BUILD_HRS*65]
            break
    if not re.fullmatch(r'(?i)Rollup',n):
        for n in xl.sheet_names:
            if re.fullmatch(r'(?i)Cost Model',n):
                dt = pd.read_excel(x,sheet_name=n,usecols='A:M')
                dt = dt.dropna(how='all').dropna(how='all',axis=1)
                dt.reset_index(drop=True,inplace=True)
                BUILD_HRS=dt.loc[:,dt.loc[0].str.contains(r'(?i)hrs',na=False)].loc[2].sum()
                pn=ft.loc[ft['Files']==x,'PN'].reset_index().iloc[0,1]
                CS.loc[0]=[pn,pn,'LABOR COST',1,BUILD_HRS*65]
                break
    BUILD_COST=pd.concat([BUILD_COST,CS],ignore_index=True)
keys=['COST EXT T2','COST EXT T3',
            'COST EXT T5','COST EXT T7','COST EXT T9',
            'COST EXT T10','COST EXT T15',
            'COST EXT T20','COST EXT T25']
for k in keys:
    BUILD_COST[k] = BUILD_COST['COST EXT T1']
SM=pd.concat([bm,BUILD_COST],ignore_index=True)
SM[['TOP LEVEL','PART#']] = SM[['TOP LEVEL','PART#']].apply(lambda x: x.str.strip())
SM=SM.loc[SM['PART#'].notna()]
SM.to_pickle('KLA QUOTES.PKL')
    # try:
# r1=r'(?<=REV\s\d_)(\d+-*\d*)'
# r2=r'(?<=PN\s)(\d+-*\d*)'
# r3=r'(?<=Q)\w+-*\w{3,5}(?:\s|_)(\d+-*\d+)'
# r4=r'(?<=KLA)\s(\d+-\d+)'
#         x=ft.loc[i,'Files']
#         if re.search(r1,x):
#             ft.loc[i,'PN']=re.search(r1,x).group(1)
#             continue
#         elif re.search(r2,x):
#             ft.loc[i,'PN']=re.search(r2,x).group(1)
#             continue
#         elif re.search(r3,x):
#             ft.loc[i,'PN']=re.search(r3,x).group(1)
#             continue
#         elif re.search(r4,x):
#             ft.loc[i,'PN']=re.search(r4,x).group(1)
#             continue
#         else:
#             ft.loc[i,'PN']=None