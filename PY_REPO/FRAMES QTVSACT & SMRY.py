import pandas as pd
import numpy as np
import xlwings as xl
import subprocess,pickle
# ------------------------ FRAME PART COSTS ----------------------------------------------------------------
# ---------------------------------- LEVEL BOMS ----------------------------------------------
book=xl.Book()
book.sheets.add(name='FRAMES SUMMARY',before='Sheet1')
book.sheets.add(name='FRAME COSTS',before='Sheet1')
book.sheets('Sheet1').delete()
ws=book.sheets
QUOTES = pd.read_pickle(r"FRAME QUOTES.PKL")
BOM = pd.read_hdf('ST_BM_BR.H5',key="BOM")
PH = pd.read_hdf('PH.H5',key='PH')
PH.rename(columns={'Material - Key':'PH'},inplace=True)
FR = pd.read_pickle("FRAMES.PKL")
def removeframes(X):
        X.columns = ['PH','ACT MAT COST']
        Y = X.merge(FR,left_on='PH',right_on='PART NUMBER',how='left')
        Y = Y.loc[Y['PART NUMBER'].isna()]
        Y = Y.loc[:,['PH','ACT MAT COST']]
        return Y
PH=removeframes(PH)
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
PNS = FR[['PART NUMBER']]
PNS.columns=['P/N']
# _______________________BOM EXTRACT_________________________________________________
string=' '.join(list(PNS['P/N'].astype(str).unique()))
pkl=subprocess.check_output(['python','BOM_EXPLODE.py'],input=string.encode('utf-8'),shell=True)
LVLBOMS=pickle.loads(pkl)
LVLBOMS=LVLBOMS[['TOPLEVEL','PARENT','PN','QTY','TQ']]
LVLBOMS.columns=['TOPLEVEL', 'MATERIAL', 'COMP', 'QTY', 'TOP LVL QTY']
# ---------------------------------- ADD COSTS TO LEVEL BOMS --------------------------------------
STD=pd.read_hdf("ST_BM_BR.H5",key='STD')
LBR = pd.read_hdf('LBR.H5',key='ACT_V_PL_CST')
OVS = pd.read_hdf('OVS.H5',key='OVS')
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
COSTS['BUR ACT MAT']=1.106*COSTS['ACT MAT COST']
COSTS.drop(columns='ACT MAT COST',axis=1,inplace=True)
ws('FRAME COSTS').clear_contents()
ws('FRAME COSTS').range('A1').options(index=False).value=COSTS
COSTS.to_pickle('FRAME.COSTS.PKL')
# ------------------------ FRAME ACT & SMRY TO PKL ----------------------------------------------------------------
TPL_COST = COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST'],aggfunc=np.sum)
TPL_COST.reset_index(inplace=True)
TPL_COST['BUR ACT']=TPL_COST.iloc[:,1:4].sum(axis=1)
QUOTES = QUOTES.merge(TPL_COST,left_on='P/N',right_on='TOPLEVEL',how='left')
QUOTES[['TIER 1','TIER 3','TIER 5','TIER 10']]=QUOTES[['TIER 1','TIER 3','TIER 5','TIER 10']].astype(float)
QUOTES['▲ TIER 1']=QUOTES['TIER 1']-QUOTES['BUR ACT']
QUOTES['▲ TIER 3']=QUOTES['TIER 3']-QUOTES['BUR ACT']
QUOTES['▲ TIER 5']=QUOTES['TIER 5']-QUOTES['BUR ACT']
QUOTES['▲ TIER 10']=QUOTES['TIER 10']-QUOTES['BUR ACT']
QUOTES.to_pickle('FRAMES_TESTQUOTES.PKL')
#------------------COSTS FOR PIE CHART DISPLAY - MAT OVS LABOR -----------------------------
PIE_GRAPH=TPL_COST[['TOPLEVEL','ACT LBR COST','BUR ACT MAT','OVS COST']]
PIE_GRAPH.to_pickle('FRAMES_PIE.PKL')
#----------------------------------CONTINUE TO FRAMES_QT_VS_ACT------------------------
QUOTES = QUOTES[['P/N','BUR ACT','TIER 1','▲ TIER 1',
                 'TIER 3','▲ TIER 3','TIER 5','▲ TIER 5',
                 'TIER 10','▲ TIER 10']]
QUOTES=QUOTES.fillna(0)
QUOTES.to_pickle('FRAMES_QT_VS_ACT.PKL')
ws('FRAMES SUMMARY').clear_contents()
ws('FRAMES SUMMARY').range('A1').options(index=False).value=QUOTES