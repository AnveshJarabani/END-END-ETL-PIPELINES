import pandas as pd
import numpy as np
wl=pd.read_pickle('LBR M-18.PKL')
rout=pd.read_hdf('ST_BM_BR.H5',key='ROUT')
BUR_RATE = pd.read_hdf('ST_BM_BR.H5',key='BR')
wl = wl.loc[:,['Fiscal year/period', 'Order - Material (Key)',
       'Order - Material (Text)', 'Order', 'Operation', 'Work Center',        
       'Standard Text Key', 'Operation Text', 'End Date',
       'Operation Quantity', 'Hours Worked', 'Labor Rate', 'Labor Cost',
       'Overhead Rate', 'Overhead Cost']]
wl = wl[(wl['Order - Material (Key)'] != '#') & (wl['Order'] != '#') & (wl['Standard Text Key'] != '#')]
pi = wl.pivot_table(index=["Order - Material (Key)","Order",'Work Center',
     'Operation Quantity'],values=["Hours Worked"],aggfunc= np.sum)
pi.reset_index(inplace=True)
pi.replace([np.inf, -np.inf], np.nan, inplace=True)
pi.dropna(how='any',inplace=True)
pi=pi.loc[pi['Hours Worked']!=0]
pi = pi.pivot_table(index=["Order - Material (Key)",'Order','Operation Quantity','Work Center'],values = ['Hours Worked'],aggfunc= np.sum)
pi.reset_index(inplace=True)
BUR_RATE['BUR_RATE'] *=1.15
pi = pi.merge(BUR_RATE,left_on='Work Center',right_on='WC',how='left')
pi = pi.assign(COST=lambda x: (x['BUR_RATE']*x['Hours Worked']))
pi.drop(columns=['WC','ST KEY'],axis=1,inplace=True)
pi['ACT COST/EA'] = pi['COST']/pi['Operation Quantity']
pi_temp=pi.pivot_table(index=['Order - Material (Key)','Work Center'],values=['ACT COST/EA'],aggfunc=np.mean)
pi_temp.reset_index(inplace=True)
pi_temp.columns=['MAT_TEMP','WC_TEMP','COST/EA_AVG']
pi=pi.merge(pi_temp,left_on=['Order - Material (Key)'],right_on=['MAT_TEMP'],how='left')
pi=pi.loc[(pi['COST/EA_AVG']/5 < pi['ACT COST/EA']) & (pi['COST/EA_AVG']*5 > pi['ACT COST/EA'])]
pi=pi.pivot_table(index=["Order - Material (Key)",'Work Center'],values = ['ACT COST/EA'],aggfunc= np.mean)
pi.reset_index(inplace=True)
pi3 = pi.pivot_table(index=["Order - Material (Key)"],values=['ACT COST/EA'],aggfunc= np.sum)
pi3.reset_index(inplace=True)
rout.columns=rout.columns.str.strip()
rt=rout.loc[:,['Material','Standard Text Key','Base Quantity','Work Center','Setup','Unit_Setup','Labor Run','Unit_Labor Run']]
rt=rt.loc[rout['Unit_Setup']!='#']
QTY=wl[['Order - Material (Key)','Order','Operation Quantity']].drop_duplicates()
QTY = QTY.pivot_table(index=['Order - Material (Key)'],values=['Operation Quantity'],aggfunc=np.mean)
QTY.reset_index(inplace=True) 
rt = rt.merge(QTY,left_on='Material',right_on='Order - Material (Key)',how='left')
rt.drop(columns=['Order - Material (Key)'],axis=1,inplace=True)
rt.loc[(rt['Operation Quantity'].isnull())&(rt['Work Center'].str.contains(r'BRAKE|LASER|TRT|SAW')),'Base Quantity'] = 10
for i in rt.loc[rt['Base Quantity']==10,'Material'].unique():
     rt.loc[rt['Material']==i,'Base Quantity']=10
rt.loc[rt['Operation Quantity'].isnull(),'Operation Quantity'] = rt['Base Quantity']
rt['PLN HR/EA'] = ((rt['Setup'] + rt['Labor Run'])/rt['Operation Quantity']).where(rt['Unit_Labor Run'] == 'H',\
                 (rt['Setup'] + (rt['Labor Run']/60))/rt['Operation Quantity'])
rt = rt.pivot_table(index=['Material','Work Center'],values=['PLN HR/EA'],aggfunc=np.sum)
rt.reset_index(inplace=True)
rt = rt.pivot_table(index=['Material','Work Center'],values=['PLN HR/EA'],aggfunc=np.sum)
rt.reset_index(inplace=True)
pi3 = pi.pivot_table(index=["Order - Material (Key)"],values=['ACT COST/EA'],aggfunc= np.sum)
pi3.reset_index(inplace=True)
rt = rt.merge(BUR_RATE,left_on='Work Center',right_on='WC',how='left')
rt.drop(columns=['WC','ST KEY'],axis=1,inplace=True)
rt['PLN COST/EA'] = rt['PLN HR/EA']*rt['BUR_RATE']
rt = rt.pivot_table(index=['Material'],values=['PLN COST/EA'],aggfunc=np.sum)
rt.reset_index(inplace=True)
rt = rt.merge(pi3,left_on='Material',right_on='Order - Material (Key)',how='left')
rt['ACT COST/EA'] = rt['ACT COST/EA'].replace("",pd.NA).fillna(rt['PLN COST/EA'])
rt.loc[(rt['ACT COST/EA'] ==0) | (rt['ACT COST/EA'] < .6*rt['PLN COST/EA'] ),'ACT COST/EA'] = rt['PLN COST/EA']
rt.drop(columns=['Order - Material (Key)'],axis=1,inplace=True)
rt.to_hdf('TEST.H5',key='LBR_CST',mode='a')