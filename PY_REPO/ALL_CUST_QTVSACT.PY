#######-------------------------------LAM LAM LAM ------------------------------------------
import pandas as pd
import numpy as np
import xlwings as xl
import win32com.client as win32
import subprocess,re,pickle,os,warnings
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
# subprocess.call(['taskkill','/f','/im','EXCEL.EXE'])
if os.path.exists('TOOLCOSTS.H5'):
    os.remove('TOOLCOSTS.H5')
# xw=win32com.client.Dispatch("Excel.Application") 
import tempfile
from time import time
# ------------------------LEVEL BOMS -----------------------------------------
#! ATTENTION THIS NEEDS TO BE UPDATED BY THE QUARTER VALUES!!!!
CUR_QTR='QTR 1'
# wb=xl.Book()
# ws=wb.sheets
# ws.add(name='LAM_SUMMARY')
# ws.add(name='CYMER_SUMMARY')
# ws.add(name='KLA_SUMMARY')
# ws.add(name='LAM_ACT VS QT')
# ws.add(name='KLA_ACT VS QT')
# ws.add(name='CYMER_ACT VS QT')
# xl.books.active.sheets('Sheet1').delete()
BOM = pd.read_hdf('ST_BM_BR.H5',key="BOM")
QUOTES = pd.read_hdf("QUOTES.H5",key='LAM')
QUOTES=QUOTES.loc[QUOTES['SUPPLIER']!='TOP LEVEL']
PH = pd.read_hdf('PH.H5',key='PH')
PH.rename(columns={'Material - Key':'PH'},inplace=True)
FR = pd.read_hdf('ST_BM_BR.H5',key='FRAMES')
SHP = pd.read_pickle('SHP.PKL')
PERIODS=pd.read_pickle('2023 FISCAL PERIODS.PKL')
SHP=SHP.merge(PERIODS,left_on='Actual Good Issue Date',right_on='DATE',how='left')
SHP=SHP.loc[SHP['QTR']==CUR_QTR]
QUOTES=QUOTES[QUOTES['TOP LEVEL'].isin(SHP['Material - Key'])]
def removeframes(X):
        X.columns = ['PH','ACT MAT COST']
        Y = X.merge(FR,left_on='PH',right_on='PART NUMBER',how='left')
        Y = Y.loc[Y['PART NUMBER'].isna()]
        Y = Y.loc[:,['PH','ACT MAT COST']]
        return Y
PH=removeframes(PH)
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
PNS = QUOTES[['LAM PART#']]
TLS= QUOTES[['TOP LEVEL']]
PH=PH[~PH['PH'].isin(TLS['TOP LEVEL'])]
PNS=PNS.drop_duplicates(ignore_index=True)
PNS.dropna(inplace=True)
TLS=TLS.drop_duplicates(ignore_index=True)
LIST=PNS.loc[~PNS['LAM PART#'].isin(TLS['TOP LEVEL']),'LAM PART#']
string=' '.join(LIST.astype(str))
str_bytes=string.encode('utf-8')
from time import time
start=time()
out=subprocess.check_output(['python','trees_to_df.py'],input=str_bytes)
LVLBOMS=pickle.loads(out)
# _______________________BOM EXTRACT_________________________________________________
def BOM_EXPLODE(LIST):
        string=' '.join(LIST.astype(str))
        str_bytes=string.encode('utf-8')
        from time import time
        start=time()
        out=subprocess.check_output(['python','trees_to_df.py'],input=str_bytes)
        df=pickle.loads(out)
        df.columns=['COMP','MATERIAL','QTY','TOP LVL QTY','TOPLEVEL']
        return df
# ------------------------ADD COSTS TO LEVEL BOMS-----------------------------------------
LVLBOMS=BOM_EXPLODE(LIST)
STD=pd.read_hdf('ST_BM_BR.H5',key="STD")
LBR = pd.read_hdf("LBR.H5",key='ACT_V_PL_CST')
OVS = pd.read_hdf("OVS.H5",key='OVS')
COSTS = LVLBOMS.merge(PH,left_on='COMP',right_on='PH',how='left')
COSTS.drop(columns=['PH'],axis=1,inplace=True)
COSTS = COSTS.merge(STD,left_on='COMP',right_on='MATERIAL',how='left')
def colrename():
    COSTS.drop(columns=['MATERIAL_y'],axis=1,inplace=True)
    COSTS.rename(columns={'MATERIAL_x':'MATERIAL'},inplace=True)
