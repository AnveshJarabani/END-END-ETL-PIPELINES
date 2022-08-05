import pandas as pd
# UPDATE PKL_NAME TO THE NAME YOU WANT TO STORE THE RESULTS.
PKL_NAME='LAM_LVLBOMS'
LVLBOMS_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\\"
BOM = pd.read_pickle(r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\BOM.PKL")
LAM_QUOTES = pd.read_pickle(r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM QUOTES.PKL")
FR_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\FRAMES.PKL"
PH_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Purchase History Report_R2R-PCO-008 (Q1, Q2 2022).xlsx"
PH = pd.read_excel(PH_PATH,sheet_name='Purchase History Report Summary',usecols='C',skiprows=[0])
PH.rename(columns={'Material - Key':'PH'},inplace=True)
FR = pd.read_pickle(FR_PATH)
LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
FAB = LAM_QUOTES[['LAM PART#','SUPPLIER']]
FAB.loc[FAB['SUPPLIER'].str.contains(r'CHANDLER+|UCTC+|UCT-C+|UCT C+|UCT FAB+|UCT-FAB+',na=False),'FAB'] = 'FAB'
FAB = FAB[['LAM PART#','FAB']]
FAB = FAB.loc[FAB['FAB']=='FAB']
FAB.drop_duplicates(inplace=True,ignore_index=True)
PNS = LAM_QUOTES[['LAM PART#']]
TLS= LAM_QUOTES[['TOP LEVEL']]
PNS.drop_duplicates(inplace=True,ignore_index=True)
for PN in PNS['LAM PART#']:
    # BOM EXTRACT ----------------------------------------
    if PN not in FAB['LAM PART#'].values:
        LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
        continue
    elif PN in TLS['TOP LEVEL']:
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
    # TOP LEVEL QTY ----------------------------------------
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
LVLBOMS.to_pickle(LVLBOMS_PATH+PKL_NAME+'.pkl')