import sqlalchemy
from sqlalchemy import inspect
import pandas as pd
import h5py
import os
import json
import numpy as np
import datetime
from paramiko import SSHClient,AutoAddPolicy
from sshtunnel import SSHTunnelForwarder

keys = json.load(open("../PRIVATE/encrypt.json", "r"))

ssh_host = keys["pyanywhere_ssh_host"]  # SSH server address
ssh_port = keys["pyanywhere_ssh_port"]  # SSH server port
ssh_username = keys["pyanywhere_ssh_username"]  # SSH username
ssh_password = keys['pyanywhere_ssh_password']  # SSH password
# Database configuration
pyanywhere_db_host = keys['pyanywhere_db_host' ] # Database server address (accessible through SSH tunnel)
pyanywhere_db_port =keys['pyanywhere_db_port']  # ]Database server port
pyanywhere_db_username = keys['pyanywhere_db_username']  # Database usernamkeyse
pyanywhere_db_password = keys['pyanywhere_db_password']  # Database password
pyanywhere_db_name = keys['pyanywhere_db_database']  # Database name

# Create an SSH client
ssh_client = SSHClient()
ssh_client.load_system_host_keys()
ssh_client.set_missing_host_key_policy(AutoAddPolicy())

# Connect to the SSH server
ssh_client.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)

# Create an SSH tunnel
server = SSHTunnelForwarder(
    ssh_address_or_host=(ssh_host, ssh_port),
    ssh_username=ssh_username,
    ssh_password=ssh_password,
    remote_bind_address=(pyanywhere_db_host, pyanywhere_db_port)
)
server.start()

pyanywhere_connection_string = f"mysql+pymysql://{pyanywhere_db_username}:{pyanywhere_db_password}@localhost:{server.local_bind_port}/{pyanywhere_db_name}"

pyanywhere_cn = sqlalchemy.create_engine(pyanywhere_connection_string)
pyanywhere_cn.connect()


today = datetime.date.today()

pkl_files = [f"../PKL/{f}" for f in os.listdir("../PKL/")]
h5_files = [f"../H5/{f}" for f in os.listdir("../H5/")]
tables=pyanywhere_cn.table_names()
#!! CAUTION -- THIS DROPS TABLES --------------------------------
for table in tables:
    pyanywhere_cn.execute(f'DROP TABLE `{table}`')

# pkl_files = [i for i in pkl_files if datetime.date.fromtimestamp(os.path.getmtime(i)) == today]
# h5_files = [i for i in h5_files if datetime.date.fromtimestamp(os.path.getmtime(i)) == today]


for x in pkl_files:
    df = pd.read_pickle(x)
    if isinstance(df, dict):
        continue
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.columns = df.columns.str.replace("\n", "").str.strip()
    nm = os.path.basename(x).split(".")[0]
    df.to_sql(name=nm.lower(), con=pyanywhere_cn, if_exists="replace", index=False)
    print("Uploaded", nm)

for x in h5_files:
    for i in h5py.File(x).keys():
        df = pd.read_hdf(x, key=i)
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.columns = df.columns.str.replace("\n", "").str.strip()
        nm = f'{os.path.basename(x).split(".")[0]}_{i}'
        df.to_sql(name=nm.lower(), con=pyanywhere_cn, if_exists="replace", index=False)
        print("Uploaded", nm)
print('________ALL FILES UPLOADED TO PYTHONANYWHERE SQL DB________')
pyanywhere_cn.dispose()
server.stop()
ssh_client.close()