colrename()
COSTS.fillna(0,inplace=True)
COSTS.loc[(COSTS['ACT MAT COST'] == 0) & (~COSTS['COMP'].isin(COSTS['MATERIAL'])),'ACT MAT COST'] = COSTS['STD COST']
COSTS = COSTS.iloc[:,:6]
COSTS = COSTS.merge(LBR,left_on='COMP',right_on='Material',how='left')
COSTS.drop(columns=['Material','PLN COST/EA','HRS/EA'],axis=1,inplace=True)
COSTS.rename(columns={'ACT COST/EA':'ACT LBR COST'},inplace=True)
COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'ACT LBR COST'] = 0
COSTS = COSTS.merge(OVS,left_on='COMP',right_on='MATERIAL',how='left')
COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'OVS COST'] = 0
colrename()
COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].multiply(COSTS['TOP LVL QTY'],axis=0)
COSTS=COSTS.fillna(0)
###----------------- COSTS TABLE NEED TO BE USED FOR PROFIT AND LOSS CALCULATION AND APPLES TO APPLES COMPARISION DEPENDING ON THE SHEET.
for i in COSTS.index:
    if COSTS.loc[i,'COMP']==COSTS.loc[i,'MATERIAL']:
        COSTS.loc[i,'BUR ACT MAT']=COSTS.loc[i,'ACT MAT COST']
    else:
        COSTS.loc[i,'BUR ACT MAT']=1.106*COSTS.loc[i,'ACT MAT COST']
COSTS['BUR ACT MAT_SMRY']=1.106*COSTS['ACT MAT COST']
COSTS.drop(columns='ACT MAT COST',axis=1,inplace=True)
# ------------------------ LAM QUOTEVSACT & SUMMARY PICKLES --------------------------------------------------------------
TPL_COST = COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST','BUR ACT MAT_SMRY'],aggfunc=np.sum)
TPL_COST.reset_index(inplace=True)
TPL_COST['ACT']=TPL_COST[['BUR ACT MAT','ACT LBR COST','OVS COST']].sum(axis=1)
TPL_COST['ACT_SMRY']=TPL_COST[['BUR ACT MAT_SMRY','ACT LBR COST','OVS COST']].sum(axis=1)
QUOTES = QUOTES.merge(TPL_COST,left_on='LAM PART#',right_on='TOPLEVEL',how='left')
for i in QUOTES.loc[QUOTES['LAM PART#'].isna()&QUOTES['DESCRIPTION'].isna(),'TOPLEVEL'].unique():
    try:
        QUOTES.loc[QUOTES['LAM PART#'].isna()&QUOTES['DESCRIPTION'].isna()&(QUOTES['TOPLEVEL']==i),'DESCRIPTION']= i + ' LABOR COST'
        QUOTES.loc[QUOTES['DESCRIPTION']==i+' LABOR COST','ACT']=LBR.loc[LBR['Material']==i,'ACT COST/EA'].reset_index().iloc[0,1]
    except:
        QUOTES.loc[QUOTES['DESCRIPTION']==i+' LABOR COST','ACT']=QUOTES.loc[QUOTES['LAM PART#'].isna()&QUOTES['DESCRIPTION'].isna()&(QUOTES['TOPLEVEL']==i),'UNITCOST']
QUOTES=QUOTES.loc[(QUOTES['UNITCOST']!=0)&(QUOTES['UNITCOST'].notna())]
QUOTES.loc[QUOTES['ACT'].isna(),'ACT'] = QUOTES['UNITCOST']
QUOTES[['UNITCOST','UNITCOST.4']]=QUOTES[['UNITCOST','UNITCOST.4']].astype(float)
#--------------OUTLIER CONTROLLERS ---------------------
QUOTES.loc[QUOTES['ACT']<(0.1*QUOTES['UNITCOST.4']),'ACT']=QUOTES['UNITCOST.4']
QUOTES.loc[QUOTES['LAM PART#'].str.match(r'^21-',na=False),'ACT']=QUOTES['UNITCOST']*1.5
QUOTES['ACT']=QUOTES['ACT'].astype(float)
QUOTES['ACT EXT'] = QUOTES['ACT']*QUOTES['EXT QTY']
#------------------------ACT_SMRY UPDATES FOR SUMMARY CALCULATION-------------------------
QUOTES.loc[QUOTES['ACT_SMRY'].isna(),'ACT_SMRY'] = QUOTES['UNITCOST']
QUOTES.loc[QUOTES['ACT_SMRY']<(0.1*QUOTES['UNITCOST.4']),['ACT_SMRY']]=QUOTES['UNITCOST.4']
QUOTES.loc[QUOTES['LAM PART#'].str.match(r'^21-',na=False),'ACT_SMRY']=QUOTES['UNITCOST.4']*1.5
QUOTES['ACT_SMRY EXT'] = QUOTES['ACT_SMRY']*QUOTES['EXT QTY']
DLST=['DELTA','DELTA.1','DELTA.2','DELTA.3','DELTA.4']
EXTLST=['EXT$$','EXT$$.1','EXT$$.2','EXT$$.3','EXT$$.4']
QUOTES[EXTLST]=QUOTES[EXTLST].astype(float)
QUOTES[DLST]=QUOTES[EXTLST].subtract(QUOTES['ACT EXT'],axis=0)
QUOTES.drop(columns=['SUPPLIER'],inplace=True)
VENDOR=pd.read_hdf('PH.H5',key='LST_VENDOR')
VENDOR.columns=['PN','VENDOR']
QUOTES=QUOTES.merge(VENDOR,left_on='LAM PART#',right_on='PN',how='left')
#----------------------------------CONTINUE TO LM_QT_VS_ACT------------------------
ACT_VS_QT = QUOTES[['TOPLEVEL', 'LAM PART#',	'DESCRIPTION','VENDOR','EXT QTY',
             'ACT','ACT EXT', 'UNITCOST',	'EXT$$', 'DELTA',
            'UNITCOST.1',	'EXT$$.1',	'DELTA.1',
            'UNITCOST.2',	'EXT$$.2', 'DELTA.2',		
            'UNITCOST.3',	'EXT$$.3', 'DELTA.3',
            'UNITCOST.4',	'EXT$$.4', 'DELTA.4']]
