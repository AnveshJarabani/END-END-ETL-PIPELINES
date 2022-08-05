import pandas as pd
import numpy as np
# UPDATE THE BOM & ROUTING PATHS BEFORE EXECUTING THE CODE.
int_path = r"C:\Users\ajarabani\Downloads\3321 Bom Dump 06222022.xlsx"
fab_path = r"C:\Users\ajarabani\Downloads\3322 Bom Dump 06222022.xlsx"
bompkl_path = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\BOM.PKL"
Hrs_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Labor Hours Q2 21 - Q2 22.xlsx"
int_bom = pd.read_excel(int_path,sheet_name='Sheet1',usecols='B:AN')
int_bom = int_bom.loc[:,['/BIC/ZMATERIAL',	'/BIC/ZBCOMNT',	'/BIC/ZBOMQTY']]
int_bom.columns = ['MATERIAL', 'COMPONENT', 'QTY']
int_bom.drop_duplicates(inplace=True,ignore_index=True)
int_bom=int_bom[int_bom['COMPONENT'] != ""]
int_bom = int_bom.pivot_table(index=['MATERIAL', 'COMPONENT'],values=['QTY'],aggfunc= np.sum)
int_bom.reset_index(inplace=True)
wl = pd.read_excel(Hrs_PATH,sheet_name='Employee Labor Hours',usecols='H,AK',skiprows=[0])
wl = wl.loc[:,['Order - Material (Key)','Operation Quantity']]
wl = wl[wl['Order - Material (Key)'] != '#']
QTY = wl.pivot_table(index=['Order - Material (Key)'],values=['Operation Quantity'],aggfunc=np.mean)
QTY.reset_index(inplace=True) 
QTY.columns=['MATERIALKEY','OP QTY']
fab_bom = pd.read_excel(fab_path,sheet_name='Sheet1',usecols='B:AN')
fab_bom = fab_bom.loc[:,['/BIC/ZMATERIAL',	'/BIC/ZBCOMNT',	'/BIC/ZBOMQTY','FMENG']]
fab_bom.columns = ['MATERIAL', 'COMPONENT', 'QTY','FIXEDQTY']
fab_bom=fab_bom.merge(QTY,left_on='MATERIAL',right_on='MATERIALKEY',how='left')
fab_bom['OP QTY'].fillna(10,inplace=True)
fab_bom.loc[fab_bom['FIXEDQTY']=='X','QTY']=fab_bom['QTY']/fab_bom['OP QTY']
fab_bom.drop_duplicates(inplace=True,ignore_index=True)
fab_bom=fab_bom[fab_bom['COMPONENT'] != ""]
fab_bom = fab_bom.pivot_table(index=['MATERIAL', 'COMPONENT'],values=['QTY'],aggfunc= np.sum)
fab_bom.reset_index(inplace=True)
BOM = pd.concat([int_bom,fab_bom],axis=0,ignore_index=True)
BOM.drop_duplicates(inplace=True,ignore_index=True)
BOM.to_pickle(bompkl_path)