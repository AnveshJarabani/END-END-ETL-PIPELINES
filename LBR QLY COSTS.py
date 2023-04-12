import pandas as pd
import numpy as np
wl=pd.read_pickle('LBR M-18.PKL')
cst=pd.read_hdf('ST_BM_BR.H5','BR')
wl = wl.loc[:,['Fiscal year/period', 'Order - Material (Key)',
       'Order - Material (Text)', 'Order', 'Operation', 'Work Center',        
       'Standard Text Key', 'Operation Text', 'End Date',
       'Operation Quantity', 'Hours Worked', 'Labor Rate', 'Labor Cost',
       'Overhead Rate', 'Overhead Cost']]
wl = wl.loc[(wl['Order - Material (Key)'] != '#')&(wl['Order'] != '#')&(wl['Standard Text Key'] != '#')]
wl['YR']=wl['Fiscal year/period'].str.extract(r'(\d{2})$')
wl['MONTH']=wl['Fiscal year/period'].str.extract(r'\b(\d{2})\b')
wl=wl.loc[wl['MONTH'].notna()].reset_index()
wl['MONTH']=wl['MONTH'].astype('int')
wl.loc[(wl['MONTH']==1)|(wl['MONTH']==2)|(wl['MONTH']==3),'QTR']='Q1'
wl.loc[(wl['MONTH']==4)|(wl['MONTH']==5)|(wl['MONTH']==6),'QTR']='Q2'
wl.loc[(wl['MONTH']==7)|(wl['MONTH']==8)|(wl['MONTH']==9),'QTR']='Q3'
wl.loc[(wl['MONTH']==10)|(wl['MONTH']==11)|(wl['MONTH']==12),'QTR']='Q4'
wl.sort_values(by=['YR','MONTH'],ascending=False,inplace=True)
wl['Q+YR']= wl['QTR'].astype(str)+" "+wl['YR'].astype(str)
cst['BUR_RATE'] *=1.15
wl = wl.merge(cst,left_on='Standard Text Key',right_on='ST KEY',how='left')
wl.drop(columns=['ST KEY'],axis=1,inplace=True)
wl = wl.assign(COST=lambda x: (x['BUR_RATE']*x['Hours Worked']))
pi = wl.pivot_table(index=["Order - Material (Key)","Order",'Standard Text Key',\
     'Operation Quantity'],values=["COST"],aggfunc= np.sum)
pi.reset_index(inplace=True)
pi=pi.merge(wl[['Order','Q+YR']],how='left')
pi['ACT COST/EA'] = pi['COST']/pi['Operation Quantity']
pi.replace([np.inf, -np.inf], np.nan, inplace=True)
pi.dropna(how='any',inplace=True)
pi2 = pi.pivot_table(index=['Q+YR',"Order - Material (Key)",'Standard Text Key'],values = ['ACT COST/EA'],aggfunc= np.mean)
pi2.reset_index(inplace=True)
pi3 = pi2.pivot_table(index=['Q+YR',"Order - Material (Key)"],values=['ACT COST/EA'],aggfunc= np.sum)
pi3.reset_index(inplace=True)
temp=wl[['Q+YR','MONTH','YR']].drop_duplicates()
pi3=pi3.merge(temp,left_on='Q+YR',right_on='Q+YR',how='left')
pi3.sort_values(by=['YR','MONTH'],ascending=True,inplace=True)
pi3=pi3[['Q+YR','Order - Material (Key)','ACT COST/EA']]
pi3.columns=['Q+YR','PN','ACT LBR COST/EA']
pi3.drop_duplicates(inplace=True)
for i in pi3['PN'].unique():
    pi3.loc[pi3['PN']==i,'LAST Q COST']=pi3.loc[pi3['PN']==i,'ACT LBR COST/EA'].shift(1)
pi3['DELTA %']=(pi3['ACT LBR COST/EA']-pi3['LAST Q COST'])/pi3['LAST Q COST']
pi3[['ACT LBR COST/EA','DELTA %']]=pi3[['ACT LBR COST/EA','DELTA %']].round(2)
pi3.replace([np.inf,-np.inf],np.nan,inplace=True)
pi3['DELTA %'].replace(np.nan,0,inplace=True)
pi3.dropna(how='all',inplace=True)
pi3.to_hdf('LBR.H5',key='Q_TRENDS',mode='a')
print('LBR.H5 Q_TRENDS COMPLETE')