ACT_VS_QT.select_dtypes(include=[float]).astype(np.float16)
ACT_VS_QT.select_dtypes(include=[int]).astype(np.int8) 
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('LM_QT_VS_ACT',ACT_VS_QT)
# ws('LAM_ACT VS QT').range('A1').options(index=False).value=ACT_VS_QT
#------------------COSTS FOR PIE CHART DISPLAY - MAT OVS LABOR -----------------------------
QUOTES[['EXT LBR COST','EXT OVS COST']]=QUOTES[['ACT LBR COST','OVS COST']].multiply(QUOTES['EXT QTY'],axis=0)
QUOTES['EXT MAT COST']=QUOTES['ACT_SMRY EXT']-(QUOTES['EXT LBR COST']+QUOTES['EXT OVS COST'])
PIE_GRAPH=QUOTES.pivot_table(index=['TOPLEVEL'],values=['EXT LBR COST','EXT MAT COST','EXT OVS COST'],aggfunc=np.sum)
PIE_GRAPH.reset_index(inplace=True)
PIE_GRAPH.rename(columns={'EXT LBR COST':'ACT LBR COST','EXT OVS COST':'OVS COST','EXT MAT COST':'BUR ACT MAT'},inplace=True)
PIE_GRAPH.select_dtypes(include=[float]).astype(np.float16)
PIE_GRAPH.select_dtypes(include=[int]).astype(np.int8) 
PIE_GRAPH['QTR']=CUR_QTR  
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('LM_PIE',PIE_GRAPH)
# PIE_GRAPH_OG=pd.read_hdf('TOOLCOSTS.H5',key='LM_PIE')
# if ~PIE_GRAPH_OG['QTR'].isin([CUR_QTR]).any():
#         PIE_GRAPH=pd.concat([PIE_GRAPH_OG,PIE_GRAPH],ignore_index=True)
#         PIE_GRAPH.to_hdf('TOOLCOSTS.H5',key='LM_PIE',mode='a')
# ----------------------------------SUMMARY -------------------------------------
SHP['MULT'] = SHP['Act Shipped Qty']*SHP['ASP']
SHP = SHP.pivot_table(index=['QTR','FISCAL PERIOD','Material - Key','Material'],
                values=['MULT','Act Shipped Qty'],aggfunc=np.sum)             
SHP.reset_index(inplace=True)
SHP['ASP']=SHP['MULT']/SHP['Act Shipped Qty']
COMP_P = QUOTES.pivot_table(index=["TOPLEVEL"],
        values=['ACT_SMRY EXT'],aggfunc= np.sum)
