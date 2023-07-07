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
UCT_cn = sqlalchemy.create_engine(
    keys['con_str_uct_sg']) 

def load_to_db(x):
    if '.pkl' in x.lower():
        df = pd.read_pickle(x)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.columns = df.columns.str.replace("\n", "").str.strip()
        nm = os.path.basename(x).split('.')[0]
        df.to_sql(name=nm.lower(), con=UCT_cn, if_exists="replace", index=False)
        print("Uploaded", nm)
    else:
        for i in h5py.File(x).keys():
            df = pd.read_hdf(x, key=i)
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df.columns = df.columns.str.replace("\n", "").str.strip()
            nm = f'{os.path.basename(x).split(".")[0]}_{i}'
            df.to_sql(name=nm.lower(), con=UCT_cn, if_exists="replace", index=False)
            print("Uploaded", nm)
    UCT_cn.dispose()
    print('***ALL UPLOADS COMPLETE***')