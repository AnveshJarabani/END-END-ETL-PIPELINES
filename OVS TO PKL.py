import numpy as np
import pandas as pd
OVS_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\OVS Purchase Order Report 7.15.22.xlsx"
OVS_PKL = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\OVS_PKL.pkl"
OVS = pd.read_excel(OVS_PATH,sheet_name='OVS Purchase Order Report',usecols='E:W', skiprows=[0])
OVS = OVS.loc[OVS['Fiscal year / period'].str.contains('2022')]
OVS = OVS.loc[~OVS['PO Amount'].isna()]
OVS = OVS.pivot_table(index=['OVS Material - Key', 'OVS Operation'],values=['PO Price'], aggfunc=np.mean)
OVS.reset_index(inplace=True)
OVS = OVS.pivot_table(index=['OVS Material - Key'], values=['PO Price'], aggfunc=np.sum)
OVS.reset_index(inplace=True)
OVS = OVS.loc[OVS['OVS Material - Key'] != '#']
OVS.rename(columns={'OVS Material - Key': 'MATERIAL', 'PO Price' : 'OVS COST'},inplace=True)
OVS.to_pickle(OVS_PKL)