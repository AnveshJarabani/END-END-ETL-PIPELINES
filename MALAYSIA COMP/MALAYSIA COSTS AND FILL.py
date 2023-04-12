# from decimal import Decimal
import pandas as pd
import numpy as np
# BOM = pd.read_pickle(r"BOM.PKL")
# QUOTES = pd.read_pickle(r"MALAYSIA QUOTE PNS.PKL")
# PH = pd.read_pickle('PH.pkl')
# #--------------------- MAKE ANY PART NUMBER CHANGES HERE ----------------------------
# PH.rename(columns={'Material - Key':'PH'},inplace=True)
# FR = pd.read_pickle("FRAMES.PKL")
# def removeframes(X):
#         X.columns = ['PH','ACT MAT COST']
#         Y = X.merge(FR,left_on='PH',right_on='PART NUMBER',how='left')
#         Y = Y.loc[Y['PART NUMBER'].isna()]
#         Y = Y.loc[:,['PH','ACT MAT COST']]
#         return Y
# PH=removeframes(PH)
# LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
# PNS = QUOTES[['LAM PART#']]
# PNS.drop_duplicates(inplace=True,ignore_index=True)
# # ------------------------------------- BOM EXTRACT ----------------------------------------
# for PN in PNS['LAM PART#']:
#     if PN in PH['PH'].values:
#         LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
#         QUOTES.loc[QUOTES['LAM PART#']==PN,'MAKE/BUY']='BUY'
#         continue
#     else:
#         QUOTES.loc[QUOTES['LAM PART#']==PN,'MAKE/BUY']='UCT FAB'
#         BM = BOM[BOM['MATERIAL']==PN].reset_index(drop=True)
#         x = 0
#         while x <= (len(BM.index)-1) :
#             if BM.iloc[x,1] in PH['PH'].values:
#                 x +=1
#                 continue
#             nx = BOM[BOM['MATERIAL']==BM.iloc[x, 1]].reset_index(drop=True)
#             BM = pd.concat([BM,nx],axis = 0)
#             x +=1
#     if PN not in BOM['MATERIAL'].values:
#         LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
#         QUOTES.loc[QUOTES['LAM PART#']==PN,'MAKE/BUY']='NA'
#         continue
#     BM.reset_index(drop=True, inplace=True)
#     BM.loc[-1] = [PN,PN,1]
#     BM.index = BM.index + 1
#     BM = BM.sort_index()
#     BM.columns = ['MATERIAL', 'COMP', 'QTY']
#     # TOOL QTY ----------------------------------------
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
# # ---------------------------------- ADD COSTS TO LEVEL BOMS --------------------------------------
# STD=pd.read_pickle("STD.PKL")
# LBR = pd.read_pickle("ACT VS PLN LABOR COST.PKL")
# FR = pd.read_pickle("FRAMES.PKL")
# OVS = pd.read_pickle("OVS.pkl")
# COSTS = LVLBOMS.merge(PH,left_on='COMP',right_on='PH',how='left')
# COSTS.drop(columns=['PH'],axis=1,inplace=True)
# COSTS = COSTS.merge(STD,left_on='COMP',right_on='MATERIAL',how='left')
# def colrename():
#     COSTS.drop(columns=['MATERIAL_y'],axis=1,inplace=True)
#     COSTS.rename(columns={'MATERIAL_x':'MATERIAL'},inplace=True)
# colrename()
# COSTS.fillna(0,inplace=True)
# COSTS.loc[(COSTS['ACT MAT COST'] == 0) & (~COSTS['COMP'].isin(COSTS['MATERIAL'])),'ACT MAT COST'] = COSTS['STD COST']
# COSTS = COSTS.iloc[:,:6]
# COSTS = COSTS.merge(LBR,left_on='COMP',right_on='Material',how='left')
# COSTS.drop(columns=['Material','PLN COST/EA','HRS/EA'],axis=1,inplace=True)
# COSTS.rename(columns={'ACT COST/EA':'ACT LBR COST'},inplace=True)
# COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'ACT LBR COST'] = 0
# COSTS = COSTS.merge(OVS,left_on='COMP',right_on='MATERIAL',how='left')
# COSTS.loc[(COSTS['ACT MAT COST'] != 0), 'OVS COST'] = 0
# colrename()
# COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].applymap(lambda x:float(x) if isinstance(x,Decimal) else x)
# COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']]=COSTS[['ACT MAT COST', 'ACT LBR COST', 'OVS COST']].multiply(COSTS['TOP LVL QTY'],axis=0)
# COSTS=COSTS.fillna(0)
# COSTS1=COSTS.copy()
# for i in COSTS1.index:
#     if COSTS1.loc[i,'COMP']==COSTS1.loc[i,'MATERIAL']:
#         COSTS1.loc[i,'BUR ACT MAT']=COSTS1.loc[i,'ACT MAT COST']
#     else:
#         COSTS1.loc[i,'BUR ACT MAT']=1.106*COSTS1.loc[i,'ACT MAT COST']
# # ------------------------ CYMER QT VS ACT & SMRY TO PKL ----------------------------------------------------------------
# TPL_COST1 = COSTS1.pivot_table(index=['TOPLEVEL'],values=['BUR ACT MAT','ACT LBR COST','OVS COST'],aggfunc=np.sum)
# TPL_COST1.reset_index(inplace=True)
# TPL_COST1['ACT']=TPL_COST1.iloc[:,1:4].sum(axis=1)
# QUOTES.rename(columns={'TOOL':'TOP LEVEL'},inplace=True)
# QUOTES = QUOTES.merge(TPL_COST1,left_on='LAM PART#',right_on='TOPLEVEL',how='left')
# QUOTES.loc[(QUOTES['ACT'].isna()|QUOTES['ACT']==0),'ACT'] = 0
# #----------------------------------CONTINUE TO LM_QT_VS_ACT------------------------
# VENDOR=pd.read_pickle('PNS LAST VENDOR.PKL')
# QUOTES=QUOTES.merge(VENDOR,left_on='LAM PART#',right_on='PN',how='left')
# QUOTES.loc[QUOTES['LAST VENDOR'].isna(),'LAST VENDOR']=QUOTES['MAKE/BUY']
# QUOTES=QUOTES.fillna(0)
# QUOTES.loc[QUOTES['LAST VENDOR']==0,'LAST VENDOR']='NA'
# QUOTES=QUOTES[['LAM PART#','MAKE/BUY','LAST VENDOR','ACT']]
# QUOTES.to_pickle('MALAYSIA ACTUALS.pkl')
import xlwings as xl
ACTUALS=pd.read_pickle('MALAYSIA ACTUALS.pkl')
import re
import pandas as pd
import glob
path=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\PRICE CHANGE MACRO 3322\PYTHON\MALAYSIA COMP"
xlx = glob.glob(path+'/*xlsx')
ft = pd.DataFrame(xlx)
ft.columns = ['Files']
ft['PN'] = ft['Files'].str.extract(r'(\w*-*\w*-\w*)',expand = True)
BOM_STRING=r'costed bom'
book=xl.Book()
for x in ft['Files']:
        xl=pd.ExcelFile(x)
        for n in xl.sheet_names:
            if re.search(BOM_STRING,n,flags=re.IGNORECASE):
                sheet=n
                break 
        dt = pd.read_excel(x,sheet_name=sheet,usecols='A:AE',skiprows=[0])
        dt.columns = dt.columns.str.upper()
        dt = dt.loc[dt['COMMODITY TYPE'].notna()]
        bm=dt.merge(ACTUALS,left_on='LAM PART#',right_on='LAM PART#',how='left')
        book.sheets.add(name=ft.loc[ft['Files']==x,'PN'].reset_index().iloc[0,1])
        book.sheets(ft.loc[ft['Files']==x,'PN'].reset_index().iloc[0,1]).range('A1').options(index=False).value=bm
book.save()