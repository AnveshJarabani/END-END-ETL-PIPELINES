import pandas as pd
import numpy as np
# ---------------------------------- LEVEL BOMS ----------------------------------------------
BOM = pd.read_pickle(r"BOM.PKL")
CYMER_QUOTES = pd.read_pickle(r"CYMER QUOTES.PKL")
PH_PATH = r"Purchase History Report_R2R-PCO-008 (Q1, Q2 2022).xlsx"
PH = pd.read_excel(PH_PATH,sheet_name='Purchase History Report Summary',usecols='C',skiprows=[0])
PH.rename(columns={'Material - Key':'PH'},inplace=True)
FR = pd.read_pickle("FRAMES.PKL")
def removeframes(X):
    if len(X.columns)==1:
        X.columns = ['PH']
        Y = X.merge(FR,left_on='PH',right_on='PART NUMBER',how='left')
        Y = Y.loc[Y['PART NUMBER'].isna()]
        Y = Y.loc[:,['PH']]
        return Y
    elif len(X.columns)==2:
        X.columns = ['PH','ACT MAT COST']
        Y = X.merge(FR,left_on='PH',right_on='PART NUMBER',how='left')
        Y = Y.loc[Y['PART NUMBER'].isna()]
        Y = Y.loc[:,['PH','ACT MAT COST']]
        return Y
PH=removeframes(PH)
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
FAB = CYMER_QUOTES[['P/N','TYPE']]
FAB.loc[FAB['TYPE'].str.contains('AAM65',na=False)|FAB['TYPE'].str.contains('BTP AFRM',na=False),'FAB'] = 'FAB'
FAB = FAB[['P/N','FAB']]
FAB = FAB.loc[FAB['FAB']=='FAB']
FAB.drop_duplicates(inplace=True,ignore_index=True)
FAB=FAB.loc[FAB['P/N']!='CY-198172'] # REMOVING THIS FRAME SINCE BOUGHT FROM AIRTRONICS
PNS = CYMER_QUOTES[['P/N']]
PNS.drop_duplicates(inplace=True,ignore_index=True)
for PN in PNS['P/N']:
    # BOM EXTRACT ----------------------------------------
    if PN not in FAB['P/N'].values:
        LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
        continue
    elif PN not in BOM['MATERIAL'].values:
        LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
        continue
    else:
        BM = BOM[BOM['MATERIAL']==PN].reset_index(drop=True)
        x = 0
        while x <= (len(BM.index)-1) :
            if BM.iloc[x,1] in PH['PH'].values:
                x +=1
                continue
            nx = BOM[BOM['MATERIAL']==BM.iloc[x, 1]].reset_index(drop=True)
            BM = pd.concat([BM,nx],axis = 0)
            x +=1
    BM.reset_index(drop=True, inplace=True)
    BM.loc[-1] = [PN,PN,1]
    BM.index = BM.index + 1
    BM = BM.sort_index()
    BM.columns = ['MATERIAL', 'COMP', 'QTY']
    # TOOL QTY ----------------------------------------
    BM['TOP LVL QTY'] = BM[BM['MATERIAL']==PN]['QTY']
    BM['TEMP']=BM.iloc[:,0] + " " + BM.iloc[:,1]
    x = BM.where(BM['MATERIAL']==PN).last_valid_index() + 1
    BM.iloc[:x-1,3] = BM.iloc[:x-1,2]
    for k in range(x,len(BM.index)):
        y = sum(BM.iloc[:k+1,4]==BM.iloc[k,4])
        t = 0    
        for l in range(0,k):
            if BM.iloc[l,1] == BM.iloc[k,0]:
                t +=1    
                if t ==y:
                    BM.iloc[k,3] = BM.iloc[l,3]*BM.iloc[k,2]
    BM.insert(0,'TOPLEVEL',PN)
    BM = BM.iloc[:,:5]
    LVLBOMS = pd.concat([LVLBOMS,BM],ignore_index=True)
LVLBOMS=LVLBOMS[LVLBOMS['TOPLEVEL'].notnull()]
LVLBOMS=LVLBOMS.loc[~LVLBOMS['COMP'].str.endswith('-UCT',na=False)]
# ---------------------------------- ADD COSTS TO LEVEL BOMS --------------------------------------
PH1_PATH = r"Purchase History Report_R2R-PCO-008 (Q1, Q2 2022).xlsx"
PH2_PATH = r"Purchase History Report_R2R-PCO-008 (Q3, Q4 2021).xlsx"
STD=pd.read_pickle("STD.PKL")
LBR = pd.read_pickle("ACT VS PLN LABOR COST.PKL")
FR = pd.read_pickle("FRAMES.PKL")
PH1 = pd.read_excel(PH1_PATH,sheet_name='Purchase History Report Summary',usecols='C,U',skiprows=[0])
PH2 = pd.read_excel(PH2_PATH,sheet_name='Purchase History Report Summary',usecols='C,U',skiprows=[0])
OVS = pd.read_pickle("OVS.pkl")
PH1=removeframes(PH1)
PH2=removeframes(PH2)
COSTS = LVLBOMS.merge(PH1,left_on='COMP',right_on='PH',how='left')
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
COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'OVS COST'] = 0
colrename()
COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].multiply(COSTS['TOP LVL QTY'],axis=0)
COSTS=COSTS.fillna(0)
COSTS.to_pickle('CYMER.COSTS.PKL')