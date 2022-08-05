import pandas as pd
FAB_STD_PATH = R"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Material Master Characteristics_P2P040 3322.xlsx"
INT_STD_PATH = R"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\Material Master Characteristics_P2P040 3321.xlsx"
STD_PATH = R"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\STD.PKL"
FAB_STD = pd.read_excel(FAB_STD_PATH,sheet_name='Material Master Character',usecols='I,BR',skiprows=[0])
INT_STD = pd.read_excel(INT_STD_PATH,sheet_name='Material Master Character',usecols='I,BR',skiprows=[0])
STD = pd.concat([FAB_STD,INT_STD],ignore_index=True)
STD = STD[STD['Material - Key'].str.endswith('-UCT')==False]
STD.reset_index(drop=True)
STD.columns = ['MATERIAL', 'STD COST']
STD['STD COST'] /=1.106
STD = STD.pivot_table(index=['MATERIAL'],values=['STD COST'], aggfunc=max)
STD.reset_index(inplace=True)
STD.to_pickle(STD_PATH)