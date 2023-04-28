import sqlalchemy
import pandas as pd
import h5py,os,re
import numpy as np
cn=sqlalchemy.create_engine('mysql+pymysql://anveshjarabani:Zintak1!@mysql12--2.mysql.database.azure.com:3306/uct_data',
                            connect_args={'ssl_ca':'DigiCertGlobalRootCA.crt.pem'})

pkl_files=[f for f in os.listdir(r'C:\Users\ajarabani\Downloads\PYTHON') if re.search(r'\.pkl$', f, flags=re.IGNORECASE)]
# h5_files=[f for f in os.listdir(r'C:\Users\ajarabani\Downloads\PYTHON') if f.endswith('5')]

table_list=cn.table_names()
for n in table_list:
    print(n)

for x in pkl_files:
    df=pd.read_pickle(x)
    if isinstance(df,dict):
        continue
    df.replace([np.inf,-np.inf],np.nan,inplace=True)
    df.columns = df.columns.str.replace('\n', '').str.strip()
    nm=x[:x.index('.')]
    df.to_sql(name=nm.lower(),con=cn,if_exists='replace',index=False)
    print('Uploaded',nm)

# for n in table_list:
#     with cn.connect() as con:
#         con.execute(f"DROP TABLE IF EXISTS `{n}`")
#         print('table dropped',n)
# for x in h5_files:
#     for i in h5py.File(x).keys():
#         df=pd.read_hdf(x,key=i)
#         df.replace([np.inf,-np.inf],np.nan,inplace=True)
#         df.columns = df.columns.str.replace('\n', '').str.strip()
#         nm=x[:x.index('.')]+'_'+i
#         df.to_sql(name=nm.lower(),con=cn,if_exists='replace',index=False)
#         print('Uploaded',nm)

cn.dispose()