SMRY = SHP.merge(COMP_P,left_on='Material - Key',right_on='TOPLEVEL',how='left')
SMRY.dropna(subset=['ACT_SMRY EXT'],inplace=True)
SMRY['DELTA.CAL'] = SMRY['ASP']-SMRY['ACT_SMRY EXT']
SMRY.rename(columns={'ACT_SMRY EXT': 'ACTUAL COST'},inplace=True)
SMRY = SMRY.loc[:,['QTR','FISCAL PERIOD','Material - Key','Material','Act Shipped Qty','ASP', 'ACTUAL COST','DELTA.CAL']]
SMRY=SMRY.loc[(SMRY['ASP']!=0)&(SMRY['ACTUAL COST']!=0)]
SMRY.reset_index(drop=True,inplace=True)
SMRY.select_dtypes(include=[float]).astype(np.float16)
SMRY.select_dtypes(include=[int]).astype(np.int8) 
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('LM_SMRY',SMRY)
# ws('LAM_SUMMARY').range('A1').options(index=False).value=SMRY_OG.iloc[:,1:]
# ws('LAM_SUMMARY').range('I2').options(index=False,transpose=True).value=SMRY_OG['FISCAL PERIOD'].unique()
# ws('LAM_SUMMARY').range("I1").value = "LAM"
# ws('LAM_SUMMARY').range("J1").value = "ASP TOTAL"
# ws('LAM_SUMMARY').range("K1").value = "ACT TOTAL"
# ws('LAM_SUMMARY').range("L1").value = "GM"
# ----------------------------------CYMER CYMER CYMER ----------------------------------
# ------------------------ CYMER COSTS ----------------------------------------------------------------
# ---------------------------------- LEVEL BOMS ----------------------------------------------
QUOTES = pd.read_hdf("QUOTES.H5",key='CY')
QUOTES=QUOTES[QUOTES['TOP LEVEL'].isin(SHP['Material - Key'])]
QUOTES.reset_index(inplace=True,drop=True)
SHP = pd.read_pickle('SHP.PKL')
SHP=SHP.merge(PERIODS,left_on='Actual Good Issue Date',right_on='DATE',how='left')
SHP=SHP.loc[SHP['QTR']==CUR_QTR]
PH=removeframes(PH)
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
FAB = QUOTES[['P/N','TYPE']]
FAB.loc[FAB['TYPE'].str.contains('AAM65',na=False)|FAB['TYPE'].str.contains('BTP AFRM',na=False),'FAB'] = 'FAB'
FAB = FAB[['P/N','FAB']]
FAB = FAB.loc[FAB['FAB']=='FAB']
FAB.drop_duplicates(inplace=True,ignore_index=True)
FAB=FAB.loc[FAB['P/N']!='CY-198172']       # REMOVING THIS FRAME SINCE BOUGHT FROM AIRTRONICS
FAB.columns=['PN_FAB','FAB']
PNS = QUOTES[['P/N']]
PNS.drop_duplicates(inplace=True,ignore_index=True)
# _______________________BOM EXTRACT_________________________________________________
LIST=PNS['P/N']
LVLBOMS=BOM_EXPLODE(LIST)
# ---------------------------------- ADD COSTS TO LEVEL BOMS --------------------------------------
COSTS = LVLBOMS.merge(PH,left_on='COMP',right_on='PH',how='left')
COSTS.drop(columns=['PH'],axis=1,inplace=True)
COSTS = COSTS.merge(STD,left_on='COMP',right_on='MATERIAL',how='left')
def colrename():
    COSTS.drop(columns=['MATERIAL_y'],axis=1,inplace=True)
    COSTS.rename(columns={'MATERIAL_x':'MATERIAL'},inplace=True)
colrename()
COSTS.fillna(0,inplace=True)
COSTS.loc[(COSTS['ACT MAT COST'] == 0) & (~COSTS['COMP'].isin(COSTS['MATERIAL'])),'ACT MAT COST'] = COSTS['STD COST']
COSTS = COSTS.iloc[:,:6]
COSTS = COSTS.merge(LBR,left_on='COMP',right_on='Material',how='left')
COSTS.drop(columns=['Material','PLN COST/EA','HRS/EA'],axis=1,inplace=True)
COSTS.rename(columns={'ACT COST/EA':'ACT LBR COST'},inplace=True)
COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'ACT LBR COST'] = 0
COSTS = COSTS.merge(OVS,left_on='COMP',right_on='MATERIAL',how='left')
COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'OVS COST'] = 0
colrename()
COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].multiply(COSTS['TOP LVL QTY'],axis=0)
COSTS=COSTS.fillna(0)
###----------------- COSTS TABLE NEED TO BE USED FOR PROFIT AND LOSS CALCULATION AND APPLES TO APPLES COMPARISION DEPENDING ON THE SHEET.
for i in COSTS.index:
    if COSTS.loc[i,'COMP']==COSTS.loc[i,'MATERIAL']:
        COSTS.loc[i,'BUR ACT MAT']=COSTS.loc[i,'ACT MAT COST']
    else:
        COSTS.loc[i,'BUR ACT MAT']=1.106*COSTS.loc[i,'ACT MAT COST']
