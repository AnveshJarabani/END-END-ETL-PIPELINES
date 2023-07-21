import sqlalchemy
from sqlalchemy import inspect
import pandas as pd
import h5py
import os
import json
import numpy as np
import datetime
keys= json.load(open("../PRIVATE/encrypt.json", "r"))

# ! UCT DATA SCHEMA CONNECTION
LOCAL_PG_CN = sqlalchemy.create_engine(
    keys['con_str_uct_pg']) 


today = datetime.date.today()

pkl_files = [f"../PKL/{f}" for f in os.listdir("../PKL/")]
h5_files = [f"../H5/{f}" for f in os.listdir("../H5/")]
# pkl_files = [i  for i in pkl_files  if datetime.date.fromtimestamp(os.path.getmtime(i)) == today]
# h5_files = [i for i in h5_files if datetime.date.fromtimestamp(os.path.getmtime(i)) == today]

for x in pkl_files:
    df = pd.read_pickle(x)
    if isinstance(df, dict):
        continue
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.columns = df.columns.str.replace("\n", "").str.strip()
    nm = os.path.basename(x).split('.')[0]
    df.to_sql(name=nm.lower(), con=LOCAL_PG_CN, if_exists="replace", index=False)
    print("Uploaded", nm)


for x in h5_files:
    for i in h5py.File(x).keys():
        df = pd.read_hdf(x, key=i)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.columns = df.columns.str.replace("\n", "").str.strip()
        nm = f'{os.path.basename(x).split(".")[0]}_{i}'
        df.to_sql(name=nm.lower(), con=LOCAL_PG_CN, if_exists="replace", index=False)
        print("Uploaded", nm)
print('________ALL FILES UPLOADED TO LOCAL PG_SQL DB________')
LOCAL_PG_CN.dispose()