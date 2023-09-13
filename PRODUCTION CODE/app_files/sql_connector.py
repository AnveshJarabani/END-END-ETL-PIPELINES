import sqlalchemy
from sqlalchemy import inspect
import pandas as pd
import json
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

def table(name):
    query=f"SELECT * FROM {name.lower()}"
    return pd.read_sql(query,pyanywhere_cn)
def query_table(query):
    return pd.read_sql(query,pyanywhere_cn)