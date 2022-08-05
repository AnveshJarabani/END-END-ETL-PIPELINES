import pandas as pd
import numpy as np
LM_QUOTES_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM QUOTES.PKL"
LM_QT_VS_ACT = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_QT_VS_ACT.PKL"
LM_COSTS_PATH =r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM.COSTS.PKL"
QUOTES = pd.read_pickle(LM_QUOTES_PATH)
COSTS = pd.read_pickle(LM_COSTS_PATH)
TPL_COST = COSTS.pivot_table(index=['TOPLEVEL'],values=['ACT MAT COST','ACT LBR COST','OVS COST'],aggfunc=np.sum)
TPL_COST.reset_index(inplace=True)
TPL_COST['ACT']=TPL_COST.iloc[:,1:4].sum(axis=1)
TPL_COST['BUR ACT']=1.106*(TPL_COST['ACT LBR COST']+TPL_COST['ACT MAT COST']+TPL_COST['OVS COST'])
QUOTES = QUOTES.merge(TPL_COST,left_on='LAM PART#',right_on='TOPLEVEL',how='left')
QUOTES.loc[(QUOTES['ACT'].isna()|QUOTES['ACT']==0),'ACT'] = QUOTES['UNITCOST']/1.106
QUOTES.loc[(QUOTES['BUR ACT'].isna()|QUOTES['BUR ACT']==0),'BUR ACT'] = QUOTES['UNITCOST']
QUOTES.loc[QUOTES['LAM PART#'].str.match(r'^21-',na=False),'ACT']=(QUOTES['UNITCOST']*1.5)/1.106
QUOTES.loc[QUOTES['LAM PART#'].str.match(r'^21-',na=False),'BUR ACT']=QUOTES['UNITCOST']*1.5
QUOTES.loc[QUOTES['TOP LEVEL']==QUOTES['LAM PART#'],'BUR ACT']=QUOTES['ACT']
QUOTES['ACT EXT'] = QUOTES['ACT']*QUOTES['EXT QTY']
QUOTES['BUR ACT EXT'] = QUOTES['BUR ACT']*QUOTES['EXT QTY']
DLST=['DELTA','DELTA.1','DELTA.2','DELTA.3','DELTA.4']
EXTLST=['EXT$$','EXT$$.1','EXT$$.2','EXT$$.3','EXT$$.4']
QUOTES[DLST]=QUOTES[EXTLST].subtract(QUOTES['ACT EXT'],axis=0)
#------------------COSTS FOR PIE CHART DISPLAY - MAT OVS LABOR -----------------------------
PIE_GRAPH=QUOTES.pivot_table(index=['TOP LEVEL'],values=['ACT MAT COST','ACT LBR COST','OVS COST'],aggfunc=np.sum)
PIE_GRAPH.reset_index(inplace=True)
PIE_PATH=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAMPIE.PKL"
PIE_GRAPH.to_pickle(PIE_PATH)
#----------------------------------CONTINUE TO LM_QT_VS_ACT------------------------
QUOTES = QUOTES[['TOP LEVEL', 'LAM PART#',	'DESCRIPTION','EXT QTY','SUPPLIER',
            'ACT','BUR ACT','ACT EXT','BUR ACT EXT',
            'UNITCOST',	'EXT$$', 'DELTA',
            'UNITCOST.1',	'EXT$$.1',	'DELTA.1',
            'UNITCOST.2',	'EXT$$.2', 'DELTA.2',		
            'UNITCOST.3',	'EXT$$.3', 'DELTA.3',
            'UNITCOST.4',	'EXT$$.4', 'DELTA.4']]
QUOTES.to_pickle(LM_QT_VS_ACT)
# ----------------------------------SUMMARY -------------------------------------
shp_path = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Shipment Order Report_Q2C102 (Q2 2022).xlsx"
SHP = pd.read_excel(shp_path,sheet_name='Shipment Report',usecols='X:AI',skiprows=[0])
SHP['MULT'] = SHP['Act Shipped Qty']*SHP['ASP']
SHP = SHP.pivot_table(index=['Material - Key','Material'],
                values=['MULT','Act Shipped Qty'],aggfunc=np.sum)             
SHP.reset_index(inplace=True)
SHP['ASP']=SHP['MULT']/SHP['Act Shipped Qty']
COMP_P = QUOTES.pivot_table(index=["TOP LEVEL"],
        values=['BUR ACT EXT'],aggfunc= np.sum)
SMRY = SHP.merge(COMP_P,left_on='Material - Key',right_on='TOP LEVEL',how='left')
SMRY.dropna(subset=['BUR ACT EXT'],inplace=True)
SMRY['DELTA.CAL'] = SMRY['ASP']-SMRY['BUR ACT EXT']
SMRY.rename(columns={'BUR ACT EXT': 'ACTUAL COST'},inplace=True)
SMRY = SMRY.loc[:,['Material - Key','Material','Act Shipped Qty','ASP', 'ACTUAL COST','DELTA.CAL']]
SMRY=SMRY.loc[SMRY['ASP']!=0]
SMRY.reset_index(drop=True,inplace=True)
SMRY_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_SMRY.PKL"
SMRY.to_pickle(SMRY_PATH)