COSTS['BUR ACT MAT_SMRY']=1.106*COSTS['ACT MAT COST']
COSTS.drop(columns='ACT MAT COST',axis=1,inplace=True)
# ------------------------ CYMER QT VS ACT & SMRY TO PKL ----------------------------------------------------------------
TPL_COST = COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST','BUR ACT MAT_SMRY'],aggfunc=np.sum)
TPL_COST.reset_index(inplace=True)
TPL_COST['ACT']=TPL_COST[['BUR ACT MAT','ACT LBR COST','OVS COST']].sum(axis=1)
TPL_COST['ACT_SMRY']=TPL_COST[['BUR ACT MAT_SMRY','ACT LBR COST','OVS COST']].sum(axis=1)
QUOTES.rename(columns={'TOOL':'TOP LEVEL'},inplace=True)
QUOTES = QUOTES.merge(TPL_COST,left_on='P/N',right_on='TOPLEVEL',how='left')
QUOTES.loc[QUOTES['P/N'].str.contains('Labor|Sell',regex=True,na=False),'QTY EXT']=1
QUOTES=pd.merge(QUOTES,LBR,left_on='TOP LEVEL',right_on='Material',how='left')
QUOTES.loc[(QUOTES['ACT'].isna()|QUOTES['ACT']==0),'ACT'] = 0
QUOTES['QTY EXT']=QUOTES['QTY EXT'].fillna(0)
QUOTES['ACT EXT'] = QUOTES['ACT']*QUOTES['QTY EXT']
QUOTES['ACT_SMRY EXT'] = QUOTES['ACT_SMRY']*QUOTES['QTY EXT']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor'),['ACT LBR COST']]=QUOTES['ACT COST/EA']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor'),['ACT','ACT EXT']]=QUOTES['ACT LBR COST']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor|Sell',regex=True,na=False),['COST EA']]=QUOTES['OLD COST EXT']
QUOTES.loc[QUOTES['P/N'].str.contains('Sell',regex=True,na=False),['ACT EXT']]=QUOTES['OLD COST EXT']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor'),['DESC']]=QUOTES['TOP LEVEL']+' INTEGRATION LABOR COST'
QUOTES['COST EA']=QUOTES['COST EA'].astype(float)
# ----------OUTLIER CONTROLLERS -----------------
QUOTES.loc[QUOTES['ACT']<(0.1*QUOTES['COST EA']),['ACT']]=QUOTES['COST EA']
QUOTES.loc[QUOTES['ACT EXT']<(0.1*QUOTES['OLD COST EXT']),['ACT EXT']]=QUOTES['OLD COST EXT']
QUOTES.loc[QUOTES['ACT_SMRY']<(0.1*QUOTES['COST EA']),['ACT_SMRY']]=QUOTES['COST EA']
QUOTES.loc[QUOTES['ACT_SMRY EXT']<(0.1*QUOTES['OLD COST EXT']),['ACT_SMRY EXT']]=QUOTES['OLD COST EXT']
QUOTES.loc[QUOTES['ACT']>(10*QUOTES['COST EA']),['ACT']]=QUOTES['COST EA']
QUOTES.loc[QUOTES['ACT EXT']>(10*QUOTES['OLD COST EXT']),['ACT EXT']]=QUOTES['OLD COST EXT']
QUOTES.loc[QUOTES['ACT_SMRY']>(10*QUOTES['COST EA']),['ACT_SMRY']]=QUOTES['COST EA']
QUOTES.loc[QUOTES['ACT_SMRY EXT']>(10*QUOTES['OLD COST EXT']),['ACT_SMRY EXT']]=QUOTES['OLD COST EXT']
QUOTES['DELTA']=QUOTES['OLD COST EXT']-QUOTES['ACT EXT']
QUOTES=QUOTES.merge(FAB,left_on='P/N',right_on='PN_FAB',how='left')
VENDOR=pd.read_hdf('PH.H5',key='LST_VENDOR')
VENDOR.columns=['PN','VENDOR']
QUOTES=QUOTES.merge(VENDOR,left_on='P/N',right_on='PN',how='left')
#----------------------------------CONTINUE TO CY_QT_VS_ACT------------------------
ACT_VS_QT = QUOTES[['TOP LEVEL', 'P/N','DESC','VENDOR','QTY EXT',
            'ACT','ACT EXT','COST EA','OLD COST EXT', 'DELTA']]
ACT_VS_QT=ACT_VS_QT.fillna(0)
ACT_VS_QT.select_dtypes(include=[float]).astype(np.float16)
ACT_VS_QT.select_dtypes(include=[int]).astype(np.int8)     
ACT_VS_QT.to_hdf('TOOLCOSTS.H5',key='CY_QT_VS_ACT',mode='a')
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('CY_QT_VS_ACT',ACT_VS_QT)
# ws('CYMER_ACT VS QT').range('A1').options(index=False).value=ACT_VS_QT
#------------------COSTS FOR PIE CHART DISPLAY - MAT OVS LABOR -----------------------------
QUOTES[['EXT LBR COST','EXT OVS COST']]=QUOTES[['ACT LBR COST','OVS COST']].multiply(QUOTES['QTY EXT'],axis=0)
QUOTES['EXT MAT COST']=QUOTES['ACT_SMRY EXT']-(QUOTES['EXT LBR COST']+QUOTES['EXT OVS COST'])
PIE_GRAPH=QUOTES.pivot_table(index=['TOP LEVEL'],values=['EXT LBR COST','EXT MAT COST','EXT OVS COST'],aggfunc=np.sum)
PIE_GRAPH.reset_index(inplace=True)
PIE_GRAPH.rename(columns={'EXT LBR COST':'ACT LBR COST','EXT OVS COST':'OVS COST','EXT MAT COST':'BUR ACT MAT'},inplace=True)
PIE_GRAPH['QTR']=CUR_QTR 
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('CY_PIE',PIE_GRAPH)
# PIE_GRAPH_OG=pd.read_hdf('TOOLCOSTS.H5',key='CY_PIE')
# if ~PIE_GRAPH_OG['QTR'].isin([CUR_QTR]).any():
#         PIE_GRAPH=pd.concat([PIE_GRAPH_OG,PIE_GRAPH],ignore_index=True)
#         PIE_GRAPH.to_hdf('TOOLCOSTS.H5',key='CY_PIE',mode='a')
# ----------------------------------SUMMARY---------------------------------------
SHP['MULT'] = SHP['Act Shipped Qty']*SHP['ASP']
SHP = SHP.pivot_table(index=['QTR','FISCAL PERIOD','Material - Key','Material'],
                values=['MULT','Act Shipped Qty'],aggfunc=np.sum)             
