import xlwings as xl
import pandas as pd
import numpy as np
COST_COMP_PATH=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LM_SMRY.PKL"
CS=pd.read_pickle(COST_COMP_PATH)
xl.books.active.sheets.active.range('A1').options(index=False).value=CS
