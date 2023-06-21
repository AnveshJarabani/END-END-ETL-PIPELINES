import multiprocessing as mp
from datetime import datetime
from time import time
import dateutil.relativedelta as delt
import numpy as np
import pandas as pd
import xlwings as xl
import warnings
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
PH = pd.read_hdf('PH.H5',key='PH')
PH.rename(columns={'Material - Key':'PH'},inplace=True)
BOM = pd.read_hdf('ST_BM_BR.H5',key="BOM")
x=pd.read_pickle('OOR.PKL')
x['Delv Schedule line date']=pd.to_datetime(x['Delv Schedule line date'],format="%m/%d/%Y")
today=datetime.today().strftime('%m/%d/%Y')
END_DATE=(datetime.today()+delt.relativedelta(months=3)).strftime('%m/%d/%Y')
x=x[['Material','Material Description','Delv Schedule line date','Open SO quantity','Unit price']]
x.columns=['PN','DESC','DATE','QTY','PRICE']
x=x.loc[(x['DATE']>today)& (x['DATE']<END_DATE)]
x=x.pivot_table(index=['PN','DESC'],values=['QTY'],aggfunc=np.sum)
x.reset_index(inplace=True)
PNS = x[['PN']]
PNS.columns=['P/N']
PNS.drop_duplicates(inplace=True,ignore_index=True)
glob_start = time()
def func(PN):
    start=time()
    LVLBOMS = pd.DataFrame(columns=['TOPLEVEL','MATERIAL','COMP', 'QTY','TOP LVL QTY'])
    # BOM EXTRACT ----------------------------------------
    if (PH['PH']==PN).any():
        LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
        return LVLBOMS
    elif ~(BOM['MATERIAL']==PN).any():
        LVLBOMS.loc[len(LVLBOMS.index)] = [PN,PN,PN,1,1]
        return LVLBOMS
    else:
        BM = BOM[BOM['MATERIAL']==PN].reset_index(drop=True)
        x = 0
        while x <= (len(BM.index)-1) :
            if BM.iloc[x,1] in PH['PH'].values:
                x +=1
                continue
            nx = BOM[BOM['MATERIAL']==BM.iloc[x, 1]].reset_index(drop=True)
            BM = pd.concat([BM,nx],axis = 0)
            x +=1
        exp=time()
        EXPAND=round(exp-start,2)
    BM.reset_index(drop=True, inplace=True)
    BM.loc[-1] = [PN,PN,1]
    BM.index = BM.index + 1
    BM = BM.sort_index()
    count=str(len(BM))
    BM.columns = ['MATERIAL', 'COMP', 'QTY']
    # TOOL QTY ----------------------------------------
    BM['TOP LVL QTY'] = BM[BM['MATERIAL']==PN]['QTY']
    BM['TEMP']=BM.iloc[:,0] + " " + BM.iloc[:,1]
    x = BM.where(BM['MATERIAL']==PN).last_valid_index() + 1
    BM.iloc[:x-1,3] = BM.iloc[:x-1,2]
    for k in range(x,len(BM.index)):
        y = sum(BM.iloc[:k+1,4]==BM.iloc[k,4])
        t = 0    
        for l in range(0,k):
            if BM.iloc[l,1] == BM.iloc[k,0]:
                t +=1    
                if t ==y:
                    BM.iloc[k,3] = BM.iloc[l,3]*BM.iloc[k,2] 
    qty_time=round(time()-exp,2)
    BM.insert(0,'TOPLEVEL',PN)
    BM = BM.iloc[:,:5]
    LVLBOMS = pd.concat([LVLBOMS,BM],ignore_index=True)
    print(PN+' - '+str(round(time()-start,1))+'Secs - ITEMS#:'+count+' ELAPSED:'+str(round((time()-glob_start)/60,2))+'Mins'+' EXPAND:'+str(EXPAND)+' QTY_ADD:'+str(qty_time))
    return LVLBOMS
if __name__=='__main__':
    pool1=mp.Pool(processes=mp.cpu_count()*3)
    new_rows=pool1.map(func,list(PNS['P/N'].unique()))
    test=pd.concat(new_rows)
    test=test.loc[~test['COMP'].str.endswith('-UCT',na=False)]
    test.to_pickle('NPVECT2.PKL')
    print(round((time()-glob_start)/60,1))