SHP.reset_index(inplace=True)
SHP['ASP']=SHP['MULT']/SHP['Act Shipped Qty']
COMP_P = QUOTES.pivot_table(index=["TOP LEVEL"],
        values=['ACT_SMRY EXT'],aggfunc= np.sum)
SMRY = SHP.merge(COMP_P,left_on='Material - Key',right_on='TOP LEVEL',how='left')
SMRY.dropna(subset=['ACT_SMRY EXT'],inplace=True)
SMRY['DELTA.CAL'] = SMRY['ASP']-SMRY['ACT_SMRY EXT']
SMRY.rename(columns={'ACT_SMRY EXT': 'ACTUAL COST'},inplace=True)
SMRY = SMRY.loc[:,['QTR','FISCAL PERIOD','Material - Key','Material','Act Shipped Qty','ASP', 'ACTUAL COST','DELTA.CAL']]
SMRY=SMRY.loc[(SMRY['ASP']!=0)&(SMRY['ACTUAL COST']!=0)]
SMRY.reset_index(drop=True,inplace=True)
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('CY_SMRY',SMRY)
# SMRY_OG=pd.read_hdf('TOOLCOSTS.H5',key='CY_SMRY')
# if ~SMRY_OG['QTR'].isin([CUR_QTR]).any():
#         SMRY=pd.concat([SMRY_OG,SMRY],ignore_index=True)
#         SMRY.to_hdf('TOOLCOSTS.H5','CY_SMRY',mode='a')
# ws('CYMER_SUMMARY').range('A1').options(index=False).value=SMRY_OG.iloc[:,1:]
# ws('CYMER_SUMMARY').range('I2').options(index=False,transpose=True).value=SMRY_OG['FISCAL PERIOD'].unique()
# ws('CYMER_SUMMARY').range("I1").value = "CYMER"
# ws('CYMER_SUMMARY').range("J1").value = "ASP TOTAL"
# ws('CYMER_SUMMARY').range("K1").value = "ACT TOTAL"
# ws('CYMER_SUMMARY').range("L1").value = "GM"
# ---------------------- KLA KLA KLA
# ------------------------ KLA COSTS ----------------------------------------------------------------
# ---------------------------------- LEVEL BOMS ----------------------------------------------
SHP = pd.read_pickle('SHP.PKL')
SHP=SHP.merge(PERIODS,left_on='Actual Good Issue Date',right_on='DATE',how='left')
SHP=SHP.loc[SHP['QTR']==CUR_QTR]
QUOTES = pd.read_hdf('QUOTES.H5',key="KLA")
QUOTES=QUOTES[QUOTES['TOP LEVEL'].isin(SHP['Material - Key'])]
QUOTES.reset_index(inplace=True,drop=True)
PH = pd.read_hdf('PH.H5',key='PH')
PH.rename(columns={'Material - Key':'PH'},inplace=True)
PH=removeframes(PH)
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
PNS = QUOTES[['TOP LEVEL','PART#']]
PNS=PNS[['PART#']]
PNS.drop_duplicates(inplace=True,ignore_index=True)
# _______________________BOM EXTRACT_________________________________________________
LIST=PNS['PART#']
LVLBOMS=BOM_EXPLODE(LIST)
# ---------------------------------- ADD COSTS TO LEVEL BOMS --------------------------------------
COSTS = LVLBOMS.merge(PH,left_on='COMP',right_on='PH',how='left')
COSTS.drop(columns=['PH'],axis=1,inplace=True)
COSTS = COSTS.merge(STD,left_on='COMP',right_on='MATERIAL',how='left')
def colrename():
    COSTS.drop(columns=['MATERIAL_y'],axis=1,inplace=True)
    COSTS.rename(columns={'MATERIAL_x':'MATERIAL'},inplace=True)
colrename()
COSTS.fillna(0,inplace=True)
COSTS.loc[(COSTS['ACT MAT COST'] == 0) & (~COSTS['COMP'].isin(COSTS['MATERIAL'])),'ACT MAT COST'] = COSTS['STD COST']
COSTS = COSTS.iloc[:,:6]
COSTS = COSTS.merge(LBR,left_on='COMP',right_on='Material',how='left')
COSTS.drop(columns=['Material','PLN COST/EA','HRS/EA'],axis=1,inplace=True)
COSTS.rename(columns={'ACT COST/EA':'ACT LBR COST'},inplace=True)
COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'ACT LBR COST'] = 0
COSTS = COSTS.merge(OVS,left_on='COMP',right_on='MATERIAL',how='left')
COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'OVS COST'] = 0
colrename()
COSTS[['ACT MAT COST','ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST','ACT LBR COST', 'OVS COST']].multiply(COSTS['TOP LVL QTY'],axis=0)
COSTS.loc[COSTS['TOPLEVEL'].isin(QUOTES['TOP LEVEL']),'BUR ACT MAT']=0
COSTS.loc[COSTS['TOPLEVEL'].isin(QUOTES['TOP LEVEL']),'OVS']=0
COSTS=COSTS.fillna(0)
for i in COSTS.index:
    if COSTS.loc[i,'COMP']==COSTS.loc[i,'MATERIAL']:
        COSTS.loc[i,'BUR ACT MAT']=COSTS.loc[i,'ACT MAT COST']
    else:
        COSTS.loc[i,'BUR ACT MAT']=1.106*COSTS.loc[i,'ACT MAT COST']
