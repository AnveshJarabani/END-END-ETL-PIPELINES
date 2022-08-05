import pandas as pd
import xlwings as xl
import numpy as np
ws = xl.books.active.sheets.active
Hrs_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Labor Hours Q2 21 - Q2 22.xlsx"
rout_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\SAP ROUTING 3321 & 22.xlsx"
cst_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\STKEY_BURCOST.xlsx"
Final_pkl = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\ACT VS PLN LABOR COST.PKL"
wl = pd.read_excel(Hrs_PATH,sheet_name='Employee Labor Hours',usecols='A:AR',skiprows=[0])
rout = pd.read_excel(rout_PATH,sheet_name='Sheet1',usecols='C:S') 
cst = pd.read_excel(cst_PATH,sheet_name='Sheet1',usecols='A:B')
wl = wl.loc[:,['Fiscal year/period', 'Order - Material (Key)',
       'Order - Material (Text)', 'Order', 'Operation', 'Work Center',        
       'Standard Text Key', 'Operation Text', 'End Date',
       'Operation Quantity', 'Hours Worked', 'Labor Rate', 'Labor Cost',
       'Overhead Rate', 'Overhead Cost']]
wl = wl[(wl['Order - Material (Key)'] != '#') & (wl['Order'] != '#')]
cst['BUR_RATE'] *=1.1
wl = wl.merge(cst,left_on='Standard Text Key',right_on='ST KEY',how='left')
wl.drop(columns=['ST KEY'],axis=1,inplace=True)
wl = wl.assign(COST=lambda x: (x['BUR_RATE']*x['Hours Worked']))
pi = wl.pivot_table(index=["Order - Material (Key)","Order",'Standard Text Key',\
     'Operation Quantity'],values=["Hours Worked","COST"],aggfunc= np.sum)
pi.reset_index(drop=True)
pi['ACT COST/EA'] = pi['COST']/pi['Operation Quantity']
pi['HRS/EA'] = pi['Hours Worked']/pi['Operation Quantity']
pi.replace([np.inf, -np.inf], np.nan, inplace=True)
pi.dropna(how='any',inplace=True)
pi2 = pi.pivot_table(index=["Order - Material (Key)",'Standard Text Key'],values = ['HRS/EA','ACT COST/EA'],aggfunc= np.mean)
pi2.reset_index(inplace=True)
pi3 = pi2.pivot_table(index=["Order - Material (Key)"],values=['ACT COST/EA','HRS/EA'],aggfunc= np.sum)
pi3.reset_index(inplace=True)
rt = rout.loc[:,['Material','StTextKy','Base Quantity',
               'Setup Hrs','Unit','Run HRs','Unit.1']]
QTY = wl.pivot_table(index=['Order - Material (Key)'],values=['Operation Quantity'],aggfunc=np.mean)
QTY.reset_index(inplace=True) 
rt = rt.merge(QTY,left_on='Material',right_on='Order - Material (Key)',how='left')
rt.drop(columns=['Order - Material (Key)'],axis=1,inplace=True)
rt.loc[rt['Operation Quantity'].isnull(),'Operation Quantity'] = rt['Base Quantity']
rt['PLN HR/EA'] = ((rt['Setup Hrs'] + rt['Run HRs'])/rt['Operation Quantity']).where(rt['Unit.1'] == 'H',\
                 (rt['Setup Hrs'] + (rt['Run HRs']/60))/rt['Operation Quantity'])
rt = rt.pivot_table(index=['Material','StTextKy'],values=['PLN HR/EA'],aggfunc=np.sum)
rt.reset_index(inplace=True)
rt = rt.merge(cst,left_on='StTextKy',right_on='ST KEY',how='left')
rt.drop(columns=['ST KEY'],axis=1,inplace=True)
rt['PLN COST/EA'] = rt['PLN HR/EA']*rt['BUR_RATE']
rt = rt.pivot_table(index=['Material'],values=['PLN COST/EA'],aggfunc=np.sum)
rt.reset_index(inplace=True)
rt = rt.merge(pi3,left_on='Material',right_on='Order - Material (Key)',how='left')
rt['ACT COST/EA'] = rt['ACT COST/EA'].replace("",pd.NA).fillna(rt['PLN COST/EA'])
rt.loc[(rt['ACT COST/EA'] ==0) | (rt['ACT COST/EA'] < .6*rt['PLN COST/EA'] ),'ACT COST/EA'] = rt['PLN COST/EA']
rt.drop(columns=['Order - Material (Key)'],axis=1,inplace=True)
rt.to_pickle(Final_pkl)