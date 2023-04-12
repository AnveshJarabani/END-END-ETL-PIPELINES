import pandas as pd
import numpy as np
import xlwings as xl
import win32com.client as win32
import subprocess,re,pickle,os,warnings
from datetime import datetime
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
BOM = pd.read_hdf('ST_BM_BR.H5',key="BOM")
dict={1:'QTR 1',2:'QTR 1',3:'QTR 1',
      4:'QTR 2',5:'QTR 2',6:'QTR 2',
      7:'QTR 3',8:'QTR 3',9:'QTR 3',
      10:'QTR 4',11:'QTR 4',12:'QTR 4'}
dt=datetime.now()
CUR_QTR=str(dt.year)+" "+dict[dt.month]
PH = pd.read_hdf('PH.H5',key='PH')
PH.rename(columns={'Material - Key':'PH'},inplace=True)
FR = pd.read_hdf('ST_BM_BR.H5',key='FRAMES')
SHP = pd.read_pickle('SHP.PKL')
PERIODS=pd.read_pickle('FISCAL CAL.PKL')
SHP=SHP.merge(PERIODS,left_on='Actual Good Issue Date',right_on='DATE',how='left')
SHP['Act Shipped Amount']=SHP['Act Shipped Amount'].apply(lambda x: float(x.replace(",",'')))
SHP=SHP.loc[SHP['Act Shipped Amount']!=0]
SHP=SHP.loc[SHP['QTR+YR'].str.contains('2023',na=False)]
def removeframes(X):
        X.columns = ['PH','ACT MAT COST']
        Y = X.merge(FR.iloc[:-1,:],left_on='PH',right_on='PART NUMBER',how='left') # remove XLR FROM FRAMES BY [:-1,:]
        Y = Y.loc[Y['PART NUMBER'].isna()]
        Y = Y.loc[:,['PH','ACT MAT COST']]
        return Y
PH=removeframes(PH)
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
# _______________________BOM EXTRACT_________________________________________________
def BOM_EXPLODE(LIST):
        string=' '.join(LIST)
        str_bytes=string.encode('utf-8')
        from time import time
        start=time()
        out=subprocess.check_output(['python','trees_to_df.py'],input=str_bytes)
        df=pickle.loads(out)
        df.columns=['COMP','MATERIAL','QTY','TOP LVL QTY','TOPLEVEL']
        return df
# ------------------------ADD COSTS TO LEVEL BOMS-----------------------------------------
LIST=set(SHP['Material - Key'])
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
mask=COSTS['COMP']==COSTS['TOPLEVEL']
COSTS.loc[mask,'BUR ACT MAT']=COSTS.loc[mask,'ACT MAT COST']
COSTS.loc[~mask,'BUR ACT MAT']=1.106*COSTS.loc[~mask,'ACT MAT COST']
COSTS['BUR ACT MAT_SMRY']=1.106*COSTS['ACT MAT COST']
# ------------------------ LAM QUOTEVSACT & SUMMARY PICKLES --------------------------------------------------------------
TPL_COST = COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST','BUR ACT MAT_SMRY'],aggfunc=np.sum)
TPL_COST.reset_index(inplace=True)
TPL_COST['ACT COST/EA']=TPL_COST[['BUR ACT MAT_SMRY','ACT LBR COST','OVS COST']].sum(axis=1)
SHP=SHP.merge(TPL_COST,left_on='Material - Key',right_on='TOPLEVEL',how='left')
SHP['TOTAL ACT']=SHP['ACT COST/EA']*SHP['Act Shipped Qty']
SMRY=SHP.pivot_table(index=['QTR+YR','FISCAL PERIOD','Material - Key'],values=['Act Shipped Amount','TOTAL ACT'],aggfunc=np.sum)
SMRY.reset_index(inplace=True)
SMRY=SMRY.merge(SHP[['Material - Key','Sold-to party']].drop_duplicates(),on='Material - Key',how='left')
SMRY.columns=['QTR+YR','FISCAL PERIOD','TOOL','SHIPPED','ACTUAL COST','CUSTOMER']
SMRY['DELTA']=SMRY['SHIPPED']-SMRY['ACTUAL COST']
SMRY.to_hdf('TOOLCOSTS.H5',key='SMRY')


