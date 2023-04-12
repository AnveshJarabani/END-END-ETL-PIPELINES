from decimal import Decimal
import pandas as pd
import numpy as np
# ------------------------ CYMER COSTS ----------------------------------------------------------------
BOM = pd.read_hdf('ST_BM_BR.H5',key="BOM")
PH = pd.read_hdf('PH.H5',key='PH')
QUOTES=pd.read_hdf('QUOTES.H5',key='CY')
SM=pd.read_hdf('ST_BM_BR.H5',key='SM_PARTS')
ind=np.array(QUOTES['TOOL'].unique()).tolist()
NEW_CRATES=pd.read_hdf('CY_ADJ.H5',key='CRATES')
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
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
FAB = QUOTES[['P/N','TYPE']]
FAB.loc[FAB['TYPE'].str.contains('AAM65',na=False)|FAB['TYPE'].str.contains('BTP AFRM',na=False),'FAB'] = 'FAB'
FAB = FAB[['P/N','FAB']]
FAB = FAB.loc[FAB['FAB']=='FAB']
FAB.drop_duplicates(inplace=True,ignore_index=True)
FAB=FAB.loc[FAB['P/N']!='CY-198172']       # REMOVING THIS FRAME SINCE BOUGHT FROM AIRTRONICS
FAB.columns=['PN_FAB','FAB']
PNS = QUOTES[['TOOL']]
PNS.drop_duplicates(inplace=True,ignore_index=True)
# ------------------------------------- BOM EXTRACT ----------------------------------------
# for PN in PNS['TOOL']:
#     if (PH['PH']==PN).any():
#         LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
#         continue
#     elif ~(BOM['MATERIAL']==PN).any():
#         LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
#         continue
#     else:
#         BM = BOM[BOM['MATERIAL']==PN].reset_index(drop=True)
#         x = 0
#         while x <= (len(BM.index)-1) :
#             if BM.iloc[x,1] in PH['PH'].values:
#                 x +=1
#                 continue
#             nx = BOM[BOM['MATERIAL']==BM.iloc[x, 1]].reset_index(drop=True)
#             BM = pd.concat([BM,nx],axis = 0)
#             x +=1
#     BM.reset_index(drop=True, inplace=True)
#     BM.loc[-1] = [PN,PN,1]
#     BM.index = BM.index + 1
#     BM = BM.sort_index()
#     BM.columns = ['MATERIAL', 'COMP', 'QTY']
# # TOOL QTY ----------------------------------------
#     BM['TOP LVL QTY'] = BM[BM['MATERIAL']==PN]['QTY']
#     BM['TEMP']=BM.iloc[:,0] + " " + BM.iloc[:,1]
#     x = BM.where(BM['MATERIAL']==PN).last_valid_index() + 1
#     BM.iloc[:x-1,3] = BM.iloc[:x-1,2]
#     for k in range(x,len(BM.index)):
#         y = sum(BM.iloc[:k+1,4]==BM.iloc[k,4])
#         t = 0    
#         for l in range(0,k):
#             if BM.iloc[l,1] == BM.iloc[k,0]:
#                 t +=1    
#                 if t ==y:
#                     BM.iloc[k,3] = BM.iloc[l,3]*BM.iloc[k,2]
#     BM.insert(0,'TOPLEVEL',PN)
#     BM = BM.iloc[:,:5]
#     LVLBOMS = pd.concat([LVLBOMS,BM],ignore_index=True)
# LVLBOMS=LVLBOMS[LVLBOMS['TOPLEVEL'].notnull()]
# LVLBOMS=LVLBOMS.loc[~LVLBOMS['COMP'].str.endswith('-UCT',na=False)]
# ---------------------------------- ADD COSTS TO LEVEL BOMS --------------------------------------
# LVLBOMS=pd.read_pickle('CY_LVLTEMP.PKL')
LVLBOMS=pd.read_pickle('CY_LVLTEMP1.25.PKL')
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
QUOTES.rename(columns={'TOOL':'TOP LEVEL'},inplace=True)
QUOTES = QUOTES.merge(TPL_COST1,left_on='P/N',right_on='TOPLEVEL',how='left')
QUOTES.loc[QUOTES['P/N'].str.contains('Labor|Sell',regex=True,na=False),'QTY EXT']=1
QUOTES=pd.merge(QUOTES,LBR,left_on='TOP LEVEL',right_on='Material',how='left')
QUOTES.loc[(QUOTES['ACT'].isna()|QUOTES['ACT']==0),'ACT'] = 0
QUOTES['QTY EXT']=QUOTES['QTY EXT'].fillna(0)
QUOTES['ACT EXT'] = QUOTES['ACT']*QUOTES['QTY EXT']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor'),['ACT LBR COST']]=QUOTES['ACT COST/EA']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor'),['ACT','ACT EXT']]=QUOTES['ACT LBR COST']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor|Sell',regex=True,na=False),['COST EA']]=QUOTES['COST EXT']
QUOTES.loc[QUOTES['P/N'].str.contains('Sell',regex=True,na=False),['ACT EXT']]=QUOTES['COST EXT']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor'),'ACT EXT']=QUOTES['COST EXT']
QUOTES.loc[QUOTES['P/N'].str.contains('Labor'),['DESC']]=QUOTES['TOP LEVEL']+' INTEGRATION LABOR COST'
QUOTES['COST EA']=QUOTES['COST EA'].astype(float)
# QUOTES.loc[QUOTES['ACT']<(0.2*QUOTES['COST EA']),['ACT']]=QUOTES['COST EA']
# QUOTES.loc[QUOTES['ACT EXT']<(0.2*QUOTES['COST EXT']),['ACT EXT']]=QUOTES['COST EXT']
QUOTES=QUOTES.merge(FAB,left_on='P/N',right_on='PN_FAB',how='left')
QUOTES.loc[QUOTES['PN_FAB'].notnull(),'MAKE/BUY']='MAKE'
QUOTES['MAKE/BUY']=QUOTES['MAKE/BUY'].fillna('BUY')
for i in QUOTES.index:
    if QUOTES.loc[i,'P/N'] in PH['PH'].values:
        QUOTES.loc[i,'MAKE/BUY']='BUY'
