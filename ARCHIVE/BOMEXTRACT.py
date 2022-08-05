import xlwings as xl
import pandas as pd
import numpy as np
ws = xl.books.active.sheets
BOMPKL=r"C:\Users\ajarabani\Desktop\Parts\DATA ANALYSIS\COSTING ANALYSIS\DASHBOARD DATA\BOM.PKL"
BOM = pd.read_pickle(BOMPKL)
PH = ws('PURCHASE HIST').range("A:A").options(pd.DataFrame,index=False).value
lr = ws('COST').range("J1").end('down').row
BOM.dropna(inplace=True)
pn = ws('COST').range('G1').value
ws('COST').range("B2:D" + str(lr)).clear()
ws('COST').range('B2:D2').value = [pn,pn,1] 
if pn not in BOM['Material'].values:
    exit()
else:
    mt = BOM[BOM['Material']==pn].reset_index(drop=True)
    x = 0
    while x <= (len(mt.index)-1) :
        nx = BOM[BOM['Material']==mt.iloc[x, 1]].reset_index(drop=True)
        mt = pd.concat([mt,nx],axis = 0)
        x +=1
    ws('COST').range('B3').options(index=False,header=False).value = mt
