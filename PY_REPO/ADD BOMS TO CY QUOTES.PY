import pandas as pd
import xlwings as xl
# X=xl.books.active.sheets.active.range('A1:I1527').options(index=False).options(pd.DataFrame,index=False).value

# QUOTES=pd.read_pickle('CY-HPARTS.PKL')

# CAT=QUOTES[['TOP LEVEL']].drop_duplicates(ignore_index=True)
# QUOTES=QUOTES.loc[QUOTES['TOP LEVEL']!='CY-213633']
# QUOTES=pd.concat([QUOTES,X],ignore_index=True)
# CAT=CAT.reset_index().set_index('TOP LEVEL')
# QUOTES['SORTER']=QUOTES['TOP LEVEL'].map(CAT['index'])
# QUOTES=QUOTES.sort_values('SORTER')
# QUOTES=QUOTES.drop(columns=['SORTER'])
# QUOTES['QTY EXT']=QUOTES['QTY EXT'].astype(float)
# QUOTES.to_hdf('QUOTES.H5',key='CY')
# x=pd.DataFrame()
# ct=xl.books.active.sheets.count
# for i in range(4,ct+1):
#     r=xl.books.active.sheets(i).range('A1').end('down').row
#     dt=xl.books.active.sheets(i).range('A1:M'+str(r)).options(index=False).options(pd.DataFrame,index=False).value
#     x=pd.concat([x,dt],ignore_index=True)
x=pd.read_hdf('QUOTES.H5',key='CY')
def updateprice(NEWPN,NEWPRICE):
    # x.loc[x['P/N']==OLDPN,'P/N']=NEWPN
    x.loc[x['P/N']==NEWPN,'NEW COST EA']=NEWPRICE
    # x.loc[x['P/N']==NEWPN,'LAST VENDOR']=VENDOR
    # x.loc[x['P/N']==NEWPN,'MAKE/BUY']='BUY'
    # x.loc[x['P/N']==NEWPN,'TYPE']='CAT'
    x.loc[x['P/N']==NEWPN,'NEW COST EXT']=NEWPRICE*x['QTY EXT']
    x['OLD COST EXT']=x['OLD COST EXT'].astype(float)
    x['NEW COST EXT']=x['NEW COST EXT'].astype(float)
    x.loc[x['P/N']==NEWPN,'DELTA']=x['OLD COST EXT']-x['NEW COST EXT']
updateprice('CY-101140',3560)
x.to_hdf('QUOTES.H5',key='CY')