QUOTES.loc[QUOTES['P/N'].str.contains('Labor',na=False),'MAKE/BUY']='Labor Cost'
QUOTES.loc[QUOTES['P/N'].str.contains('Sell',na=False),'MAKE/BUY']='Crate Cost'
QUOTES.loc[QUOTES['TYPE'].str.contains('H-PART',na=False),'MAKE/BUY']='H-PART'
QUOTES.loc[QUOTES['P/N'].str.contains('Labor'),'ACT']=QUOTES['COST EA']
# QUOTES.loc[QUOTES['TOP LEVEL'].isin(SM['SM']),['ACT','ACT EXT']]=QUOTES.loc[QUOTES['TOP LEVEL'].isin(SM['SM']),['ACT','ACT EXT']]*1.3 # 30% markup on MAKE parts
QUOTES.loc[(QUOTES['MAKE/BUY']=='MAKE'),'ACT']=QUOTES['ACT'] #*1.05 # MAKE PARTS MARKUP 30%
QUOTES.loc[(QUOTES['MAKE/BUY']=='MAKE'),'ACT EXT']=QUOTES['ACT']*QUOTES['QTY EXT'] # REDO EXT COST CALCULATION
# QUOTES.loc[(QUOTES['ACT']<QUOTES['COST EA'])&(QUOTES['MAKE/BUY']=='MAKE'),'ACT']=QUOTES['COST EA']
# QUOTES.loc[(QUOTES['ACT EXT']<QUOTES['COST EXT'])&(QUOTES['MAKE/BUY']=='MAKE'),'ACT EXT']=QUOTES['COST EXT']
QUOTES=QUOTES.merge(NEW_CRATES,left_on='TOP LEVEL',right_on='TOOL',how='left')
QUOTES.loc[QUOTES['P/N'].str.contains('Crate',regex=True,na=False)&QUOTES['CRATE TOTAL COST'].notna(),['ACT']]=QUOTES['CRATE TOTAL COST']
QUOTES.loc[QUOTES['P/N'].str.contains('Crate',regex=True,na=False)&QUOTES['CRATE TOTAL COST'].notna(),['ACT EXT']]=QUOTES['CRATE TOTAL COST']
QUOTES.loc[QUOTES['P/N'].str.contains('Crate',regex=True,na=False),['DESC','TYPE']]='CRATE'
QUOTES.loc[QUOTES['P/N'].str.contains('Labor',regex=True,na=False),['DESC','TYPE']]='LABOR'
QUOTES[['COST EXT','ACT EXT']]=QUOTES[['COST EXT','ACT EXT']].applymap(lambda x:float(x) if isinstance(x,Decimal) else x)
QUOTES=QUOTES.pivot_table(index=['TOP LEVEL', 'P/N','DESC','MAKE/BUY','TYPE'],values=['QTY EXT',
            'COST EA','COST EXT',
            'ACT','ACT EXT'],aggfunc=np.sum)
QUOTES.reset_index(inplace=True)
QUOTES['CATEG']=pd.Categorical(QUOTES['TOP LEVEL'],ind)
QUOTES.sort_values('CATEG',inplace=True)
QUOTES.drop(columns=['CATEG'],inplace=True)
QUOTES.reset_index(inplace=True,drop=True)
QUOTES['DELTA']=QUOTES['COST EXT']-QUOTES['ACT EXT']
#----------------------------------CONTINUE TO LM_QT_VS_ACT------------------------
VENDOR=pd.read_hdf('PH.H5',key='LST_VENDOR')
QUOTES=QUOTES.merge(VENDOR,left_on='P/N',right_on='PN',how='left')
QUOTES = QUOTES[['TOP LEVEL', 'P/N','DESC','LAST VENDOR','QTY EXT',
            'COST EA','COST EXT',
            'ACT','ACT EXT','DELTA','MAKE/BUY','TYPE']]