COSTS['BUR ACT MAT_SMRY']=1.106*COSTS['ACT MAT COST']
COSTS.drop(columns='ACT MAT COST',axis=1,inplace=True)
# ------------------------ KLA QT VS ACT & SMRY TO PKL ----------------------------------------------------------------
COSTS=pd.read_hdf('TEMP_KLA.H5',key='COSTS')
TPL_COST = COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST','BUR ACT MAT_SMRY'],aggfunc=np.sum)
TPL_COST.reset_index(inplace=True)
TPL_COST['ACT']=TPL_COST[['BUR ACT MAT','ACT LBR COST','OVS COST']].sum(axis=1)
TPL_COST['ACT_SMRY']=TPL_COST[['BUR ACT MAT_SMRY','ACT LBR COST','OVS COST']].sum(axis=1)
QUOTES.rename(columns={'TOOL':'TOP LEVEL'},inplace=True)
QUOTES = QUOTES.merge(TPL_COST,left_on='PART#',right_on='TOPLEVEL',how='left')
QUOTES=pd.merge(QUOTES,LBR,left_on='TOP LEVEL',right_on='Material',how='left')
QUOTES['ACT']=QUOTES['ACT'].fillna(0)
QUOTES['QTY']=QUOTES['QTY'].apply(lambda x:float(x))
QUOTES['ACT EXT'] = QUOTES['ACT']*QUOTES['QTY']
QUOTES['ACT_SMRY EXT'] = QUOTES['ACT_SMRY']*QUOTES['QTY']
QUOTES.iloc[:,5:15]=QUOTES.iloc[:,5:15].fillna(0)
QUOTES=QUOTES.loc[QUOTES['QTY'].notna()]
for i in range(5,15):
    QUOTES.iloc[:,i]=QUOTES.iloc[:,i].apply(lambda x: re.sub('[\$]','',x) if isinstance(x,str) else x)
QUOTES.iloc[:,5:15]=QUOTES.iloc[:,5:15].astype(float)
#-----------------------OUTLIER CONTROLLERS -----------------------------
QUOTES.loc[QUOTES['ACT EXT']==0,'ACT EXT']=QUOTES['COST EXT T3']
QUOTES.loc[QUOTES['ACT EXT']==0,'ACT EXT']=QUOTES['COST EXT T1']
QUOTES['ACT']=QUOTES['ACT EXT']/QUOTES['QTY']
QUOTES.loc[QUOTES['ACT_SMRY EXT']==0,'ACT_SMRY EXT']=QUOTES['COST EXT T3']
QUOTES.loc[QUOTES['ACT_SMRY EXT']==0,'ACT_SMRY EXT']=QUOTES['COST EXT T1']
for i in [1,2,3,5,7,9,10,15,20,25]:
    QUOTES['DELTA T'+str(i)]=QUOTES['COST EXT T'+str(i)]-QUOTES['ACT EXT']
QUOTES.drop(columns=['VENDOR'],inplace=True)
VENDOR=pd.read_hdf('PH.H5',key='LST_VENDOR')
VENDOR.columns=['PN','VENDOR']
QUOTES=QUOTES.merge(VENDOR,left_on='PART#',right_on='PN',how='left')
#----------------------------------CONTINUE TO KLA_QT_VS_ACT------------------------
ACT_VS_QT=QUOTES[['TOP LEVEL', 'PART#', 'DESCRIPTION', 'VENDOR', 'QTY', 'ACT','ACT EXT',
        'COST EXT T1', 'DELTA T1','COST EXT T2', 'DELTA T2','COST EXT T3','DELTA T3',
        'COST EXT T5','DELTA T5', 'COST EXT T7', 'DELTA T7','COST EXT T9','DELTA T9',
        'COST EXT T10','DELTA T10', 'COST EXT T15','DELTA T15', 'COST EXT T20','DELTA T20',
        'COST EXT T25','DELTA T25']]
