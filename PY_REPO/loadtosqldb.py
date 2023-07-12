import sqlalchemy
from sqlalchemy import inspect
import pandas as pd
import h5py
import os
import json
import numpy as np
import datetime

keys = json.load(open("../PRIVATE/encrypt.json", "r"))


con_str_uct = "mysql+pymysql://anveshj:Zintak1!@ANVESHJ.mysql.pythonanywhere-services.com:3306/ANVESHJ$uct_data"
cn = sqlalchemy.create_engine(con_str_uct)
cn.connect()


# ! UCT DATA SCHEMA CONNECTION
UCT_cn = sqlalchemy.create_engine(
    keys["con_str_uct"],
    connect_args={"ssl_ca": keys["ssl_ca"]},
)


today = datetime.date.today()

pkl_files = [f"../PKL/{f}" for f in os.listdir("../PKL/")]
pkl_files = [
    i for i in pkl_files if datetime.date.fromtimestamp(os.path.getmtime(i)) == today
]
h5_files = [f"../H5/{f}" for f in os.listdir("../H5/")]
h5_files = [
    i for i in h5_files if datetime.date.fromtimestamp(os.path.getmtime(i)) == today
]


for x in pkl_files:
    df = pd.read_pickle(x)
    if isinstance(df, dict):
        continue
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.columns = df.columns.str.replace("\n", "").str.strip()
    nm = os.path.basename(x).split(".")[0]
    df.to_sql(name=nm.lower(), con=UCT_cn, if_exists="replace", index=False)
    print("Uploaded", nm)

for x in h5_files:
    for i in h5py.File(x).keys():
        df = pd.read_hdf(x, key=i)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.columns = df.columns.str.replace("\n", "").str.strip()
        nm = f'{os.path.basename(x).split(".")[0]}_{i}'
        df.to_sql(name=nm.lower(), con=UCT_cn, if_exists="replace", index=False)
        print("Uploaded", nm)
UCT_cn.dispose()


# ! LEETCODE DATA SCHEMA CONNECTION
# leet_cn = sqlalchemy.create_engine(
#     keys['con_str_leetcode'],
#     connect_args={"ssl_ca": keys['ssl_ca']},
# )
# learn_folder = r"C:\Users\anves\Downloads\Olympics_data"
# csv_files = [
#     f for f in os.listdir(learn_folder) if re.search(r"\.csv$", f, flags=re.IGNORECASE)
# ]
# for x in csv_files:
#     df = pd.read_csv(os.path.join(learn_folder, x))
#     df.columns = df.columns.str.replace("\n", "").str.strip()
#     nm = x[: x.index(".")]
#     df.to_sql(name=nm, con=lt_cn, if_exists="replace", index=False)
#     print("uploaded", x)

# inspector=inspect(cn)
# tables=inspector.get_table_names()
# for table in tables:
#     if '.' in table:
#         cn.execute(f"DROP TABLE IF EXISTS `{table}`")C:\UCT-CORP-ePDM\(101)-uct\2-workspace\06-manufacturing\02-uct-cad\users\AJarabani