QUOTES.iloc[:,5:10]=QUOTES.iloc[:,5:10].round(2)
QUOTES.rename(columns={'ACT':'NEW COST EA','ACT EXT':'NEW COST EXT','COST EA':'OLD COST EA','COST EXT':'OLD COST EXT'},inplace=True)
QUOTES=QUOTES.fillna(0)
QUOTES.loc[(QUOTES['LAST VENDOR']==0)&(QUOTES['MAKE/BUY']=='MAKE'),'LAST VENDOR']='UCT FAB'
QUOTES.loc[(QUOTES['LAST VENDOR'].str.contains('MERCURY MINNESOTA'))&(QUOTES['MAKE/BUY']=='MAKE'),'LAST VENDOR']='UCT FAB'
QUOTES.loc[QUOTES['LAST VENDOR']==0,'LAST VENDOR']='NA'
QUOTES['COMMENTS']=''
CLMS=QUOTES.columns
PREV_QUOTES=pd.read_hdf('CY_ADJ.H5',key='YT')
PREV_QUOTES.loc[PREV_QUOTES['P/N']=='CY-207754','NEW COST EA']=2475
PREV_QUOTES.loc[PREV_QUOTES['P/N']=='CY-207754','NEW COST EXT']=2475*PREV_QUOTES['QTY EXT']
PREV_QUOTES=PREV_QUOTES[['TOP LEVEL','P/N','NEW COST EA','NEW COST EXT','TYPE']]
PREV_QUOTES=PREV_QUOTES.pivot_table(index=['TOP LEVEL','P/N','NEW COST EA'],values='NEW COST EXT',aggfunc=np.sum)
PREV_QUOTES.reset_index(inplace=True)
PREV_QUOTES.columns=['TOP LEVEL','P/N','NEW COST EA_OLD','NEW COST EXT_OLD']
QUOTES=QUOTES.merge(PREV_QUOTES,left_on=['TOP LEVEL','P/N'],right_on=['TOP LEVEL','P/N'],how='left')
QUOTES.loc[~QUOTES['TYPE'].str.contains('AAM65|BTP AFRM|CRATE',regex=True,na=True),['NEW COST EA']]=QUOTES['NEW COST EA_OLD']
QUOTES.loc[~QUOTES['TYPE'].str.contains('AAM65|BTP AFRM|CRATE',regex=True,na=True),['NEW COST EXT']]=QUOTES['NEW COST EXT_OLD']
QUOTES.loc[QUOTES['MAKE/BUY'].str.contains('MAKE',na=False),['NEW COST EA','NEW COST EXT']]=QUOTES[['NEW COST EA','NEW COST EXT']]*.975
QUOTES=QUOTES[CLMS]
QUOTES['DELTA']=QUOTES['OLD COST EXT']-QUOTES['NEW COST EXT']
QUOTES.to_hdf('CY_ADJ.H5',key='YT_H-PART',mode='a')
exec(open('CY QT BY TABS.py').read()) 






#TEMPORARY TO CALCULATE ACTUAL FAB VS QUOTE COSTS -------------
# xt=pd.read_hdf('CY_ADJ.H5',key='YT_H-PART')
# ACT_FAB=QUOTES.loc[QUOTES['MAKE/BUY']=='MAKE']
# ACT_FAB=ACT_FAB.loc[ACT_FAB['P/N']!='CY-135323']
# QUOTE_FAB=xt.loc[xt['MAKE/BUY']=='MAKE']
# ACT_FAB=ACT_FAB.pivot_table(index=['TOP LEVEL'],values=['NEW COST EXT'],aggfunc=np.sum)
# ACT_FAB.reset_index(inplace=True)
# QUOTE_FAB=QUOTE_FAB.pivot_table(index=['TOP LEVEL'],values=['NEW COST EXT'],aggfunc=np.sum)
# QUOTE_FAB.reset_index(inplace=True)
# ACT_FAB.columns=['TOP LEVEL','ACT FAB CST']
# QUOTE_FAB.columns=['TOP LEVEL_','QUOTE FAB CST']
# QUOTE_FAB=QUOTE_FAB.merge(ACT_FAB,left_on='TOP LEVEL_',right_on='TOP LEVEL',how='left')
# QUOTE_FAB=QUOTE_FAB[['TOP LEVEL','QUOTE FAB CST','ACT FAB CST']]
# QUOTE_FAB['DELTA']=QUOTE_FAB['QUOTE FAB CST']-QUOTE_FAB['ACT FAB CST']
# QUOTE_FAB['% DELTA']=QUOTE_FAB['DELTA']/QUOTE_FAB['ACT FAB CST']
# print(QUOTE_FAB)