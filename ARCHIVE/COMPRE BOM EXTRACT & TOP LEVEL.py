import xlwings as xl
import pandas as pd
ws = xl.books.active.sheets
DT = ws('COST').range("AF:AH").options(pd.DataFrame,index=False).value
PH = ws('PURCHASE HIST').range("A:A").options(pd.DataFrame,index=False).value
lr = ws('COST').range("J1").end('down').row
DT.dropna(inplace=True)
PN = ws('COST').range('G1').value
# BOM EXTRACT ----------------------------------------
if PN not in DT['Material'].values:
    exit()
else:
    BM = DT[DT['Material']==PN].reset_index(drop=True)
    x = 0
    while x <= (len(BM.index)-1) :
        nx = DT[DT['Material']==BM.iloc[x, 1]].reset_index(drop=True)
        BM = pd.concat([BM,nx],axis = 0)
        x +=1
BM.reset_index(drop=True, inplace=True)
print(BM)
BM.loc[-1] = [PN,PN,1]
BM.index = BM.index + 1
BM = BM.sort_index()
BM.columns = ['COMPONENT', 'MATERIAL', 'QTY']
# TOP LEVEL QTY ----------------------------------------
BM['TOP LEVEL QTY'] = BM[BM['COMPONENT']==PN]['QTY']
BM['TEMP']=BM.iloc[:,0] + " " + BM.iloc[:,1]
x = BM.where(BM['COMPONENT']==PN).last_valid_index() + 1
BM.iloc[:x-1,3] = BM.iloc[:x-1,2]
for k in range(x,len(BM.index)):
    y = sum(BM.iloc[:k+1,4]==BM.iloc[k,4])
    t = 0    
    for l in range(0,k):
        if BM.iloc[l,1] == BM.iloc[k,0]:
            t +=1    
            if t ==y:
                BM.iloc[k,3] = BM.iloc[l,3]*BM.iloc[k,2]
ws('COST').range("B2:D" + str(lr)).clear()
BM.insert(0,'TOP LEVEL PN',PN)
ws('COST').range('A1').options(index=False,header=True).value = BM.iloc[:,:5]