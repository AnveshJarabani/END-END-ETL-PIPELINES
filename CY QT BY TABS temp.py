# ----------------------- UPDATE FILE SAVE NAME FIRST ---------------------
import warnings,time,subprocess,win32com.client
import pandas as pd
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
pd.options.mode.chained_assignment=None
subprocess.call(['taskkill','/f','/im','EXCEL.EXE'])
import xlwings as xl
# x=xl.books.active.sheets.count
# ten=[]
# for i in range(4,x+1):
#       q=xl.books.active.sheets(i).name
#       ten.append(q)
#     ten=xl.books.active.sheets(i).range('A1').expand().options(pd.DataFrame,index=False).value
#     yt=pd.concat([yt,ten],ignore_index=True)
from decimal import Decimal
start_time=time.time()
yt = pd.read_hdf('CY_ADJ.H5',key='YT')
TYPE=pd.read_hdf('CY_ADJ.H5',key='OLD-NEW TYPES')
typ=pd.DataFrame(columns=['TYP'])
typ['TYP']=TYPE['TYPE'].unique()
TOOLS=yt['TOP LEVEL'].unique()
typ.reset_index(inplace=True,drop=True)
yt.loc[yt['TYPE']=='BTP AFRM','MAKE/BUY']='BUY'
yt[['NEW COST EA','NEW COST EXT']]=yt[['NEW COST EA','NEW COST EXT']].applymap(lambda x:float(x) if isinstance(x,Decimal) else x)
xt=pd.read_hdf('CY_ADJ.H5',key='2021 TOTALS')
macro_book=xl.Book(r"MACRO.XLSM")
book=xl.Book()
xw=win32com.client.Dispatch("Excel.Application") 
for i in TOOLS:  
    book.sheets.add(name=i,before='Sheet1')
book.sheets('Sheet1').delete()
for i in TOOLS:  
    sht=book.sheets(i)
    df=yt.loc[yt['TOP LEVEL']==i]
    df.sort_values(by=['DELTA'],inplace=True)
    x=len(df)+1
    sht.range('A1').options(index=False).value=df
    if i=='CY-210257':
        sht.range('A1:M1').font.bold=True
        sht.range('F1:G' + str(x)).color = (162, 217, 242)
        sht.range('H1:I' + str(x)).color = (214, 174, 242)
        sht.range('A1:M1').color = (235, 208, 136)
        book.sheets(i).range("D" + str(x+16)).options(index=False,header=False).value=typ
        LIST1=['UCT FAB','MATERIAL COST','BURDEN 6.5%','SG&A 5%','PROFIT 8%','LABOR','H-PARTS','H-PARTS MARKUP','CRATE+MARGIN','TOTAL SELL:']
        book.sheets(i).range('D'+str(x+4)).options(transpose=True,index=False,columns=False).value=LIST1
    xr=xt.loc[(xt['TOOL'] ==i),'COST EXT'] 
    sht.range('G'+str(x+4)).options(index=False,header=False).value=xr
    try:
       sht.range('G'+str(x+12)).value=df.loc[df['P/N'].str.contains('Crate Sell Price',na=False),'OLD COST EXT'].reset_index().iloc[0,1]
    except:
        sht.range('G'+str(x+12)).value=0
book.sheets.add(name='XL SUMMARY',before=1)
book.sheets.add(name='7X SUMMARY',after=1)
book.sheets.add(name='SPARES SUMMARY',after=2)
book.sheets('XL SUMMARY').range('A1:XFD1048576').color = (255, 255, 255)
book.sheets('7X SUMMARY').range('A1:XFD1048576').color = (255, 255, 255)
book.sheets('SPARES SUMMARY').range('A1:XFD1048576').color = (255, 255, 255)
xw.Application.Run("MACRO.XLSM!Module1.calc") 
print("File built in "+str(round((time.time()-start_time),2))+" Seconds")
macro_book.close()
del xl
book.save(r"C:\Users\ajarabani\Downloads\UCT Q4’22 Cymer Product Pricing 10.12.xlsx")