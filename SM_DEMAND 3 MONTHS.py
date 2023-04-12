import xlwings as xl
from datetime import datetime
from time import time
import dateutil.relativedelta as delt
import numpy as np
import pandas as pd
import warnings,pickle,os,subprocess
from bigtree import tree_to_dataframe,print_tree
import multiprocessing as mp
warnings.simplefilter(action='ignore', category=(FutureWarning,UserWarning))
os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
PH = pd.read_hdf('PH.H5',key='PH')
PH.rename(columns={'Material - Key':'PH'},inplace=True)
OOR=pd.read_pickle('OOR.PKL')
today=datetime.today().strftime('%m/%d/%Y')
END_DATE=(datetime.today()+delt.relativedelta(months=3)).strftime('%m/%d/%Y')
OOR=OOR[['Material','Material Description','Delv Schedule line date','Open SO quantity','Unit price']]
OOR.columns=['TOOL','DESC','DATE','DEMAND_QTY','PRICE']
OOR=OOR.loc[(OOR['DATE']>today)& (OOR['DATE']<END_DATE)]
OOR=OOR.pivot_table(index=['TOOL','DESC'],values=['DEMAND_QTY'],aggfunc=np.sum)
OOR.reset_index(inplace=True)
OOR=OOR[OOR['DEMAND_QTY']!=0]
PNS = OOR[['TOOL']]
glob_time=time()
List=list(PNS['TOOL'].astype(str).unique())
string=' '.join(map(str,List))
str_bytes=string.encode('utf-8')
result=subprocess.check_output(['python','trees_to_df.py'],input=str_bytes)
BOM_DF=pickle.loads(result)
print(time()-glob_time)
BOM_DF=BOM_DF[['TOPLEVEL','PN','PARENT','QTY','TQ']]
TEMP=BOM_DF[['PN','PARENT']].drop_duplicates()
TEMP.columns=['RAW MATERIAL','PARENT']
BOM_DF=BOM_DF.merge(OOR,left_on='TOPLEVEL',right_on='TOOL',how='left')
BOM_DF['DEMAND FORECAST']=BOM_DF['DEMAND_QTY']*BOM_DF['TQ']
DEMAND=BOM_DF.pivot_table(index=['PN'],values=['DEMAND FORECAST'],aggfunc=np.sum)
DEMAND.reset_index(inplace=True)
DEMAND.columns=['KEY','DEMAND FORECAST']
SM_DEMAND=DEMAND.merge(TEMP,left_on=['KEY'],right_on=['PARENT'],how='left')
SM_DEMAND=SM_DEMAND[['RAW MATERIAL','PARENT','DEMAND FORECAST']]
SM_DEMAND=SM_DEMAND.dropna(how='any')
SM_DEMAND['DEMAND FORECAST']=SM_DEMAND['DEMAND FORECAST'].astype(int)
SM_DEMAND=SM_DEMAND.sort_values('DEMAND FORECAST',ascending=False)
SM_DEMAND.to_pickle('SM_DEMAND_FORECAST.PKL')
print('SM_DEMAND_FORECAST.PKL COMPLETE')