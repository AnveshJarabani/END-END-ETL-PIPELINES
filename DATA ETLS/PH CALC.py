import pandas as pd
import numpy as np
from time import time
import os,warnings
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
import multiprocessing as mp
def remove_outliers(group):
    q1 = group['ACT_MAT_COST'].quantile(0.25)
    q3 = group['ACT_MAT_COST'].quantile(0.75)
    iqr = q3 - q1
    return group[(group['ACT_MAT_COST'] >= q1 - 1.5*iqr) & (group['ACT_MAT_COST'] <= q3 + 1.5*iqr)]
if __name__=='__main__':
    # ---------------QUARTERLY TRENDS FOR CHARTS ---------------------
    PH_DATA=pd.read_pickle("../PKL/PH.PKL")
    PH_DATA['YR']=PH_DATA['QTR_YR'].str[-4:].astype(int)
    PH_DATA['QTR']=PH_DATA['QTR_YR'].str[1:2].astype(int)
    PH_DATA=PH_DATA.sort_values(by=['YR','QTR'])
    PH_DATA.drop_duplicates(ignore_index=True,inplace=True)
    PH=PH_DATA[['QTR_YR','PART_NUMBER','ACT_MAT_COST']]
    FR = pd.read_hdf('../H5/ST_BM_BR.H5',key="FRAMES")
    def removeframes(X):
                    Y = X.merge(FR,left_on=X.columns[0],right_on='PART NUMBER',how='left')
                    Y = Y.loc[Y['PART NUMBER'].isna()]
                    Y = Y.iloc[:,:3]
                    return Y
    PH=removeframes(PH)
    PH.columns=['Q+YR','PN','BUY COST']
    PH=PH.loc[PH.iloc[:,1].notna()].reset_index(drop=True)
    PH['LAST Q COST'] = PH.groupby('PN')['BUY COST'].shift(-1)
    PH['DELTA %']=(PH['BUY COST']-PH['LAST Q COST'])/PH['LAST Q COST']
    PH[['BUY COST','DELTA %']]=PH[['BUY COST','DELTA %']].round(2)
    PH['DELTA %'].replace(np.nan,0,inplace=True)
    PH.dropna(how='all',inplace=True)
    PH.to_hdf('../H5/PH.H5',key='TREND',mode='w') # DONT PUT BREAKPOINTS ON THIS CODE! PH KEYS WILL BE LOST!
    print('PH.H5 TREND COMPLETE')
    #------------------PURCHASE HISTORY PH FOR CALCULATIONS -------------------
    PH=PH_DATA.loc[PH_DATA['QTR_YR'].isin(list(PH_DATA['QTR_YR'].unique())[-5:])]
    PH=PH[['PART_NUMBER','ACT_MAT_COST']]
    PH.columns = ["PART_NUMBER",'ACT_MAT_COST']
    PH_MATERIALGROUP=PH.groupby("PART_NUMBER")
    pool=mp.Pool(processes=mp.cpu_count())
    result=pool.map(remove_outliers,[df for _,df in PH_MATERIALGROUP])
    PH=pd.concat(result).reset_index(drop=True)
    PH=PH.pivot_table(index=["PART_NUMBER"],values=['ACT_MAT_COST'],aggfunc=np.average)
    PH.reset_index(inplace=True)
    MERCURY_PART=pd.read_hdf('../H5/CY_ADJ.H5',key='MERCURY')
    MERCURY_PART.columns=['PART NUMBER']
    FR=pd.concat([FR,MERCURY_PART])
    def removeframes(X):
                    X.columns = ["PART_NUMBER",'ACT_MAT_COST']
                    Y = X.merge(FR,left_on="PART_NUMBER",right_on='PART NUMBER',how='left')
                    Y = Y.loc[Y['PART NUMBER'].isna()]
                    Y = Y.loc[:,["PART_NUMBER",'ACT_MAT_COST']]
                    return Y
    PH=removeframes(PH)
    PH.loc[PH["PART_NUMBER"]=='CY-198172','ACT_MAT_COST']=18634.5
    PH.to_hdf('../H5/PH.H5',key="FOR_PLUGINS",mode='a')
    print('LBR.H5 PH COMPLETE')
    #------------------------VENDOR DETAILS ------------
    PH_DATA['YR']=PH_DATA['QTR_YR'].str[-4:].astype(int)
    PH_DATA['QTR']=PH_DATA['QTR_YR'].str[1:2].astype(int)
    PH_DATA=PH_DATA.sort_values(by=['YR','QTR'],ascending=False)
    PH=PH_DATA[['PART_NUMBER','ACT_MAT_COST']]
    PH.drop_duplicates(subset=['PART_NUMBER'],ignore_index=True,inplace=True)
    def removeframes(X):
                    X.columns = ['PART_NUMBER','LAST_VENDOR']
                    Y = X.merge(FR,left_on='PART_NUMBER',right_on='PART NUMBER',how='left')
                    Y = Y.loc[Y['PART NUMBER'].isna()]
                    Y = Y.loc[:,['PART_NUMBER','LAST_VENDOR']]
                    return Y
    PH=removeframes(PH)
    PH.to_hdf('../H5/PH.H5',key='LAST_VENDOR',mode='a')
    print('LBR.H5 LST_VENDOR COMPLETE')