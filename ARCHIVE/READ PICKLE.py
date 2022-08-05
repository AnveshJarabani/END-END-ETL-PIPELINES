import pandas as pd
import xlwings as xl
LVLBOMS_PATH = r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\LAM_LVLBOMS.PKL"
lvlboms = pd.read_pickle(LVLBOMS_PATH)
ws = xl.books.active.sheets.active
ws.range('A2').options(index=False).value=lvlboms