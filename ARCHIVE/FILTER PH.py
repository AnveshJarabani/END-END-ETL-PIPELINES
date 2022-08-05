import pandas as pd
LVLBOMS_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM_LVLBOMS.PKL"
PH_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Purchase History Report_R2R-PCO-008 (Q1, Q2 2022).xlsx"
PH = pd.read_excel(PH_PATH,sheet_name=1,usecols='C',skiprows=[0])
PHA = PH.iloc[:,0].values
LVLBOMS = pd.read_pickle(LVLBOMS_PATH)
LVLBOMS = LVLBOMS.loc[~LVLBOMS['TOPLEVEL'].isin(PHA)]
LVLBOMS.to_pickle(LVLBOMS_PATH)