import pandas as pd

rout_path='../../Routings with WC 09.13.23.csv'

rout=pd.read_csv(rout_path)
rout=rout[['Plnt','Material','OpAc','StTextKy','Base Quantity','Un','StdVal.1','Unit.2','StdVal.2','Unit.3','Work Center']]
rout.columns=['PLANT','MATERIAL','OP_NUMBER','WORK_CENTER','STD_KEY','BASE_QUANTITY','UNIT','SETUP','SETUP_UNIT','RUN','RUN_UNIT']
rout=rout.loc[rout['PLANT'].notna()]
convert_cols=['PLANT','OP_NUMBER','BASE_QUANTITY','SETUP','RUN']
rout[convert_cols]=rout[convert_cols].applymap(lambda x: str(x).replace(',',''))
rout[convert_cols]=rout[convert_cols].applymap(lambda x: float(x))
rout.to_hdf('../H5/ST_BM_BR.H5','ROUT')