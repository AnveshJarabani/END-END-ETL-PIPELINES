import pandas as pd
import numpy as np
import pickle,subprocess,swifter
wl=pd.read_pickle('LBR M-18.PKL')
rout=pd.read_hdf('ST_BM_BR.H5',key='ROUT')
SM=pd.DataFrame()
SM['SM']=np.array(rout.loc[rout['Work Center'].str.contains(r'BRAKE|LASER|TRT'),"Material"].unique()).tolist()
SM.to_hdf('ST_BM_BR.H5',key='SM_PARTS',mode='a')
cst = pd.read_hdf('ST_BM_BR.H5',key='BR')
wl = wl.loc[:,['Fiscal year/period', 'Order - Material (Key)',
       'Order - Material (Text)', 'Order', 'Operation', 'Work Center',        
       'Standard Text Key', 'Operation Text', 'End Date',
       'Operation Quantity', 'Hours Worked', 'Labor Rate', 'Labor Cost',
       'Overhead Rate', 'Overhead Cost']]
wl = wl[(wl['Order - Material (Key)'] != '#') & (wl['Order'] != '#') & (wl['Standard Text Key'] != '#')]
cst['BUR_RATE'] *=1.15
wl = wl.merge(cst,left_on='Standard Text Key',right_on='ST KEY',how='left')
wl.drop(columns=['ST KEY'],axis=1,inplace=True)
wl = wl.assign(COST=lambda x: (x['BUR_RATE']*x['Hours Worked']))
pi = wl.pivot_table(index=["Order - Material (Key)","Order",'Standard Text Key',\
     'Operation Quantity'],values=["Hours Worked","COST"],aggfunc= np.sum)
pi.reset_index(inplace=True)
pi['ACT COST/EA'] = pi['COST']/pi['Operation Quantity']
pi['HRS/EA'] = pi['Hours Worked']/pi['Operation Quantity']
pi.replace([np.inf, -np.inf], np.nan, inplace=True)
pi.dropna(how='any',inplace=True)
pi=pi.loc[pi['COST']!=0]
pi=pi[['Order - Material (Key)', 'Order', 'Standard Text Key', 'ACT COST/EA', 'HRS/EA']]
def remove_outliers(group):
    mean = group.mean()  
    median = group.median()
    mad = np.median(np.abs(group - median))  
#     std = group.std()
    z_scores = 0.6745*np.abs((group - mean)/mad)
    return group[z_scores < 3.5]
# def remove_outliers(group):
#     Q1 = group.quantile(0.25)
#     Q3 = group.quantile(0.75)
#     IQR = Q3 - Q1
#     upper_bound = Q3 + 0.5*IQR
#     lower_bound = Q1 - 0.5*IQR
#     return group[(group > lower_bound) & (group < upper_bound)]
pi[['ACT COST/EA_t', 'HRS/EA_t']] = pi.groupby(['Order - Material (Key)', 'Standard Text Key'])[['ACT COST/EA', 'HRS/EA']].transform(remove_outliers)
pi_temp = pi.pivot_table(index=["Order - Material (Key)",'Standard Text Key'],values = ['ACT COST/EA'],aggfunc= np.mean)
pi_temp.reset_index(inplace=True)
pi_temp.columns=['MAT_TEMP','STKEY_TEMP','COST/EA_AVG']
pi=pi.merge(pi_temp,left_on=['Order - Material (Key)','Standard Text Key'],right_on=['MAT_TEMP','STKEY_TEMP'],how='left')
pi=pi.loc[(pi['COST/EA_AVG']/5 < pi['ACT COST/EA']) & (pi['COST/EA_AVG']*5 > pi['ACT COST/EA'])]
pi=pi.pivot_table(index=["Order - Material (Key)",'Standard Text Key'],values = ['HRS/EA','ACT COST/EA'],aggfunc= np.mean)
pi.reset_index(inplace=True)
rout.columns=rout.columns.str.strip()
rt=rout.loc[:,['Material','Standard Text Key','Base Quantity','Work Center','Setup','Unit_Setup','Labor Run','Unit_Labor Run']]
rt=rt.loc[rout['Unit_Setup']!='#']
QTY=wl[['Order - Material (Key)','Order','Operation Quantity']]
QTY=QTY.drop_duplicates()
QTY = QTY.pivot_table(index=['Order - Material (Key)'],values=['Operation Quantity'],aggfunc=np.mean)
QTY.reset_index(inplace=True) 
rt = rt.merge(QTY,left_on='Material',right_on='Order - Material (Key)',how='left')
rt.drop(columns=['Order - Material (Key)'],axis=1,inplace=True)
rt.loc[(rt['Operation Quantity'].isnull())&(rt['Work Center'].str.contains(r'BRAKE|LASER|TRT|SAW')),'Base Quantity'] = 10
rt.loc[(rt['Operation Quantity']!=1),'Base Quantity']=10
for i in rt.loc[rt['Base Quantity']==10,'Material'].unique():
     rt.loc[rt['Material']==i,'Base Quantity']=10
rt.loc[rt['Operation Quantity'].isnull(),'Operation Quantity'] = rt['Base Quantity']
rt['PLN HR/EA'] = ((rt['Setup'] + rt['Labor Run'])/rt['Base Quantity']).where(rt['Unit_Labor Run'] == 'H',\
                 (rt['Setup'] + (rt['Labor Run']/60))/rt['Base Quantity'])
rt = rt.pivot_table(index=['Material','Standard Text Key'],values=['PLN HR/EA'],aggfunc=np.sum)
rt.reset_index(inplace=True)
pi3 = pi.pivot_table(index=["Order - Material (Key)"],values=['ACT COST/EA','HRS/EA'],aggfunc= np.sum)
pi3.reset_index(inplace=True)
rt = rt.merge(cst,left_on='Standard Text Key',right_on='ST KEY',how='left')
rt.drop(columns=['ST KEY'],axis=1,inplace=True)
rt['PLN COST/EA'] = rt['PLN HR/EA']*rt['BUR_RATE']
rt = rt.pivot_table(index=['Material'],values=['PLN COST/EA'],aggfunc=np.sum)
rt.reset_index(inplace=True)
rt = rt.merge(pi3,left_on='Material',right_on='Order - Material (Key)',how='left')
rt['ACT COST/EA'] = rt['ACT COST/EA'].replace("",pd.NA).fillna(rt['PLN COST/EA'])
rt.loc[(rt['ACT COST/EA'] ==0) | (rt['ACT COST/EA'] < .6*rt['PLN COST/EA'] ),'ACT COST/EA'] = rt['PLN COST/EA']
rt.drop(columns=['Order - Material (Key)'],axis=1,inplace=True)
rt.to_hdf('LBR.H5',key='ACT_V_PL_CST',mode='a')
print('LBR.H5 ACT_V_PL_CST COMPLETE')