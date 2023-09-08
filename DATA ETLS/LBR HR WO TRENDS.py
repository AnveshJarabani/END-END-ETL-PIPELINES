import pandas as pd
import numpy as np
wl=pd.read_pickle('../PKL/RAW_LBR.PKL')
rout=pd.read_hdf('../H5/ST_BM_BR.H5',key='ROUT') 
BURCOST=pd.read_hdf('../H5/ST_BM_BR.H5',key='BR') 
BURCOST.dropna(inplace=True,how='all')
wl = wl[(wl['PART_NUMBER'] != '#') &
    (wl['WORK_ORDER'] != '#') & (wl['STD_KEY'] != '#')]
def filteroverheadkeys(x,y):
     x = x.merge(BURCOST,left_on=y,right_on='ST KEY',how='left')
     x.drop(columns=['ST KEY'],axis=1,inplace=True)
     x=x.loc[x['BUR_RATE']!=0]
     return x
wl=filteroverheadkeys(wl,'STD_KEY')
pi = wl.pivot_table(index=["PART_NUMBER",
     "WORK_ORDER",'OP_QTY'],values=["HRS_WORKED"],aggfunc= np.sum)
pi.reset_index(inplace=True)
pi['HRS/EA'] = pi['HRS_WORKED']/pi['OP_QTY']
pi.replace([np.inf, -np.inf], np.nan, inplace=True)
pi.dropna(how='any',inplace=True)
pi.drop_duplicates(subset=['WORK_ORDER'],keep='last',inplace=True)
calendar=pd.read_pickle("../PKL/FISCAL_CAL.PKL")
PERIOD=wl[['END_DATE','WORK_ORDER']].sort_values(by='END_DATE')
PERIOD.drop_duplicates(subset=['WORK_ORDER'],keep='last',inplace=True)
pk=PERIOD.merge(pi,how='left',on=['WORK_ORDER'],validate='1:1')
pk['HRS/EA']=pk['HRS/EA'].astype(float)
pk['WORK_ORDER']=pk['WORK_ORDER'].astype(str)
pk.drop_duplicates(subset=['WORK_ORDER'],keep='last',inplace=True)
pk.to_hdf('../H5/LBR.H5',key='WO_TRENDS',mode='a')
# rout.columns=['PLANT','MATERIAL','OP_NUMBER','STD_KEY','BASE_QUANTITY','UNIT','SETUP','SETUP_UNIT','RUN','RUN_UNIT']
rt=rout.loc[rout['SETUP_UNIT']!='#']
wl.columns
QTY = wl.pivot_table(index=['PART_NUMBER'],values=['OP_QTY'],aggfunc=np.mean)
QTY.reset_index(inplace=True) 
rt = rt.merge(QTY,left_on='MATERIAL',right_on='PART_NUMBER',how='left')
rt.drop(columns=['PART_NUMBER'],axis=1,inplace=True)
rt.loc[rt['OP_QTY'].isnull(),'OP_QTY'] = rt['BASE_QUANTITY']
rt['PLN HR/EA'] = ((rt['SETUP'] + rt['RUN'])/rt['BASE_QUANTITY']).where(rt['RUN_UNIT'] == 'H',\
                 (rt['SETUP'] + (rt['RUN']/60))/rt['BASE_QUANTITY'])
rt = rt.merge(BURCOST,left_on='STD_KEY',right_on='ST KEY',how='left')
rt.drop(columns=['ST KEY'],axis=1,inplace=True)
rt=rt.loc[rt['BUR_RATE']!=0]
rt = rt.pivot_table(index=['MATERIAL'],values=['PLN HR/EA'],aggfunc=np.sum)
rt.reset_index(inplace=True)
rt['PLN HR/EA']=rt['PLN HR/EA'].astype(float)
rt.select_dtypes(include=[float]).astype(np.float16)
rt.select_dtypes(include=[int]).astype(np.int8) 
rt.to_hdf('../H5/LBR.H5',key='PLN_HR',mode='a')
print('LBR.H5 PLN_HR COMPLETE')