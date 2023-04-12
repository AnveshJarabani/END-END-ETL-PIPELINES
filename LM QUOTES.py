import re,glob,os,warnings
import numpy as np
from time import time
import pandas as pd
import openpyxl as opxl
import multiprocessing as mp
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
path = r"\\chafs01\ChandlerBU\Quoting\Lam Research\LATEST QUOTES PER PN"
xlm = glob.glob(path + '/*xlsm')
xlm.sort(key=os.path.getmtime,reverse=True)
cutoff=time()-(60*60*24*365*3) #365 = 365 days prior to current date as cut off selection
# cutoff=os.path.getmtime('QUOTES.H5')
xlm=[i for i in xlm if  os.path.getmtime(i)>cutoff]
ft = pd.DataFrame(xlm)
ft.columns = ['Files']
ft['PN'] = ft['Files'].str.extract(r'(\w*-*\w*-\w*)',expand = True)
ft =ft[~ft['Files'].str.contains(r'(RMA+|REWORK+|RWK+)')]
ft.drop_duplicates('PN',inplace=True,ignore_index=True)
bm = pd.DataFrame(columns=['TOP LEVEL', 'Lam Part#','Description', 'EXT QTY',
                            'SUPPLIER', 'UnitCost','Ext$$','UnitCost.1','Ext$$.1',
                            'UnitCost.2','Ext$$.2',
                            'UnitCost.3','Ext$$.3',
                            'UnitCost.4','Ext$$.4'])
bm.columns = bm.columns.str.upper()
BOM_STRING=r'costed bom'
def costed_bom(x):
    try:
        xl=pd.ExcelFile(x)
        for n in xl.sheet_names:
            if re.search(BOM_STRING,n,flags=re.IGNORECASE):
                sheet=n
                break 
        if sheet is None:
            return None
        # wb=opxl.load_workbook(x,data_only=True)
        dt = pd.read_excel(x,sheet_name=sheet,usecols='A:AB',skiprows=[0],engine='openpyxl')
        dt.columns = dt.columns.str.upper()
        dt.insert(0,"TOP LEVEL",ft.loc[ft['Files']==x,'PN'].iloc[0])
        print(re.findall(r'(\w*-*\w*-\w*)',x)[0])
        return dt
    except Exception as e:
        print(re.findall(r'(\w*-*\w*-\w*)',x)[0]+' skipped',e)
CS=pd.DataFrame(columns=['TOP LEVEL','LAM PART#','DESCRIPTION','QTY/ASSY','TOTAL MATERIAL COST','ASSY HRS','TEST HRS'])
SUPPLIER_STRING=r'supplier cost'
def supplier_cost(x):
    try:    
        xl=pd.ExcelFile(x)
        for n in xl.sheet_names:
            if re.search(SUPPLIER_STRING,n,flags=re.IGNORECASE):
                sheet=n
                break 
        dt = pd.read_excel(x,sheet_name=sheet,usecols='A:M',engine='openpyxl')
        dt = dt.dropna(how='all').dropna(how='all',axis=1)
        dt.columns=dt.loc[dt.iloc[:,0].str.contains('LAM PART',flags=re.IGNORECASE,na=False)].iloc[0]
        dt.columns = dt.columns.str.upper()
        dt.columns=dt.columns.str.strip()
        if any(dt.columns.str.contains('UNIT COST',flags=re.IGNORECASE)):
            dt.rename(columns={'UNIT COST':'TOTAL MATERIAL COST'})
        dt.insert(0,"TOP LEVEL",ft.loc[ft['Files']==x,'PN'].iloc[0])
        dt=dt[['TOP LEVEL','LAM PART#','DESCRIPTION','QTY/ASSY','TOTAL MATERIAL COST','ASSY HRS','TEST HRS']]
        print(re.findall(r'(\w*-*\w*-\w*)',x)[0] + 'supplier cost')
        return dt
    except Exception as e:
        print(re.findall(r'(\w*-*\w*-\w*)',x)[0]+' supplier cost skipped',e)
