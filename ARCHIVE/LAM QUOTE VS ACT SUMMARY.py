import pandas as pd
import numpy as np
import xlwings as xl
ws = xl.books.active.sheets.active
LM_QT_VS_ACT = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_QT_VS_ACT.PKL"
shp_path = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Shipment Order Report_Q2C102 (Q2 2022).xlsx"
COMP = pd.read_pickle(LM_QT_VS_ACT)
SHP = pd.read_excel(shp_path,sheet_name='Shipment Report',usecols='X:AI',skiprows=[0])
SHP['MULT'] = SHP['Act Shipped Qty']*SHP['ASP']
SHP = SHP.pivot_table(index=['Material - Key','Material'],
                values=['MULT','Act Shipped Qty'],aggfunc=np.sum)             
SHP.reset_index(inplace=True)
SHP['ASP']=SHP['MULT']/SHP['Act Shipped Qty']
COMP_P = COMP.pivot_table(index=["TOP LEVEL"],
        values=['BUR ACT EXT','EXT$$','DELTA','DELTA.1','DELTA.2','DELTA.3'],aggfunc= np.sum)
COMP_P.reset_index(inplace=True)
SMRY = SHP.merge(COMP_P,left_on='Material - Key',right_on='TOP LEVEL',how='left')
SMRY.dropna(subset=['TOP LEVEL'],inplace=True)
SMRY.drop(columns=['TOP LEVEL'],axis=1,inplace=True)
SMRY['DELTA.CAL'] = SMRY['ASP']-SMRY['BUR ACT EXT']
SMRY.rename(columns={'BUR ACT EXT': 'ACTUAL COST'},inplace=True)
SMRY = SMRY.loc[:,['Material - Key','Material','Act Shipped Qty','ASP','EXT$$',
                'ACTUAL COST','DELTA','DELTA.1','DELTA.2','DELTA.3','DELTA.CAL']]
SMRY.reset_index(drop=True,inplace=True)
SMRY_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_SMRY.PKL"
SMRY.to_pickle(SMRY_PATH)