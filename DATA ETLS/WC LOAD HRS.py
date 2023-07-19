import pandas as pd
import numpy as np
wl=pd.read_pickle('../PKL/RAW_LBR.PKL')
cst=pd.read_hdf('../H5/ST_BM_BR.H5','BR')
wl = wl.loc[:,['Fiscal year/period', 'Order - Material (Key)',
       'Order - Material (Text)', 'Order', 'Operation', 'Work Center',        
       'Standard Text Key', 'Operation Text', 'End Date',
       'Operation Quantity', 'Hours Worked', 'Labor Rate', 'Labor Cost',
       'Overhead Rate', 'Overhead Cost']]
wl = wl.loc[(wl['Order - Material (Key)'] != '#')&(wl['Order'] != '#')&(wl['Standard Text Key'] != '#')]
wl['YR']=wl['Fiscal year/period'].str.extract(r'(\d{2})$')
wl['MONTH']=wl['Fiscal year/period'].str.extract(r'\b(\d{2})\b')
wl['X']=wl['MONTH'].astype(str)+" "+wl['YR'].astype(str)
wl=wl.loc[wl['MONTH'].notna()].reset_index(drop=True)
wl['MONTH']=wl['MONTH'].astype('int')
pi = wl.pivot_table(index=['YR','MONTH','X','Work Center'],values=["Hours Worked"],aggfunc= np.sum)
pi.reset_index(inplace=True)
pi.replace([np.inf, -np.inf], np.nan, inplace=True)
pi.dropna(how='any',inplace=True)
pi2 = pi.pivot_table(index=['Work Center'],values = ['Hours Worked'],aggfunc= np.mean)
pi2.reset_index(inplace=True)
pi2.columns=['WC_mean','MONTHLY AVG. HRS']
pi3=pi.merge(pi2,left_on='Work Center',right_on='WC_mean',how='left')
pi3.drop(columns=['WC_mean'],inplace=True)
cst=cst[['WC','BUR_RATE']].drop_duplicates(ignore_index=True)
pi3 = cst.merge(pi3,left_on='WC',right_on='Work Center',how='left')
pi.sort_values(by=['YR','MONTH'],ascending=False,inplace=True,)
pi3.drop(columns=['YR','MONTH','WC','BUR_RATE'],axis=1,inplace=True)
pi3.dropna(inplace=True)
pi3[['Hours Worked','MONTHLY AVG. HRS']]=pi3[['Hours Worked','MONTHLY AVG. HRS']].round(2)
pi3.to_hdf('../H5/LBR.H5',key='WC_LOAD',mode='a')
print('LBR.H5 WC_LOAD COMPLETE')