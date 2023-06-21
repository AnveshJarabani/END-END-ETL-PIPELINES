import xlwings
import pandas as pd
import numpy as np
# ------------------------ CYMER COSTS ----------------------------------------------------------------
# ---------------------------------- LEVEL BOMS ----------------------------------------------
# XLFILE=r"C:\Users\ajarabani\Downloads\CYMER REQUOTE - 2022 Q4 - AJ.xlsx"
BOM = pd.read_pickle(r"BOM.PKL")
PH = pd.read_pickle('PH.pkl')
#--------------------- MAKE ANY PART NUMBER CHANGES HERE ----------------------------
YT=pd.read_pickle('yt.pkl')
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
PNS = YT.loc[YT['LAST VENDOR'].str.contains('MERCURY',na=False)]
xlwings.books.active.sheets.active.range('A20').options(index=False).value=PNS
PNS=PNS[['P/N']]
PNS.drop_duplicates(inplace=True,ignore_index=True)
# ------------------------------------- BOM EXTRACT ----------------------------------------
for PN in PNS['P/N']:
    if PN not in BOM['MATERIAL'].values:
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
STD=pd.read_pickle("STD.PKL")
LBR = pd.read_pickle("ACT VS PLN LABOR COST.PKL")
FR = pd.read_pickle("FRAMES.PKL")
OVS = pd.read_pickle("OVS.pkl")
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
COSTS1=COSTS.copy()
for i in COSTS1.index:
    if COSTS1.loc[i,'COMP']==COSTS1.loc[i,'MATERIAL']:
        COSTS1.loc[i,'BUR ACT MAT']=COSTS1.loc[i,'ACT MAT COST']
    else:
        COSTS1.loc[i,'BUR ACT MAT']=1.106*COSTS1.loc[i,'ACT MAT COST']
COSTS['BUR ACT MAT']=1.106*COSTS['ACT MAT COST']
COSTS.drop(columns='ACT MAT COST',axis=1,inplace=True)
# ------------------------ CYMER QT VS ACT & SMRY TO PKL ----------------------------------------------------------------
TPL_COST1 = COSTS1.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST'],aggfunc=np.sum)
TPL_COST1.reset_index(inplace=True)
TPL_COST1['ACT']=TPL_COST1.iloc[:,1:4].sum(axis=1)
xlwings.books.active.sheets.active.range('A1').options(index=False).value=TPL_COST1