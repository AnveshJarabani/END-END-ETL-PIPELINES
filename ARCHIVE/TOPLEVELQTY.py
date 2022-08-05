import pandas as pd
import xlwings as xl
import numpy as np
ws = xl.books.active.sheets
BM = ws('COST').range("B:D").options(pd.DataFrame,index=0).value
BM.dropna(inplace=True)
BM['TEMP']=BM.iloc[:,0] + " " + BM.iloc[:,1]
PN = ws('COST').range('G1').value
ws('COST').range('H:H').options(index=False,header=True).value = BM['TEMP']
BM['TOP LEVEL QTY'] = BM[BM['COMPONENT']==PN]['QTY'] 
x = BM.where(BM['COMPONENT']==PN).last_valid_index() + 1
BM.iloc[:x-1,4] = BM.iloc[:x-1,2]
for k in range(x,len(BM.index)):
    y = sum(BM.iloc[:k+1,3]==BM.iloc[k,3])
    t = 0    
    for l in range(0,k):
        if BM.iloc[l,1] == BM.iloc[k,0]:
            t +=1    
            if t ==y:
                BM.iloc[k,4] = BM.iloc[l,4]*BM.iloc[k,2]
ws('COST').range('E:E').options(index=False,header=True).value = BM['TOP LEVEL QTY']