ACT_VS_QT=ACT_VS_QT.fillna(0)
ACT_VS_QT.select_dtypes(include=[float]).astype(np.float16)
ACT_VS_QT.select_dtypes(include=[int]).astype(np.int8)
# ACT_VS_QT.to_hdf('TOOLCOSTS.H5',key='KLA_QT_VS_ACT',mode='a')
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('KLA_QT_VS_ACT',ACT_VS_QT)
# ws('KLA_ACT VS QT').range('A1').options(index=False).value=ACT_VS_QT
#------------------COSTS FOR PIE CHART DISPLAY - MAT OVS LABOR -----------------------------
QUOTES.loc[QUOTES['DESCRIPTION'].str.contains(r'(?i)LABOR',regex=True,na=False),['BUR ACT','BUR ACT EXT']]=QUOTES['ACT LBR COST']
QUOTES['BUR ACT EXT'] = QUOTES['BUR ACT']*QUOTES['QTY']
QUOTES[['EXT LBR COST','EXT OVS COST']]=QUOTES[['ACT LBR COST','OVS COST']].multiply(QUOTES['QTY'],axis=0)
QUOTES['EXT MAT COST']=QUOTES['ACT_SMRY EXT']-(QUOTES['EXT LBR COST']+QUOTES['EXT OVS COST'])
PIE_GRAPH=QUOTES.pivot_table(index=['TOP LEVEL'],values=['EXT LBR COST','EXT MAT COST','EXT OVS COST'],aggfunc=np.sum)
PIE_GRAPH.reset_index(inplace=True)
PIE_GRAPH.rename(columns={'EXT LBR COST':'ACT LBR COST','EXT OVS COST':'OVS COST','EXT MAT COST':'BUR ACT MAT'},inplace=True)
PIE_GRAPH['QTR']=CUR_QTR  
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('KLA_PIE',PIE_GRAPH)
# PIE_GRAPH_OG=pd.read_hdf('TOOLCOSTS.H5',key='KLA_PIE')
# if ~PIE_GRAPH_OG['QTR'].isin([CUR_QTR]).any():
#         PIE_GRAPH=pd.concat([PIE_GRAPH_OG,PIE_GRAPH],ignore_index=True)
#         PIE_GRAPH.to_hdf('TOOLCOSTS.H5',key='KLA_PIE',mode='a')
# ----------------------------------SUMMARY---------------------------------------
SHP['MULT'] = SHP['Act Shipped Qty']*SHP['ASP']
SHP = SHP.pivot_table(index=['QTR','FISCAL PERIOD','Material - Key','Material'],
                values=['MULT','Act Shipped Qty'],aggfunc=np.sum)             
SHP.reset_index(inplace=True)
SHP['ASP']=SHP['MULT']/SHP['Act Shipped Qty']
COMP_P = QUOTES.pivot_table(index=["TOP LEVEL"],
        values=['ACT_SMRY EXT'],aggfunc= np.sum)
SMRY = SHP.merge(COMP_P,left_on='Material - Key',right_on='TOP LEVEL',how='left')
SMRY.dropna(subset=['ACT_SMRY EXT'],inplace=True)
SMRY['DELTA.CAL'] = SMRY['ASP']-SMRY['ACT_SMRY EXT']
SMRY.rename(columns={'ACT_SMRY EXT': 'ACTUAL COST'},inplace=True)
SMRY = SMRY.loc[:,['QTR','FISCAL PERIOD','Material - Key','Material','Act Shipped Qty','ASP', 'ACTUAL COST','DELTA.CAL']]
SMRY=SMRY.loc[(SMRY['ASP']!=0)&(SMRY['ACTUAL COST']!=0)]
SMRY.reset_index(drop=True,inplace=True)
with pd.HDFStore('TOOLCOSTS.H5',mode='a') as store:
     store.put('KLA_SMRY',SMRY)
# SMRY_OG=pd.read_hdf('TOOLCOSTS.H5',key='KLA_SMRY')
# if ~SMRY_OG['QTR'].isin([CUR_QTR]).any():
#         SMRY=pd.concat([SMRY_OG,SMRY],ignore_index=True)
#         SMRY.to_hdf('TOOLCOSTS.H5','KLA_SMRY',mode='a')
# ws('KLA_SUMMARY').range('A1').options(index=False).value=SMRY_OG.iloc[:,1:]
# ws('KLA_SUMMARY').range('I2').options(index=False,transpose=True).value=SMRY_OG['FISCAL PERIOD'].unique()
# ws('KLA_SUMMARY').range("I1").value = "KLA"
# ws('KLA_SUMMARY').range("J1").value = "ASP TOTAL"
# ws('KLA_SUMMARY').range("K1").value = "ACT TOTAL"
# ws('KLA_SUMMARY').range("L1").value = "GM"
# macro_book=xl.App().books.open("MACRO.XLSM")
# time.sleep(5)
# wb.activate()
# xw=win32.GetActiveObject('Excel.Application')
# macro_book=xw.Workbooks('MACRO.XLSM')
# xw.Application.Run("MACRO.XLSM!Module3.PNL") 
# # macro_book.close()
# xl.books.active.save(r"C:\Users\ajarabani\Downloads\PNL " +CUR_QTR +r" 2023.xlsx")
# print(time()-start)
# del xl