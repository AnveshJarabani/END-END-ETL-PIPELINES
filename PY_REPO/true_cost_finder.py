import pandas as pd
import numpy as np
from trees_to_df import tree_to_df
STD=pd.read_hdf('../H5/ST_BM_BR.H5',key="STD")
LBR = pd.read_hdf('../H5/LBR.H5',key="ACT_V_PL_CST")
OVS = pd.read_hdf("../H5/OVS.H5",key='OVS')
PH = pd.read_hdf('../H5/PH.H5',key='PH')
def PN_TRUE_COST(PN):
    if PN is None:
        PN='UC-66-112093-00'
    PN=PN.strip().upper()
    PH.rename(columns={'Material - Key':'PH'},inplace=True)
    # ___________BOMEXTRACT_________________________________________________
    LVLBOMS=tree_to_df(PN)
    LVLBOMS['TOPLEVEL']=PN
    LVLBOMS=LVLBOMS[['TOPLEVEL','PARENT','PN','QTY','TQ']]
    LVLBOMS.columns=['TOPLEVEL', 'MATERIAL', 'COMP', 'QTY', 'TOP LVL QTY']
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
    COSTS['BUR ACT MAT']=1.106*COSTS['ACT MAT COST']
    PIE_COST=COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT', 'ACT LBR COST', 'OVS COST'],aggfunc=np.sum)
    PIE_COST.reset_index(inplace=True)
    PIE_COST=PIE_COST.transpose().reset_index()
    PIE_COST.columns=PIE_COST.iloc[0]
    PIE_COST=PIE_COST.drop(index=0)
    return PIE_COST.sum()[1]

