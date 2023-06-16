import sqlalchemy
from sqlalchemy import inspect
import pandas as pd
import h5py
import os
import re
import numpy as np
import datetime
# ! UCT DATA SCHEMA CONNECTION
cn = sqlalchemy.create_engine('mysql+pymysql://anveshjarabani:Zintak1!@mysql12--2.mysql.database.azure.com:3306/uct_data',
                              connect_args={'ssl_ca': 'DigiCertGlobalRootCA.crt.pem'})
# ! LEETCODE DATA SCHEMA CONNECTION
lt_cn = sqlalchemy.create_engine('mysql+pymysql://anveshjarabani:Zintak1!@mysql12--2.mysql.database.azure.com:3306/leetcode',
                                 connect_args={'ssl_ca': 'DigiCertGlobalRootCA.crt.pem'})

today = datetime.date.today()


learn_folder = r'C:\Users\ajarabani\Downloads\Dataset_n_Scripts'
csv_files = [f for f in os.listdir(learn_folder) if re.search(
    r'\.csv$', f, flags=re.IGNORECASE)]
for x in csv_files:
    df = pd.read_csv(os.path.join(learn_folder, x))
    df.columns = df.columns.str.replace('\n', '').str.strip()
    nm = x[:x.index('.')]
    df.to_sql(name=nm, con=lt_cn, if_exists='replace', index=False)
    print('uploaded', x)


folder = r'C:\Users\ajarabani\Downloads\PYTHON'
pkl_files = [f for f in os.listdir(r'C:\Users\ajarabani\Downloads\PYTHON') if re.search(
    r'\.pkl$', f, flags=re.IGNORECASE)]
pkl_files = [i for i in pkl_files if datetime.date.fromtimestamp(
             os.path.getmtime(os.path.join(folder, i))) == today]
h5_files = [f for f in os.listdir(
    r'C:\Users\ajarabani\Downloads\PYTHON') if f.endswith('5')]
h5_files = [i for i in h5_files if datetime.date.fromtimestamp(
    os.path.getmtime(os.path.join(folder, i))) == today]
table_list = cn.table_names()
# for n in table_list:
#     print(n)

for x in pkl_files:
    df = pd.read_pickle(x)
    if isinstance(df, dict):
        continue
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.columns = df.columns.str.replace('\n', '').str.strip()
    nm = x[:x.index('.')]
    df.to_sql(name=nm.lower(), con=cn, if_exists='replace', index=False)
    print('Uploaded', nm)

for x in h5_files:
    for i in h5py.File(x).keys():
        df = pd.read_hdf(x, key=i)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.columns = df.columns.str.replace('\n', '').str.strip()
        nm = f'{x.split(".")[0]}_{i}'
        df.to_sql(name=nm.lower(), con=cn, if_exists='replace', index=False)
        print('Uploaded', nm)

cn.dispose()


# inspector=inspect(cn)
# tables=inspector.get_table_names()
# for table in tables:
#     if '.' in table:
#         cn.execute(f"DROP TABLE IF EXISTS `{table}`")C:\UCT-CORP-ePDM\(101)-uct\2-workspace\06-manufacturing\02-uct-cad\users\AJarabani
