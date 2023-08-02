import pandas as pd
import numpy as np
import math
import xlwings as xl
import win32com.client as win32
import subprocess,re,pickle,os,warnings
from datetime import datetime
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
BOM = pd.read_hdf('../H5/ST_BM_BR.H5',key="BOM")
PH = pd.read_hdf('../H5/PH.H5',key='FOR_PLUGINS')
PH.rename(columns={'Material - Key':'PH'},inplace=True)
FR = pd.read_hdf('../H5/ST_BM_BR.H5',key='FRAMES')
SHP = pd.read_pickle('../PKL/SHP.PKL')
SHP['QTR+YR']=SHP['SHIPPED_DATE'].apply(lambda x: f"Q{math.ceil(x.month/3)} {x.year}")
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
        out=subprocess.check_output(['python','../PY_REPO/trees_to_df.py'],input=str_bytes)
        df=pickle.loads(out)
        df.columns=['COMP','MATERIAL','QTY','TOP LVL QTY','TOPLEVEL']
        return df
# ------------------------ADD COSTS TO LEVEL BOMS-----------------------------------------
LIST=set(SHP['PART_NUMBER']) 
LVLBOMS=BOM_EXPLODE(LIST)
STD=pd.read_hdf('../H5/ST_BM_BR.H5',key="STD")
LBR = pd.read_hdf("../H5/LBR.H5",key='ACT_V_PL_CST')
OVS = pd.read_hdf("../H5/OVS.H5",key='OVS')
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
TPL_COST = COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST','BUR ACT MAT_SMRY'],aggfunc=np.sum)
TPL_COST.reset_index(inplace=True)
TPL_COST['ACT COST/EA']=TPL_COST[['BUR ACT MAT_SMRY','ACT LBR COST','OVS COST']].sum(axis=1)
SHP=SHP.merge(TPL_COST,left_on='PART_NUMBER',right_on='TOPLEVEL',how='left')
SHP['TOTAL_BUILD_COST']=SHP['ACT COST/EA']*SHP['SHIPPED_QTY']
SMRY=SHP.pivot_table(index=['QTR+YR','CUSTOMER','PART_NUMBER'],values=['SHIPPED_QTY','SHP_AMOUNT','TOTAL_BUILD_COST'],aggfunc=np.sum)
SMRY.reset_index(inplace=True)
SMRY['DELTA']=SMRY['SHP_AMOUNT']-SMRY['TOTAL_BUILD_COST']
SMRY['GM%']=round(SMRY['DELTA']/SMRY['SHP_AMOUNT'],2)
SMRY.to_hdf('../H5/TOOLCOSTS.H5',key='PNL_SHIPMENTS_SMRY')


