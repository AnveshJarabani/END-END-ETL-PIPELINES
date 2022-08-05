import pandas as pd
import numpy as np
STD_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\STD.PKL"
PH1_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Purchase History Report_R2R-PCO-008 (Q1, Q2 2022).xlsx"
PH2_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Purchase History Report_R2R-PCO-008 (Q3, Q4 2021).xlsx"
LBR_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\ACT VS PLN LABOR COST.PKL"
LAMBOMS_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM_LVLBOMS.PKL"
OVS_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\OVS_PKL.pkl"
FR_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\FRAMES.PKL"
LAMBOMS = pd.read_pickle(LAMBOMS_PATH)
LAMBOMS=LAMBOMS.loc[~LAMBOMS['COMP'].str.endswith('-UCT',na=False)]
STD=pd.read_pickle(STD_PATH)
LBR = pd.read_pickle(LBR_PATH)
FR = pd.read_pickle(FR_PATH)
PH1 = pd.read_excel(PH1_PATH,sheet_name='Purchase History Report Summary',usecols='C,U',skiprows=[0])
PH2 = pd.read_excel(PH2_PATH,sheet_name='Purchase History Report Summary',usecols='C,U',skiprows=[0])
OVS = pd.read_pickle(OVS_PATH)
def removeframes(X):
    X.columns = ['PH','ACT MAT COST']
    Y = X.merge(FR,left_on='PH',right_on='PART NUMBER',how='left')
    Y = Y.loc[Y['PART NUMBER'].isna()]
    Y = Y.loc[:,['PH','ACT MAT COST']]
    return Y
PH1=removeframes(PH1)
PH2=removeframes(PH2)
COSTS = LAMBOMS.merge(PH1,left_on='COMP',right_on='PH',how='left')
COSTS.drop(columns=['PH'],axis=1,inplace=True)
COSTS = COSTS.merge(PH2,left_on='COMP',right_on='PH',how='left')
COSTS.drop(columns=['PH'],axis=1,inplace=True)
COSTS = COSTS.merge(STD,left_on='COMP',right_on='MATERIAL',how='left')
def colrename():
    COSTS.drop(columns=['MATERIAL_y'],axis=1,inplace=True)
    COSTS.rename(columns={'MATERIAL_x':'MATERIAL'},inplace=True)
colrename()
COSTS.fillna(0,inplace=True)
COSTS.loc[(COSTS['ACT MAT COST_x'] == 0),'ACT MAT COST_x'] = COSTS['ACT MAT COST_y']
COSTS.drop(columns=['ACT MAT COST_y'],axis=1,inplace=True)
COSTS.rename(columns={'ACT MAT COST_x':'ACT MAT COST'},inplace=True)
COSTS.loc[(COSTS['ACT MAT COST'] == 0) & (~COSTS['COMP'].isin(COSTS['MATERIAL'])),'ACT MAT COST'] = COSTS['STD COST']
COSTS = COSTS.iloc[:,:6]
COSTS = COSTS.merge(LBR,left_on='COMP',right_on='Material',how='left')
COSTS.drop(columns=['Material','PLN COST/EA','HRS/EA'],axis=1,inplace=True)
COSTS.rename(columns={'ACT COST/EA':'ACT LBR COST'},inplace=True)
COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'ACT LBR COST'] = 0
COSTS = COSTS.merge(OVS,left_on='COMP',right_on='MATERIAL',how='left')
colrename()
COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].multiply(COSTS['TOP LVL QTY'],axis=0)
COSTS=COSTS.fillna(0)
COST_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM.COSTS.PKL"
COSTS.to_pickle(COST_PATH)