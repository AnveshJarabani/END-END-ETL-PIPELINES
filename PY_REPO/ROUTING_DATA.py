import pandas as pd

import xlwings as xl
rout_path='../../Routing Extract 3321 3322- Anvesh.csv'

rout=pd.read_csv(rout_path)
rout=rout[['Plnt','Material','OpAc','StTextKy','Base Quantity','Un','StdVal.1','Unit.2','StdVal.2','Unit.3']]
rout.columns=['PLANT','MATERIAL','OPERATION','ST_KEY','BASE_QUANTITY','UNIT','SETUP','SETUP_UNIT','RUN','RUN_UNIT']
rout=rout.loc[rout['PLANT'].notna()]
rout[['PLANT','OPERATION']]=rout[['PLANT','OPERATION']].applymap(lambda x: int(x))

...


old_rout=pd.read_hdf('../H5/ST_BM_BR.H5',key='ROUT')
old_rout.columns