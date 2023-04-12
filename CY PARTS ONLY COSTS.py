from decimal import Decimal
import pandas as pd
import numpy as np
import xlwings as xl
# ------------------------ CYMER COSTS ----------------------------------------------------------------
BOM = pd.read_hdf('ST_BM_BR.H5',key="BOM")
PH = pd.read_hdf('PH.H5',key='PH')
NEW_PNS=xl.books.active.sheets.active.range('A2:A162').options(pd.DataFrame,index=False).value
NEW_PNS['PN']='CY-'+NEW_PNS['PN'].astype(str).str.extract(r'(\w*\d*-*\d*-*\d{2,})')
NEW_PNS=NEW_PNS.loc[NEW_PNS['PN']!='CY-211685']
FUTURE_COSTS=pd.read_hdf('CY_ADJ.H5',key='FUTURE_COSTS')
MERCURY_PART=pd.read_hdf('CY_ADJ.H5',key='MERCURY')
PH=PH.merge(FUTURE_COSTS,left_on='PH',right_on='P/N',how='left')
PH.loc[PH['NEW COST'].notna(),'ACT MAT COST']=PH['NEW COST']
PH.drop(columns=['P/N','NEW COST'],inplace=True)
#--------------------- MAKE ANY PART NUMBER CHANGES HERE ----------------------------
PH.loc[PH['PH']=='CY-198172','ACT MAT COST']=18634.5
PH.rename(columns={'Material - Key':'PH'},inplace=True)
FR = pd.read_hdf('ST_BM_BR.H5',key="FRAMES")
def removeframes(X):
        X.columns = ['PH','ACT MAT COST']
        Y = X.merge(FR,left_on='PH',right_on='PART NUMBER',how='left')
        Y = Y.loc[Y['PART NUMBER'].isna()]
        Y = Y.loc[:,['PH','ACT MAT COST']]
        return Y
def remove_mercury_parts(X):
        X.columns = ['PH','ACT MAT COST']
        Y = X.merge(MERCURY_PART,left_on='PH',right_on='TOPLEVEL',how='left')
        Y = Y.loc[Y['TOPLEVEL'].isna()]
        Y = Y.loc[:,['PH','ACT MAT COST']]
        return Y        
PH=removeframes(PH)
PH=remove_mercury_parts(PH)
# ------------------------------------- BOM EXTRACT ----------------------------------------
PNS = NEW_PNS[['PN']]
PNS.drop_duplicates(inplace=True,ignore_index=True)
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
for PN in PNS['PN']:
    if (PH['PH']==PN).any():
        LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
        continue
    elif ~(BOM['MATERIAL']==PN).any():
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
STD=pd.read_hdf('ST_BM_BR.H5',key='STD')
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
COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].applymap(lambda x:float(x) if isinstance(x,Decimal) else x)
COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].multiply(COSTS['TOP LVL QTY'],axis=0)
COSTS=COSTS.fillna(0)
for i in COSTS.index:
    if COSTS.loc[i,'COMP']==COSTS.loc[i,'MATERIAL']:
        COSTS.loc[i,'BUR ACT MAT']=COSTS.loc[i,'ACT MAT COST']
    else:
        COSTS.loc[i,'BUR ACT MAT']=1.106*COSTS.loc[i,'ACT MAT COST']
# ------------------------ CYMER QT VS ACT & SMRY TO PKL ----------------------------------------------------------------
TPL_COST1 = COSTS.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST'],aggfunc=np.sum)
TPL_COST1.reset_index(inplace=True)
TPL_COST1['ACT']=TPL_COST1.iloc[:,1:4].sum(axis=1)
for i in NEW_PNS.index:
    if NEW_PNS.loc[i,'PN'] in PH['PH'].values:
        NEW_PNS.loc[i,'MAKE/BUY']='BUY'
xl.books.active.sheets.active.range('R1').options(index=False).value=TPL_COST1