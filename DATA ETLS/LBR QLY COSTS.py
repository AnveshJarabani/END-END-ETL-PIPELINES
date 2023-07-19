import pandas as pd
import numpy as np
wl=pd.read_pickle('../PKL/RAW_LBR.PKL')
cst=pd.read_hdf('../H5/ST_BM_BR.H5','BR')
wl = wl.loc[(wl['PART_NUMBER'] != '#')&(wl['WORK_ORDER'] != '#')&(wl['STD_KEY'] != '#')]
wl['END_DATE']=pd.to_datetime(wl['END_DATE'])
cal=pd.read_pickle("../PKL/FISCAL_CAL.PKL")
wl=wl.merge(cal,left_on='END_DATE',right_on='DATE',how='left')
wl=wl.sort_values(by='END_DATE',ascending=False)
cst['BUR_RATE'] *=1.15
wl = wl.merge(cst,left_on='STD_KEY',right_on='ST KEY',how='left')
wl.drop(columns=['ST KEY'],axis=1,inplace=True)
wl = wl.assign(COST=lambda x: (x['BUR_RATE']*x['HRS_WORKED']))
pi = wl.pivot_table(index=["PART_NUMBER","WORK_ORDER",'STD_KEY',\
     'OP_QTY'],values=["COST"],aggfunc= np.sum)
pi.reset_index(inplace=True)
pi=pi.merge(wl[['WORK_ORDER','QTR+YR']],how='left')
pi['ACT COST/EA'] = pi['COST']/pi['OP_QTY']
pi.replace([np.inf, -np.inf], np.nan, inplace=True)
pi.dropna(how='any',inplace=True)
pi2 = pi.pivot_table(index=['QTR+YR',"PART_NUMBER",'STD_KEY'],values = ['ACT COST/EA'],aggfunc= np.mean)
pi2.reset_index(inplace=True)
pi3 = pi2.pivot_table(index=['QTR+YR',"PART_NUMBER"],values=['ACT COST/EA'],aggfunc= np.sum)
pi3.reset_index(inplace=True)
pi3=pi3[['QTR+YR','PART_NUMBER','ACT COST/EA']]
pi3.columns=['QTR+YR','PN','ACT LBR COST/EA']
pi3.drop_duplicates(inplace=True)
for i in pi3['PN'].unique():
    pi3.loc[pi3['PN']==i,'LAST Q COST']=pi3.loc[pi3['PN']==i,'ACT LBR COST/EA'].shift(1)
pi3['DELTA %']=(pi3['ACT LBR COST/EA']-pi3['LAST Q COST'])/pi3['LAST Q COST']
pi3[['ACT LBR COST/EA','DELTA %']]=pi3[['ACT LBR COST/EA','DELTA %']].round(2)
pi3.replace([np.inf,-np.inf],np.nan,inplace=True)
pi3['DELTA %'].replace(np.nan,0,inplace=True)
pi3.dropna(how='all',inplace=True)
pi3.to_hdf('../H5/LBR.H5',key='Q_TRENDS',mode='a')
print('LBR.H5 Q_TRENDS COMPLETE')