if __name__=='__main__':
    pool=mp.Pool(processes=mp.cpu_count())
    bm_pool=pool.map(costed_bom,list(ft['Files']))
    bm=pd.concat(bm_pool)
    bm = bm[bm.iloc[:,4] != 'ZZ']
    bm.dropna(subset=['LAM PART#',"UNITCOST"],inplace=True)
    bm =  bm[bm['UNITCOST'] != 0]
    bm = bm.iloc[:,:15].reset_index(drop=True)
    cs_pool=pool.map(supplier_cost,list(ft['Files']))
    CS=pd.concat(cs_pool)

    CS=CS.fillna(0)
    CS.reset_index(inplace=True,drop=True)
    CS=CS.applymap(lambda x:x.strip() if isinstance(x,str) else x)
    BUILD_HRS=CS[['TOP LEVEL','ASSY HRS','TEST HRS']]
    BUILD_HRS=BUILD_HRS[~BUILD_HRS.iloc[:,1].apply(lambda x: isinstance(x,str))]
    BUILD_HRS=BUILD_HRS[~BUILD_HRS.iloc[:,2].apply(lambda x: isinstance(x,str))]
    BUILD_HRS['BUILD HRS']=BUILD_HRS.iloc[:,1]+BUILD_HRS.iloc[:,2]
    BUILD_HRS=BUILD_HRS.iloc[:,[0,3]]
    BUILD_HRS.drop_duplicates(subset=['TOP LEVEL'],inplace=True)
    BUILD_HRS.reset_index(drop=True,inplace=True)
    BUILD_HRS['EXT QTY']=1
    BUILD_HRS['UNITCOST']=BUILD_HRS['BUILD HRS']*85
    XL=['EXT$$','UNITCOST.1','EXT$$.1','UNITCOST.2','EXT$$.2','UNITCOST.3','EXT$$.3','UNITCOST.4','EXT$$.4']
    for i in range(0,9):
        BUILD_HRS[XL[i]]=BUILD_HRS['UNITCOST']
    BUILD_HRS.drop(['BUILD HRS'],axis=1,inplace=True)
    CS=CS[CS['LAM PART#'].str.fullmatch(r'\d*-*\d*-\d*',na=False)]
    CS=CS[CS['DESCRIPTION']!=0]
    CS=CS[CS['TOP LEVEL']!=CS['LAM PART#']]
    CS=CS.loc[~CS['DESCRIPTION'].str.contains(r'FAI|Program|Art|silk',na=False,flags=re.IGNORECASE)]
    try:
        CS=CS[~CS['QTY/ASSY'].str.contains(r'FAI|Program|Art|silk',na=False,flags=re.IGNORECASE)]
        CS=CS[~CS['QTY/ASSY'].apply(lambda x: isinstance(x,str))]
        CS=CS[CS[['QTY/ASSY','TOTAL MATERIAL COST']].sum(axis=1)!=0]
        CS['EXT']=CS['TOTAL MATERIAL COST']*CS['QTY/ASSY']
    except:
        pass
    SM = pd.DataFrame(columns=['TOP LEVEL', 'Lam Part#','EXT QTY',
                                'UnitCost','Ext$$','UnitCost.1','Ext$$.1',
                                'UnitCost.2','Ext$$.2',
                                'UnitCost.3','Ext$$.3',
                                'UnitCost.4','Ext$$.4'])
    SM.columns=SM.columns.str.upper()
    try:
        CS=CS[['TOP LEVEL','LAM PART#','QTY/ASSY','TOTAL MATERIAL COST','EXT']]
        CS.columns=['TOP LEVEL','LAM PART#','EXT QTY','UNITCOST','EXT$$']
        TEMP=CS.drop_duplicates(subset=['TOP LEVEL','LAM PART#'])
        CS['TC']=CS.groupby(['TOP LEVEL','LAM PART#']).cumcount()+1
    except:
        pass
    SUBPARTS=pd.concat([SM,CS])
    SUBPARTS.reset_index(drop=True,inplace=True)
    # SM=pd.concat([SM,TEMP])
    SM.reset_index(drop=True,inplace=True)
    CL=['UNITCOST.1','EXT$$.1','UNITCOST.2','EXT$$.2','UNITCOST.3','EXT$$.3','UNITCOST.4','EXT$$.4']
    for y in range(2,6):
        for TL in SM['TOP LEVEL'].unique():
            for LM in SM['LAM PART#'].unique():
                if SUBPARTS.loc[(SUBPARTS['TC']==y)&(SUBPARTS['TOP LEVEL']==TL)&(SUBPARTS['LAM PART#']==LM)].empty:
                    continue
                else: 
                    T=SUBPARTS.loc[(SUBPARTS['TC']==y)& (SUBPARTS['TOP LEVEL']==TL) & (SUBPARTS['LAM PART#']==LM),'UNITCOST'].reset_index(drop=True)
                    Q=SUBPARTS.loc[(SUBPARTS['TC']==y)& (SUBPARTS['TOP LEVEL']==TL) & (SUBPARTS['LAM PART#']==LM),'EXT$$'].reset_index(drop=True)
                    SM.loc[(SM['TOP LEVEL']==TL)&(SM['LAM PART#']==LM),CL[(y-2)*2]]=T.loc[0]
                    SM.loc[(SM['TOP LEVEL']==TL)&(SM['LAM PART#']==LM),CL[((y-1)*2)-1]]=Q.loc[0]
    SM=pd.concat([BUILD_HRS,SM],axis=0,ignore_index=True)
    SM=pd.concat([bm,SM],axis=0,ignore_index=True)
    SM[['TOP LEVEL','LAM PART#']] = SM[['TOP LEVEL','LAM PART#']].apply(lambda x: x.str.strip())
    SM=SM.loc[(SM['UNITCOST']!=0)|(SM['UNITCOST'].notna())]
    SM_OLD=pd.read_hdf('QUOTES.H5',key='LAM')
    # REMOVE COMMON TOOLS IN OLD TOOLS.
    CM_LST=list(set(SM_OLD['TOP LEVEL'].unique()).intersection(SM['TOP LEVEL'].unique()))
    SM_OLD=SM_OLD.loc[~SM_OLD['TOP LEVEL'].isin(CM_LST)]
    SM=pd.concat([SM,SM_OLD],ignore_index=True)
    SM.loc[SM['LAM PART#'].isna(),'LAM PART#']='LABOR COST'
    SM.select_dtypes(include=[float]).astype(np.float16)
    SM.select_dtypes(include=[int]).astype(np.int8)
    SM.to_hdf('QUOTES.H5',key='LAM')